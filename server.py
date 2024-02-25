import grpc
import reporting_pb2
import reporting_pb2_grpc
import time
from concurrent import futures
import random 
from faker import Faker

class ReportingServicer(reporting_pb2_grpc.ReportingServicer):
    def GetSpaceshipStream(self, request, context):
        num_ships = random.randint(1, 10)
        fake = Faker()
        for _ in range(num_ships):
            alignment = random.choice([reporting_pb2.Alignment.ALLY, reporting_pb2.Alignment.ENEMY])
            ship_class = random.choice([reporting_pb2.ShipClass.CORVETTE, reporting_pb2.ShipClass.FRIGATE, reporting_pb2.ShipClass.CRUISER,\
                 reporting_pb2.ShipClass.DESTROYER, reporting_pb2.ShipClass.CARRIER, reporting_pb2.ShipClass.DREADNOUGHT])
            if alignment == reporting_pb2.Alignment.ENEMY:
                ship_name = random.choice([fake.city(), "Unknown"])
            else:
                ship_name = fake.city()    
    

            ship_length = round(random.uniform(80.0, 20000.0),1)
            crew_size = random.randint(4, 500)
            is_armed = random.choice([True, False])
            officers_list = []
            
            if alignment == reporting_pb2.Alignment.ENEMY:
                num_officers = random.randint(0, 10)
            else:
                num_officers = random.randint(1, 10)  
            
            ranks = ['Captain', 'Lieutenant', 'Corporal', 'Sergeant', 'Sergeant Major', \
                'Lieutenant Commander', 'Commander', 'Captain Commander', 'Captain of the Armada']
            for _ in range(num_officers):
                officer = reporting_pb2.Officer(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    rank=random.choice(ranks)
                )
                officers_list.append(officer)

            spaceship = reporting_pb2.Spaceship(
                alignment=alignment,
                name=ship_name,
                ship_class=ship_class,
                length=ship_length,
                crew_size=crew_size,
                is_armed=is_armed,
                officers=officers_list
            )
            yield spaceship
            time.sleep(1)  

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reporting_pb2_grpc.add_ReportingServicer_to_server(ReportingServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()