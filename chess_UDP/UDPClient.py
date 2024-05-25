import socket
import threading
import time

import netifaces


class UDPClient:
    def __init__(self):
        self.DATA_FORMAT = "utf-8"
        self.BUFFER_SIZE = 1024
        self.EXCLUDED_IPS = ["127.0.0.1"]
        self.DEFAULT_PORT = 5000
        self.ip = None
        self.port = None
        self.opponent_ip = None
        self.opponent_port = None
        self.connected = False
        self.thread_wait_for_opponent = None
        self.terminate_wait_for_opponent = False
        self.thread_wait_for_connect_reply = None
        self.terminate_wait_for_connect_reply = False
        self.thread_receive = None
        self.terminate_receive = False
        self.shut_client_down = False
        self.addresses = None
        self.__init_addresses()

        self.sock = None

        self.message_received = ""
        self.message_read = True


    def __init_addresses(self) -> None:
        address_entries = [netifaces.ifaddresses(interface) for interface in netifaces.interfaces()]
        ipv4_addresses = [interface[netifaces.AF_INET] for interface in address_entries if netifaces.AF_INET in interface]
        self.addresses = [address[0]["addr"] for address in ipv4_addresses]

        for ip in self.EXCLUDED_IPS:
            if ip in self.addresses:
                self.addresses.remove(ip)

        if len(self.addresses) == 0:
            raise ConnectionError("Cannot find ip for local network")


    def start(self, ip_address: str = None, port: int = None) -> None:
        self.__initialize_socket(ip_address, port)


    def try_to_connect(self, opponent_ip: str, opponent_port: int = None) -> None:
        if opponent_port is None:
            opponent_port = self.DEFAULT_PORT

        print(f"[Initialize connection] '/connect' sent to {opponent_ip, opponent_port}")
        self.sock.sendto("/connect".encode(), (opponent_ip, opponent_port))

        timeout_seconds = 30
        self.thread_wait_for_connect_reply = threading.Thread(target=self.__wait_for_connect_reply, args=[opponent_ip, opponent_port, timeout_seconds])
        self.thread_wait_for_connect_reply.start()


    def wait_for_connection(self, answer_message: str = None) -> None:
        if self.connected:
            print("[Opponent connected]")
            return
        self.thread_wait_for_opponent = threading.Thread(target=self.__wait_for_opponent, args=[answer_message])
        self.thread_wait_for_opponent.start()
        print("[Waiting for opponent to connect]...")


    def send_to_opponent(self, data: str) -> None:
        print(f"[Send] '{data}' to {self.opponent_ip}:{self.opponent_port}")
        if self.connected:
            self.sock.sendto(data.encode(), (self.opponent_ip, self.opponent_port))


    def start_receiving(self) -> None:
        print("[Starting receiving incoming data]")
        self.thread_receive = threading.Thread(target=self.__receive)
        self.thread_receive.start()


    def restart(self, ip_address: str = None, port: int = None) -> None:
        self.shut_down()
        self.__start(ip_address, port)


    def shut_down(self) -> None:
        print(f"[App shutting down]...")
        if self.thread_wait_for_opponent is not None:
            self.terminate_wait_for_opponent = True
            self.thread_wait_for_opponent.join()
        if self.thread_wait_for_connect_reply is not None:
            self.terminate_wait_for_connect_reply = True
            self.thread_wait_for_connect_reply.join()
        if self.thread_receive is not None:
            self.terminate_receive = True
            self.thread_receive.join()
        self.sock.shutdown(socket.SHUT_RDWR)
        print(f"[App shut down]")
        self.shut_client_down = True


    def extract_ip_and_port(self, address_port_str: str) -> tuple:
        try:
            ip, port = address_port_str.split(":")
        except ValueError:
            return None, None

        if not self.__address_is_valid(ip) or not self.__port_is_valid(port):
            return None, None

        port = int(port)

        return ip, port


    def __start(self, ip_address: str = None, port: int = None) -> None:
        print(f"[App starting] at {ip_address}:{port}...")
        self.__initialize_socket(ip_address, port)
        print(f"[App started] at {ip_address}:{port}")


    def __initialize_socket(self, ip_address: str = None, port: int = None) -> None:
        if ip_address is None:
            ip_address = self.addresses[0]
        elif ip_address not in self.addresses:
            raise ValueError("Unknown or invalid ip address")

        if port is None:
            port = self.DEFAULT_PORT
        elif port < 0 or port > 65535:
            raise ValueError("Invalid port number")

        self.ip = ip_address
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Internet, UDP
        self.sock.bind((ip_address, port))
        self.sock.settimeout(0)


    def __wait_for_connect_reply(self, opponent_ip: str, opponent_port: int, timeout_seconds: float) -> None:
        # stalls the program
        print("[Starting thread] __wait_for_connect_reply")
        self.terminate_wait_for_connect_reply = False

        start = time.time()
        now = time.time()
        while not self.terminate_wait_for_connect_reply and now - start < timeout_seconds:
            try:
                data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
            except BlockingIOError:
                continue
            except ConnectionResetError as e:
                print(e)
                continue

            message = data.decode()
            if message.startswith("/accept") and addr[0] == opponent_ip and addr[1] == opponent_port:
                self.__connect(opponent_ip, opponent_port)
                self.message_received = ' '.join(message.split(' ')[1:])
                self.message_read = False
                break

            now = time.time()

        if not self.connected and not self.terminate_wait_for_connect_reply:
            print(f"[Warning] Timeout: cannot connect to {opponent_ip}:{opponent_port}")

        self.thread_wait_for_connect_reply = None
        self.terminate_wait_for_connect_reply = False
        print("[Stopping thread] __wait_for_connect_reply")


    def __wait_for_opponent(self, answer_message: str) -> None:
        # stalls the program
        print("[Starting thread] __wait_for_opponent")
        print("Answer message =", answer_message)
        self.terminate_wait_for_opponent = False
        while not self.terminate_wait_for_opponent:
            try:
                data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
            except BlockingIOError:
                continue
            if data.decode(self.DATA_FORMAT) == "/connect":
                self.__connect(addr[0], addr[1])
                self.sock.sendto(("/accept " + answer_message).encode(), (self.opponent_ip, self.opponent_port))
                break

        self.thread_wait_for_opponent = None
        self.terminate_wait_for_opponent = False

        print("[Stopping thread] __wait_for_opponent")


    def __receive(self) -> None:
        # stalls the program
        print("[Starting thread] __receive")
        self.terminate_receive = False

        while not self.terminate_receive:
            try:
                data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
            except BlockingIOError:
                continue

            self.message_read = False
            self.message_received = data.decode()

        self.thread_receive = None
        self.terminate_receive = False
        print("[Stopping thread] __receive")


    def __connect(self, opponent_ip: str, opponent_port: int) -> None:
        self.opponent_ip = opponent_ip
        self.opponent_port = opponent_port
        self.connected = True
        print(f"[Connected] to {self.opponent_ip}:{self.opponent_port}")


    def __address_is_valid(self, ip_address: str) -> bool:
        try:
            ip_bytes = list(map(int, ip_address.split(".")))
        except ValueError:
            return False
        if len(ip_bytes) != 4:
            return False
        for b in ip_bytes:
            if not 0 <= b <= 255:
                return False

        return True


    def __port_is_valid(self, port: str) -> bool:
        try:
            port = int(port)
        except ValueError:
            return False
        if (port < 0 or port > 65535):
            return False
        return True
