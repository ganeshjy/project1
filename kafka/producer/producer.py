import socket
import os
from dotenv import load_dotenv
load_dotenv()
Port = int(os.getenv('Port'))
print(Port)
ADDR =('server',Port)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
while True:
    data = client.recv(1024).decode('utf-8')
    if not data:
        break
    from confluent_kafka import Producer
    producer_config={'bootstrap.servers':'kafka:9092'}
    producer = Producer(producer_config)
    send_data=producer.produce('learn',data)
    producer.flush()
    print("received data from server",data)
client.close()