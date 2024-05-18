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

FORMAT = "utf-8"
ip_address = "192.168.1.100"
port = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[Client starting] sending to {ip_address}:{port}")
print("Enter messages and send them. Type '\\exit' to exit")
message = input(">> ")
while message != "\\exit":
    client.sendto(message.encode(), (ip_address, port))
    message = input(">> ")
