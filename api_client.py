import socket
from typing import Optional
from log_interf import LoggerInterface


class APIClient:
    def __init__(self, logger: LoggerInterface):
        self.host: str = ""
        self.port: int = -1
        self.client: Optional[socket.socket] = None
        self.logger = logger

    def connected(self) -> bool:
        return self.client is not None

    def connect(self, host: str, port: int):
        if self.client is not None:
            self.logger.print("already connected")
            return

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
        except Exception as err:
            self.logger.print(f"conn error{err}")
            self.client = None

    def disconnect(self):
        if self.client is None:
            self.logger.print("already disconnected")
            return
        self.client.close()
        self.client = None
