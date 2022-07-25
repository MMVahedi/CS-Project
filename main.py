import random
import simpy


class Service:
    All_resources = [None for _ in range(7)]
    Queues = [[] for _ in range(7)]
    Queues_time_sum = [0 for _ in range(7)]
    Servers_busy_times = [0 for _ in range(7)]
    In_progress_requests = [[] for _ in range(7)]

    def __init__(self, service_type):
        self.type = service_type
        if self.type == "mobile portal service":
            self.id = 0
            self.mean = 1.0 / 2
        elif self.type == "order management service":
            self.id = 1
            self.mean = 1.0 / 6
        elif self.type == "payment service":
            self.id = 2
            self.mean = 1.0 / 12
        elif self.type == "web portal service":
            self.id = 3
            self.mean = 1.0 / 3
        elif self.type == "customers management service":
            self.id = 4
            self.mean = 1.0 / 5
        elif self.type == "delivery communication":
            self.id = 5
            self.mean = 1.0 / 9
        elif self.type == "restaurant management service":
            self.id = 6
            self.mean = 1.0 / 8

    def add_customer_to_queue(self, request):
        Service.Queues[self.id].append(request)

    def remove_customer_from_queue(self, index):
        Service.Queues[self.id].pop(index)

    def add_time_to_queue_time_sum(self, time):
        Service.Queues_time_sum[self.id] += time

    def get_resources(self):
        return Service.All_resources[self.id]

    def add_busy_time(self, time):
        Service.Servers_busy_times[self.id] += time

    def get_queue(self):
        return Service.Queues[self.id]

    def add_in_progress_request(self, request, time):
        Service.In_progress_requests[self.id].append([request, time])

    def remove_in_progress_requests(self, request):
        lst = Service.In_progress_requests[self.id]
        for i in range(len(lst)):
            if lst[i][0].id == request.id:
                lst.pop(i)
                break


class Request:
    id = 0
    waiting_times = [0] * 7
    number_of_received_requests = [0] * 7

    def __init__(self, request_type):
        Request.id += 1
        self.enter_queue_time = 0
        self.exit_queue_time = 0
        self.id = Request.id
        self.priority = 0
        self.type = request_type
        Request.number_of_received_requests[self.type - 1] += 1
        self.processes = []
        self.turn = -1
        if request_type == 1:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("order management service"))
            self.processes.append(Service("payment service"))
            self.priority = 1
        elif request_type == 2:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("order management service"))
            self.processes.append(Service("payment service"))
            self.priority = 1
        elif request_type == 3:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("customers management service"))
            self.processes.append(Service("delivery communication"))
            self.priority = 2
        elif request_type == 4:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("restaurant management service"))
            self.priority = 2
        elif request_type == 5:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("restaurant management service"))
            self.priority = 2
        elif request_type == 6:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("restaurant management service"))
            self.processes.append(Service("delivery communication"))
            self.priority = 1
        elif request_type == 7:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("order management service"))
            self.priority = 2

    def current_process(self):
        return self.processes[self.turn]

    def next_process(self):
        self.turn += 1

    def add_waiting_time(self, time):
        Request.waiting_times[self.type - 1] += time


def check_error(service_type):
    p = 0
    if service_type == "mobile portal service":
        p = 0.01
    elif service_type == "order management service":
        p = 0.03
    elif service_type == "payment service":
        p = 0.2
    elif service_type == "web portal service":
        p = 0.01
    elif service_type == "customers management service":
        p = 0.02
    elif service_type == "delivery communication":
        p = 0.1
    elif service_type == "restaurant management service":
        p = 0.02

    return p >= random.random()


def request_generator(rate):
    global env
    while True:
        request_type = random.random()
        if request_type < 0.2:
            request = Request(1)
        elif request_type < 0.3:
            request = Request(2)
        elif request_type < 0.35:
            request = Request(3)
        elif request_type < 0.60:
            request = Request(4)
        elif request_type < 0.75:
            request = Request(5)
        elif request_type < 0.95:
            request = Request(6)
        else:
            request = Request(7)

        request.next_process()
        env.process(general_service(request))
        t = random.expovariate(1.0 / rate)
        yield env.timeout(t)


def general_service(request):
    global env
    service = request.current_process()
    service.add_customer_to_queue(request)
    request.enter_queue_time = env.now
    # print(service.type, "time_entered_queue: ", request.enter_queue_time, request.id)
    with service.get_resources().request() as req:
        yield req
        service_queue = service.get_queue()
        preferred_index = find_preferred_request(service_queue)
        request = service_queue[preferred_index]
        # if len(service_queue) > 0:
        request.exit_queue_time = env.now
        service_start_time = env.now
        service.remove_customer_from_queue(preferred_index)
        service.add_in_progress_request(request, env.now)
        # print(service.type, "time_left_queue: ", request.exit_queue_time, request.id)
        time_in_queue = request.exit_queue_time - request.enter_queue_time
        request.add_waiting_time(time_in_queue)
        service.add_time_to_queue_time_sum(time_in_queue)
        if len(request.processes) > request.turn + 1:
            request.next_process()
            yield env.process(general_service(request))
            request.turn -= 1
        service_time = random.expovariate(service.mean)
        # print(service.type, "service time: ", service_time)
        yield env.timeout(service_time)
        service.add_busy_time(env.now - service_start_time)
        service.remove_in_progress_requests(request)
        # print(service.type, "service finished in", env.now)


def find_preferred_request(queue):
    try:
        preferred_request = queue[0]
        index = 0
        for i in range(1, len(queue)):
            request = queue[i]
            if request.priority < preferred_request.priority:
                preferred_request = request
                index = i
        return index
    except:
        print("Error occurred in find prefer request function!")
        return 0


env = simpy.Environment()

number_of_resources = list(map(int, input().split()))

Service.All_resources[6] = simpy.Resource(env, capacity=number_of_resources[0])
Service.All_resources[4] = simpy.Resource(env, capacity=number_of_resources[1])
Service.All_resources[1] = simpy.Resource(env, capacity=number_of_resources[2])
Service.All_resources[5] = simpy.Resource(env, capacity=number_of_resources[3])
Service.All_resources[2] = simpy.Resource(env, capacity=number_of_resources[4])
Service.All_resources[0] = simpy.Resource(env, capacity=number_of_resources[5])
Service.All_resources[3] = simpy.Resource(env, capacity=number_of_resources[6])

rate = int(input())
simulation_time = int(input())
simulation_time = 1000  # TODO: remove me

maximum_waiting_times = list(map(int, input().split()))

env.process(request_generator(1 / rate))
env.run(until=simulation_time)

for i in range(len(Service.Queues)):
    for request in Service.Queues[i]:
        time_in_queue = simulation_time - request.enter_queue_time
        request.add_waiting_time(time_in_queue)
        request.current_process().add_time_to_queue_time_sum(time_in_queue)

print('-' * 50)
print("Queue length mean for each service:")
print("     Mobile portal service:", Service.Queues_time_sum[0] / simulation_time)
print("     Order management service:", Service.Queues_time_sum[1] / simulation_time)
print("     Payment service:", Service.Queues_time_sum[2] / simulation_time)
print("     Web portal service:", Service.Queues_time_sum[3] / simulation_time)
print("     Customers management service:", Service.Queues_time_sum[4] / simulation_time)
print("     Delivery communication:", Service.Queues_time_sum[5] / simulation_time)
print("     Restaurant management service:", Service.Queues_time_sum[6] / simulation_time)
print('-' * 50)

for i in range(7):
    if Request.number_of_received_requests[i] == 0:
        Request.number_of_received_requests[i] = 1e-9

print('-' * 50)
print('Waiting time in queue mean:', sum(Request.waiting_times) / sum(Request.number_of_received_requests))
print("Waiting time in queue mean for each request:")
print("     Place order through mobile phone:",
      Request.waiting_times[0] / Request.number_of_received_requests[0])
print("     Place order through the web:",
      Request.waiting_times[1] / Request.number_of_received_requests[1])
print("     Send a message to the courier:",
      Request.waiting_times[2] / Request.number_of_received_requests[2])
print("     See restaurant information via mobile:",
      Request.waiting_times[3] / Request.number_of_received_requests[3])
print("     View restaurant information through the web:",
      Request.waiting_times[4] / Request.number_of_received_requests[4])
print("     Courier request:",
      Request.waiting_times[5] / Request.number_of_received_requests[5])
print("     Order tracking:",
      Request.waiting_times[6] / Request.number_of_received_requests[6])
print('-' * 50)

for i in range(len(Service.In_progress_requests)):
    for lst in Service.In_progress_requests[i]:
        progress_time = simulation_time - lst[1]
        Service.Servers_busy_times[i] += progress_time

print('-' * 50)
print("The efficiency of services:")
print("     Mobile portal service:",
      Service.Servers_busy_times[0] / (simulation_time * number_of_resources[5]))
print("     Order management service:",
      Service.Servers_busy_times[1] / (simulation_time * number_of_resources[2]))
print("     Payment service:",
      Service.Servers_busy_times[2] / (simulation_time * number_of_resources[4]))
print("     Web portal service:",
      Service.Servers_busy_times[3] / (simulation_time * number_of_resources[6]))
print("     Customers management service:",
      Service.Servers_busy_times[4] / (simulation_time * number_of_resources[1]))
print("     Delivery communication:",
      Service.Servers_busy_times[5] / (simulation_time * number_of_resources[3]))
print("     Restaurant management service:",
      Service.Servers_busy_times[6] / (simulation_time * number_of_resources[0]))
print('-' * 50)
