import socket
from typing import Optional
from log_interf import LoggerInterface
import struct
import threading
import time


class APIClient:
    def __init__(self, logger: LoggerInterface):
        self.host: str = ""
        self.port: int = -1
        self.client: Optional[socket.socket] = None
        self.logger = logger

        self.received_bytes = bytes()
        self._running = False
        self._stop_thread_req = False
        self._thread: Optional[threading.Thread] = None

    def _run(self):
        self._running = True
        print("Running thread")
        while self._running is True:
            if self._stop_thread_req:
                break
            assert self.client
            b = self.client.recv(1)
            if len(b) == 0:
                self.disconnect()
                break
            self.received_bytes += b
            print(f"received {len(self.received_bytes)} bytes")

        print("After thread")
        self._running = False
        self._thread = None

    def connected(self) -> bool:
        return self.client is not None

    def connect(self, host: str, port: int):
        if self.client is not None:
            self.logger.print("already connected")
            return
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            assert self._thread is None
            self._thread = threading.Thread(target=self._run)
            self._stop_thread_req = False
            self._thread.start()
        except Exception as err:
            self.logger.print(f"conn error {type(err)} {err}")
            self.client = None

    def disconnect(self):
        if self.client is None:
            self.logger.print("already disconnected")
            return
        self._stop_thread_req = True
        self.client.close()
        self.client = None

    def _send(self, data):
        assert self.client
        try:
            self.client.send(data)
        except Exception as err:
            self.logger.print(f"conn error {type(err)} {err}")
            self.client = None

    def _recv(self, size):
        assert self.client
        try:
            return self.client.recv(size)
        except Exception as err:
            self.logger.print(f"conn error {type(err)} {err}")
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
        if data is None:
            return
        self.logger.print(f"{data}")
        self.logger.print(f"Done receiving {data} {len(data)}")
        if len(data) == 6:
            test_rx0, test_rx1, test_rx2, = struct.unpack("=BBL", data)
            self.logger.print(f"{test_rx0}, {test_rx1}, {test_rx2}")
