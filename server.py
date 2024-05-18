import socket
import threading

import netifaces

address_entries = [netifaces.ifaddresses(interface) for interface in netifaces.interfaces()]
ipv4_addresses = [interface[netifaces.AF_INET] for interface in address_entries if netifaces.AF_INET in interface]
addresses = [address[0]["addr"] for address in ipv4_addresses]

if "127.0.0.1" in addresses:
    addresses.remove("127.0.0.1")

if len(addresses) == 0:
    print("Cannot find ip for local network")
    exit(1)

ip_address = addresses[0]
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((ip_address, port))
print(f"[Server starting] at {ip_address}:{port}")
while True:
    data, addr = server.recvfrom(1024)
    print(f"Received: {data}")

# input_str = ''
# while input_str != 'exit':
#     # print(f'Starting game at {address}:{port}')
#     # print('To choose another address type "address"')
#     # print('To choose another port type "port"')
#     # print('To start game type "start"')
#     # print('To exit game type "exit"')
#     input_str = input(">> ")

print(addresses)
