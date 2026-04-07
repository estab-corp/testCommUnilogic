import socket
from typing import Optional
from log_interf import LoggerInterface
import struct


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

    def _send(self, data):
        assert self.client
        try:
            self.client.send(data)
        except Exception as err:
            self.logger.print(f"conn error{err}")
            self.client = None

    def _recv(self, size):
        assert self.client
        try:
            return self.client.recv(size)
        except Exception as err:
            self.logger.print(f"conn error{err}")
            self.client = None
        return None

    def send_test(self, val: int):
        if self.client is None:
            self.logger.print("not connected!")
            return

        test_tx = struct.pack("=HBL", val, 250, 400)
        self._send(test_tx)

    def test_recv(self):
        if self.client is None:
            self.logger.print("not connected!")
            return

        data = self._recv(6)
        self.logger.print(f"{data}")
        self.logger.print(f"Done receiving {data} {len(data)}")
        if len(data) == 6:
            test_rx0, test_rx1, test_rx2, = struct.unpack("=BBL", data)
            self.logger.print(f"{test_rx0}, {test_rx1}, {test_rx2}")
