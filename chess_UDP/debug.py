class Debug:
    def __init__(self):
        self.enabled = True
    

    def print(self, message: str, end: str = None, sep: str = None) -> None:
        if self.enabled:
            print(message)
