import struct
import threading
import socket
from enum import IntEnum
from typing import Optional, Tuple
from log_interf import LoggerInterface
import api


class MSGType(IntEnum):
    Unknown = 0
    TaskStarted = 1
    TaskEnded = 2
    MachineState = 3


class MsgParser:
    def __init__(self):
        rx_header_fmt = "B"
        self.task_request_msg = struct.Struct("=IB3I3I")
        self.rx_header = struct.Struct(f"{rx_header_fmt}")
        self.task_started_msg = struct.Struct(f"={rx_header_fmt}IB")
        self.task_ended_msg = struct.Struct(f"={rx_header_fmt}IB")
        self.machine_state_msg = struct.Struct(f"={rx_header_fmt}B")

    def encode_msg(self, msg: api.MoveRequest) -> bytes:
        command_byte = 1  # VTDBRE
        if msg.typ == api.ValidationType.PICK_AND_PLACE:
            command_byte = 2
        if msg.typ == api.ValidationType.PRISE_RETOURNEUR:
            command_byte = 4
        return self.task_request_msg.pack(msg.task_id, command_byte,  msg.origin[0], msg.origin[1], msg.origin[2], msg.dest[0], msg.dest[1], msg.dest[2])

    def decode_msg(self, data: bytes) -> Tuple[Optional[api.RxBaseMsg], int]:
        msg_typ: MSGType = self._decode_header(data[0:1])
        if msg_typ == MSGType.Unknown:
            return None, 0
        if msg_typ == MSGType.MachineState:
            _, test = self.machine_state_msg.unpack(data)
            return api.MachineStateMsg(test=test), self.machine_state_msg.size
        if msg_typ == MSGType.TaskStarted:
            _, task_id, ok = self.task_started_msg.unpack(data)
            return api.TaskStartedMsg(task_id=task_id, ok_status=ok), self.task_started_msg.size
        if msg_typ == MSGType.TaskEnded:
            _, task_id, ok = self.task_ended_msg.unpack(data)
            return api.TaskEndedMsg(task_id=task_id, ok_status=ok), self.task_ended_msg.size
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
                self._try_decode()
        finally:
            print("After thread")
            self._running = False
            self._thread = None

    def _try_decode(self):
        print("Try decoding some msg...")
        try:
            msg, read_size = self.msg_parser.decode_msg(self.received_bytes)
            if msg is not None:
                self.logger.print(f"received Msg {msg} read_size={read_size}")
            else:
                self.logger.print("invalid buffer")
        except Exception as err:
            self.logger.print(f"Decode error {err}")

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

    def send_msg(self, msg: api.MoveRequest):
        data = self.msg_parser.encode_msg(msg)
        self.logger.print(f"{data.hex(sep=" ")}")
        self._send(data)


if __name__ == "__main__":
    msg_parser = MsgParser()
    msg, size = msg_parser.decode_msg(bytes())
    assert msg is None

    buf = bytes([0x01, 0X00, 0X00, 0X00, 0XFF, 0X01])
    msg, read_size = msg_parser.decode_msg(
        buf)
    assert isinstance(msg, api.TaskStartedMsg)
    assert read_size == len(buf)
    print(msg)

    buf = bytes([0x02, 0X00, 0X00, 0X00, 0XFF, 0X01])
    msg, read_size = msg_parser.decode_msg(
        buf)
    assert isinstance(msg, api.TaskEndedMsg)
    assert read_size == len(buf)
    print(msg)

    buf = bytes([0x03, 0X02])
    msg, read_size = msg_parser.decode_msg(buf)
    assert isinstance(msg, api.MachineStateMsg)
    assert read_size == len(buf)
    print(msg)
