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

ip_address = "26.116.186.114"
port = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b"Halo", (ip_address, port))
