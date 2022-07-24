import random
import simpy


class Service:
    mobile_portal_resources = None
    order_management_resources = None
    payment_resources = None

    def __init__(self, type):
        self.type = type
        if self.type == "mobile portal service":
            self.resources = Service.mobile_portal_resources
            self.mean = 1.0 / 2
        elif self.type == "order management service":
            self.resources = Service.order_management_resources
            self.mean = 1.0 / 6
        elif self.type == "payment service":
            self.resources = Service.payment_resources
            self.mean = 1.0 / 12
        elif self.type == "web portal service":
            self.resources = Service.mobile_portal_resources
            self.mean = 1.0 / 3
        elif self.type == "customers management service":
            self.resources = Service.order_management_resources
            self.mean = 1.0 / 5
        elif self.type == "delivery communication":
            self.resources = Service.order_management_resources
            self.mean = 1.0 / 9
        elif self.type == "restaurant management service":
            self.resources = Service.order_management_resources
            self.mean = 1.0 / 8



class Request:
    id = 0

    def __init__(self, type):
        Request.id += 1
        self.id = Request.id
        self.type = type
        self.processes = []
        self.turn = -1
        if type == 1:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("order management service"))
            self.processes.append(Service("payment service"))
        elif type == 2:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("order management service"))
            self.processes.append(Service("payment service"))
        elif type == 3:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("customers management service"))
            self.processes.append(Service("delivery communication"))
        elif type == 4:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("restaurant management service"))
        elif type == 5:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("restaurant management service"))
        elif type == 6:
            self.processes.append(Service("web portal service"))
            self.processes.append(Service("restaurant management service"))
            self.processes.append(Service("delivery communication"))
        elif type == 7:
            self.processes.append(Service("mobile portal service"))
            self.processes.append(Service("order management service"))

    def current_process(self):
        return self.processes[self.turn]

    def next_process(self):
        self.turn += 1


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
    time_entered_queue = env.now
    print(service.type, "time_entered_queue: ", time_entered_queue, request.id)
    with service.resources.request() as req:
        yield req
        time_lef_queue = env.now
        print(service.type, "time_lef_queue: ", time_lef_queue, request.id)
        time_in_queue = time_lef_queue - time_entered_queue
        if len(request.processes) > request.turn + 1:
            request.next_process()
            yield env.process(general_service(request))
            request.turn -= 1
        service_time = random.expovariate(service.mean)
        print(service.type, "service time:", service_time)
        yield env.timeout(service_time)


env = simpy.Environment()
number_of_resources = list(map(int, input().split()))
Service.order_management_resources = simpy.Resource(env, capacity=number_of_resources[2])
Service.payment_resources = simpy.Resource(env, capacity=number_of_resources[4])
Service.mobile_portal_resources = simpy.Resource(env, capacity=number_of_resources[5])
rate = 30
env.process(request_generator(rate))
env.run(until=50)
