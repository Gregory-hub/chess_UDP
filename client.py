import socket
import threading

from app import App


class Client:
    def __init__(self, data_format: str, buffer_size: int) -> None:
        self.DATA_FORMAT = data_format
        self.BUFFER_SIZE = buffer_size
        self.client = None
        self.client_ip = None
        self.client_port = None
        self.server_ip = None
        self.server_port = None
        self.thread_incoming = None
        self.terminate_incoming = False


    def start(self) -> None:
        success = False
        while not success:
            success = self.__try_init_server_ip_and_port()
            if success == False:
                print("Invalid ip address or port. Try again")

        self.__start_client()


    def __try_init_server_ip_and_port(self) -> bool:
        # stalls the program
        print(r"Enter server ip address and port ({address}:{port})")
        input_str = input(">> ")
        try:
            server_ip, server_port = input_str.split(":")
        except ValueError:
            return False

        try:
            ip_bytes = list(map(int, server_ip.split(".")))
        except ValueError:
            return False
        if len(ip_bytes) != 4:
            return False
        for b in ip_bytes:
            if not 0 <= b <= 255:
                return False

        try:
            server_port = int(server_port)
        except ValueError:
            return False
        if (server_port < 0 or server_port > 65535):
            return False

        self.server_ip = server_ip
        self.server_port = server_port
        return True


    def __start_client(self) -> None:
        print(f"[Client starting] communicating with {self.server_ip}:{self.server_port}")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__connect()

        self.terminate_incoming = False
        self.thread_incoming = threading.Thread(target=self.__handle_incoming)
        self.thread_incoming.start()

        print(f"[Client started] communicating with {self.server_ip}:{self.server_port}")


    def __connect(self) -> None:
        print(f"[Connecting to server] on {self.server_ip}:{self.server_port}")
        print(f"\n{socket.gethostbyname(socket.gethostname())}\n")
        self.client.sendto(b"/connect", (self.server_ip, self.server_port))

        print(f"[Connected to server] on {self.server_ip}:{self.server_port}")


    def __shut_down(self) -> None:
        # stalls the program (for a bit)
        print(f"[Client shutting down]...")
        self.__stop_thread_handle_incoming()
        self.server.close()
        print(f"[Client shut down]")


    def __handle_user_input(self) -> None:
        # stalls the program
        print("Enter messages to send. Type '/exit' to exit")
        message = input(">> ")
        while message != "/exit":
            client.sendto(message.encode(), (self.server_ip, self.server_port))
            message = input(">> ")


    def __handle_incoming(self) -> None:
        # stalls the program
        print("[Starting thread] __handle_incoming")
        while not self.terminate_incoming:
            data, addr = self.client.recv(self.BUFFER_SIZE)
            message = data.decode(self.DATA_FORMAT)

            if len(message) > 0:
                print(f"\n[Received] '{message}' from {addr}\n>> ", end="")


    def __stop_thread_handle_incoming(self) -> None:
        # stalls the program (for a bit)
        print("[Stopping thread] __handle_incoming")
        self.terminate_incoming = True
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:         # sends empty data packet for server.recvfrom to stop stalling
            s.sendto(b'', (self.client_ip, self.client_port))

        self.thread_incoming.join()


if __name__ == "__main__":
    app = App()
    client = Client(app.DATA_FORMAT, app.BUFFER_SIZE)
    client.start()
