import socket
import sys
import errno
import json
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("Port"))
SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)
ADDR = ('', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket created")

server.bind(ADDR)    # bind this socket to the address we configured earlier
server.listen(2)
print(f"[LISTENING] Server is listening on {SERVER}")
conn, addr = server.accept()
print(f'CONNECTION FROM {addr} HAS BEEN ESTABLISHED')
count = 1
while count<=5:
        try:
            for i in range(0,5):     
                route = ['Newyork,USA','Chennai, India','Bengaluru, India','London,UK']
                routefrom = random.choice(route)
                routeto = random.choice(route)
                if (routefrom!=routeto):
                    data = {
                        "Battery_Level":round(random.uniform(2.00,5.00),2),
                        "Device_ID": random.randint(1150,1158),
                        "First_Sensor_temperature":round(random.uniform(10,40.0),1),
                        "Route_From":routefrom,
                        "Route_To":routeto
                        }
                    userdata = (json.dumps(data, indent=1)).encode(FORMAT)
                    conn.send(userdata)
                    print(count)
                    print(userdata)
                    count+=1
                    time.sleep(2)
                    break
                else:
                    continue
            # clientdata = conn.recv(1024).decode(FORMAT)
            # print("ACKNOWLEDGEMENT RECEIVED FROM CLIENT : " +clientdata)
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass
     #close the connection
conn.close()