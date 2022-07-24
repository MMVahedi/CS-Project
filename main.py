import random
import simpy


class Service:
    mobile_portal_resources = None
    order_management_resources = None
    payment_resources = None
    web_portal_resources = None
    customers_management_resources = None
    delivery_communication_resources = None
    restaurant_management_resources = None
    mobile_portal_queue = []
    order_management_queue = []
    payment_queue = []
    web_portal_queue = []
    customers_management_queue = []
    delivery_communication_queue = []
    restaurant_management_queue = []
    mobile_portal_queue_time_sum = 0
    order_management_queue_time_sum = 0
    payment_queue_time_sum = 0
    web_portal_queue_time_sum = 0
    customers_management_queue_time_sum = 0
    delivery_communication_queue_time_sum = 0
    restaurant_management_queue_time_sum = 0

    def __init__(self, type):
        self.type = type
        if self.type == "mobile portal service":
            self.resources = Service.mobile_portal_resources
            self.queue = Service.mobile_portal_queue
            self.queue_time_sum = Service.mobile_portal_queue_time_sum
            self.mean = 1.0 / 2
        elif self.type == "order management service":
            self.resources = Service.order_management_resources
            self.queue = Service.order_management_queue
            self.queue_time_sum = Service.order_management_queue_time_sum
            self.mean = 1.0 / 6
        elif self.type == "payment service":
            self.resources = Service.payment_resources
            self.queue = Service.payment_queue
            self.queue_time_sum = Service.payment_queue_time_sum
            self.mean = 1.0 / 12
        elif self.type == "web portal service":
            self.resources = Service.web_portal_resources
            self.queue = Service.web_portal_queue
            self.queue_time_sum = Service.web_portal_queue_time_sum
            self.mean = 1.0 / 3
        elif self.type == "customers management service":
            self.resources = Service.customers_management_resources
            self.queue = Service.customers_management_queue
            self.queue_time_sum = Service.customers_management_queue_time_sum
            self.mean = 1.0 / 5
        elif self.type == "delivery communication":
            self.resources = Service.delivery_communication_resources
            self.queue = Service.delivery_communication_queue
            self.queue_time_sum = Service.delivery_communication_queue_time_sum
            self.mean = 1.0 / 9
        elif self.type == "restaurant management service":
            self.resources = Service.restaurant_management_resources
            self.queue = Service.restaurant_management_queue
            self.queue_time_sum = Service.restaurant_management_queue_time_sum
            self.mean = 1.0 / 8


class Request:
    id = 0

    def __init__(self, type):
        Request.id += 1
        self.id = Request.id
        self.priority = 0
        self.type = type
        self.processes = []
        self.turn = -1
        if type == 1:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("order management service"))
            self.processes.append(Service("payment service"))
            self.priority = 1
        elif type == 2:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("order management service"))
            self.processes.append(Service("payment service"))
            self.priority = 1
        elif type == 3:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("customers management service"))
            self.processes.append(Service("delivery communication"))
            self.priority = 2
        elif type == 4:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("restaurant management service"))
            self.priority = 2
        elif type == 5:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("restaurant management service"))
            self.priority = 2
        elif type == 6:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("restaurant management service"))
            self.processes.append(Service("delivery communication"))
            self.priority = 1
        elif type == 7:
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
    service.queue.append(request.id)
    time_entered_queue = env.now
    print(service.type, "time_entered_queue: ", time_entered_queue, request.id)
    with service.resources.request() as req:
        yield req
        time_lef_queue = env.now
        service.queue.pop(0)
        print(service.type, "time_lef_queue: ", time_lef_queue, request.id)
        time_in_queue = time_lef_queue - time_entered_queue
        service.queue_time_sum += time_in_queue
        if len(request.processes) > request.turn + 1:
            request.next_process()
            yield env.process(general_service(request))
            request.turn -= 1
        service_time = random.expovariate(service.mean)
        print(service.type, "service time:", service_time)
        yield env.timeout(service_time)


Queues_length = {}
env = simpy.Environment()

number_of_resources = list(map(int, input().split()))
Service.restaurant_management_resources = simpy.Resource(env, capacity=number_of_resources[0])
Service.customers_management_resources = simpy.Resource(env, capacity=number_of_resources[1])
Service.order_management_resources = simpy.Resource(env, capacity=number_of_resources[2])
Service.delivery_communication_resources = simpy.Resource(env, capacity=number_of_resources[3])
Service.payment_resources = simpy.Resource(env, capacity=number_of_resources[4])
Service.mobile_portal_resources = simpy.Resource(env, capacity=number_of_resources[5])
Service.web_portal_resources = simpy.Resource(env, capacity=number_of_resources[6])

rate = int(input())
simulation_time = int(input())

maximum_waiting_times = list(map(int, input().split()))

env.process(request_generator(rate))
env.run(until=50)
