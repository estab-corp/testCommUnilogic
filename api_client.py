import struct
import threading
import socket
from enum import IntEnum
from typing import Optional
from log_interf import LoggerInterface
import api


class MSGType(IntEnum):
    Unknown = 0
    TaskStarted = 1
    TaskEnded = 2
    MachineState = 3


class MsgParser:
    def __init__(self):
        self.task_request_msg = struct.Struct("IB3I3I")
        self.rx_header = struct.Struct("B")
        self.task_started_msg = struct.Struct("=BIB")

    def encode_msg(self, msg: api.MoveRequest) -> bytes:
        command_byte = 1  # VTDBRE
        if msg.typ == api.ValidationType.PICK_AND_PLACE:
            command_byte = 2
        if msg.typ == api.ValidationType.PRISE_RETOURNEUR:
            command_byte = 4
        return self.task_request_msg.pack(msg.task_id, command_byte, msg.origin[0], msg.origin[1], msg.origin[2], msg.dest[0], msg.dest[1], msg.dest[2])

    def decode_msg(self, data: bytes) -> Optional[api.RxBaseMsg]:
        msg_typ: MSGType = self._decode_header(data[0:1])
        if msg_typ == MSGType.Unknown:
            return None
        if msg_typ == MSGType.MachineState:
            return api.MachineStateMsg()
        if msg_typ == MSGType.TaskStarted:
            _, task_id, ok = self.task_started_msg.unpack(data)
            return api.TaskStartedMsg(task_id=task_id, ok_status=ok)
        if msg_typ == MSGType.TaskEnded:
            _, task_id, ok = self.task_started_msg.unpack(data)
            return api.TaskEndedMsg(task_id=task_id, ok_status=ok)
        assert 0
        return None

    def _decode_header(self, data: bytes) -> MSGType:
        try:
            msg_typ, = self.rx_header.unpack(data)
            return MSGType(msg_typ)
        except struct.error as err:
            print(f"Error: {err}")
        return MSGType.Unknown


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
        self.msg_parser = MsgParser()

    def _run(self):
        self._running = True
        print("Running thread")
        try:
            while self._running is True:
                if self._stop_thread_req:
                    break
                assert self.client
                b = self.client.recv(1)
                if len(b) == 0:
                    self.disconnect()
                    break
                self.received_bytes += b
        finally:
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
            self.logger.print(f"conn error 3: {type(err)} {str(err)}")
            self.client = None

    def disconnect(self):
        if self.client is None:
            return
        self._stop_thread_req = True
        self.client.close()
        self.client = None

    def _send(self, data):
        assert self.client
        try:
            self.client.send(data)
        except Exception as err:
            self.logger.print(f"conn error 1: {type(err)} {str(err)}")
            self.client = None

    def _recv(self, size):
        assert self.client
        try:
            return self.client.recv(size)
        except Exception as err:
            self.logger.print(f"conn error 2: {type(err)} {str(err)}")
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

    def send_msg(self, msg: api.MoveRequest):
        data = self.msg_parser.encode_msg(msg)
        self.logger.print(f"{data.hex(sep=" ")}")
        self._send(data)


if __name__ == "__main__":
    msg_parser = MsgParser()
    assert msg_parser.decode_msg(bytes()) is None

    msg = msg_parser.decode_msg(
        bytes([0x01, 0X00, 0X00, 0X00, 0XFF, 0X01]))
    assert isinstance(msg, api.TaskStartedMsg)
    print(msg)

    msg = msg_parser.decode_msg(
        bytes([0x02, 0X00, 0X00, 0X00, 0XFF, 0X01]))
    assert isinstance(msg, api.TaskEndedMsg)
    print(msg)

    msg = msg_parser.decode_msg(
        bytes([0x03]))
    assert isinstance(msg, api.MachineStateMsg)
    print(msg)
