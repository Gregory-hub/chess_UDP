from UDPClient import UDPClient


class App:
    def __init__(self):
        self.udp_clent = UDPClient()
    

    def start(self):
        self.udp_clent.start()


if __name__ == "__main__":
    app = App()
    app.start()
