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
        self.addresses = None
        self.__init_addresses()

        self.sock = None


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
        self.__handle_user_input()


    def initialize_connection(self, opponent_ip: str, opponent_port: int = None) -> None:
        if opponent_port is None:
            opponent_port = self.DEFAULT_PORT

        print(f"[Initialize connection] '/connect' sent to {opponent_ip, opponent_port}")
        self.sock.sendto("/connect".encode(), (opponent_ip, opponent_port))

        timeout_seconds = 30
        self.thread_wait_for_connect_reply = threading.Thread(target=self.__wait_for_connect_reply, args=[opponent_ip, opponent_port, timeout_seconds], daemon=True)
        self.thread_wait_for_connect_reply.start()


    def create_game(self) -> None:
        print("[Game created]")
        self.thread_wait_for_opponent = threading.Thread(target=self.__wait_for_opponent, daemon=True)
        self.thread_wait_for_opponent.start()
        print("[Waiting for opponent]...")


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
        self.sock.shutdown(socket.SHUT_RDWR)
        print(f"[App shut down]")


    def __start(self, ip_address: str = None, port: int = None) -> None:
        print(f"[App starting] at {ip_address}:{port}")
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

            if data.decode() == "/accept" and addr[0] == opponent_ip and addr[1] == opponent_port:
                self.__connect(opponent_ip, opponent_port)
                break

            now = time.time()

        if not self.connected and not self.terminate_wait_for_connect_reply:
            print(f"[Warning] Timeout: cannot connect to {opponent_ip}:{opponent_port}")

        self.thread_wait_for_connect_reply = None
        self.terminate_wait_for_connect_reply = False
        print("[Stopping thread] __wait_for_connect_reply")


    def stop_waiting_for_connect_reply(self):
        self.terminate_wait_for_connect_reply = True


    def stop_waiting_for_opponent(self):
        self.terminate_wait_for_opponent = True


    def __wait_for_opponent(self) -> None:
        # stalls the program
        print("[Starting thread] __wait_for_opponent")
        self.terminate_wait_for_opponent = False
        while not self.terminate_wait_for_opponent:
            try:
                data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
            except BlockingIOError:
                continue
            if data.decode(self.DATA_FORMAT) == "/connect":
                self.__connect(addr[0], addr[1])
                self.sock.sendto("/accept".encode(), (self.opponent_ip, self.opponent_port))
                break

        self.thread_wait_for_opponent = None
        self.terminate_wait_for_opponent = False

        print("[Stopping thread] __wait_for_opponent")


    def __connect(self, opponent_ip: str, opponent_port: int) -> None:
        self.opponent_ip = opponent_ip
        self.opponent_port = opponent_port
        self.connected = True
        print(f"[Connected] to {self.opponent_ip}:{self.opponent_port}")


    def __handle_user_input(self):
        # stalls the program
        text = f"[App is running] at {self.ip}:{self.port}\n"
        text += "To choose another ip address type '/address'\nTo choose another port type '/port'\n"
        text += "To create a game type '/create'\nTo connect to a game type '/connect'\nTo exit type '/exit'"
        print(text)

        input_str = ""
        while True:
            try:
                input_str = input(">> ")
            except KeyboardInterrupt:
                print()
                self.shut_down()
                return

            match input_str:
                case "/address":
                    for i in range(len(self.addresses)):
                        address = self.addresses[i]
                        print(f"{i}: {address}")
                    index = int(input("Choose address entry\n>> "))
                    new_address = self.addresses[index]
                    self.restart(ip_address=new_address, port=self.port)

                case "/port":
                    new_port = int(input("Enter port number\n>> "))
                    self.restart(ip_address=self.ip, port=new_port)

                case "/create":
                    self.create_game()
                    self.thread_wait_for_opponent.join()

                case "/connect":
                    opponent_ip = input("Enter opponent ip address\n>> ")
                    self.initialize_connection(opponent_ip)
                    self.thread_wait_for_connect_reply.join()

                case "/exit":
                    self.shut_down()
                    return


if __name__ == "__main__":
    app = UDPClient()
    app.start()
