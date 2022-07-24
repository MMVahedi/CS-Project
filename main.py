import random
import simpy


class Service:
    All_resources = [None] * 7
    Queues = [[] for i in range(7)]
    Queues_time_sum = [0] * 7

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

    def add_customer_to_queue(self, request_id):
        Service.Queues[self.id].append(request_id)

    def remove_customer_from_queue(self):
        Service.Queues[self.id].pop(0)

    def add_time_to_queue_time_sum(self, time):
        Service.Queues_time_sum[self.id] += time

    def get_resources(self):
        return Service.All_resources[self.id]


class Request:
    id = 0

    def __init__(self, request_type):
        Request.id += 1
        self.id = Request.id
        self.priority = 0
        self.type = request_type
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
    request_id = 0
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
        request_id += 1


def general_service(request):
    global env
    service = request.current_process()
    service.add_customer_to_queue(request.id)
    time_entered_queue = env.now
    print(service.type, "time_entered_queue: ", time_entered_queue, request.id)
    with service.get_resources().request() as req:
        yield req
        time_lef_queue = env.now
        service.remove_customer_from_queue()
        print(service.type, "time_lef_queue: ", time_lef_queue, request.id)
        time_in_queue = time_lef_queue - time_entered_queue
        service.add_time_to_queue_time_sum(time_in_queue)
        if len(request.processes) > request.turn + 1:
            request.next_process()
            yield env.process(general_service(request))
            request.turn -= 1
        service_time = random.expovariate(service.mean)
        print(service.type, "service time:", service_time)
        yield env.timeout(service_time)


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

maximum_waiting_times = list(map(int, input().split()))

env.process(request_generator(rate))
env.run(until=50)
