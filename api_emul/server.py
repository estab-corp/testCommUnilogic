import socket
from api_client import MsgParser, MSGType
from api import MoveRequest, MachineStateMsg, TaskEndedMsg


msg_parser = MsgParser()


def send_machine_state(conn: socket.socket, msg: MachineStateMsg):
    data = msg_parser.machine_state_msg.pack(MSGType.MachineState, msg.test)
    print(f"sending {data.hex(sep=" ")}")
    conn.send(data)


def send_task_ended(conn: socket.socket, req: MoveRequest, ok: bool):
    data = msg_parser.task_ended_msg.pack(
        MSGType.TaskEnded, req.task_id, 1 if ok else 0)
    print(f"sending {data.hex(sep=" ")}")
    conn.send(data)


def send_task_started(conn: socket.socket, req: MoveRequest, ok: bool):
    data = msg_parser.task_started_msg.pack(
        MSGType.TaskStarted, req.task_id, 1 if ok else 0)
    print(f"sending {data.hex(sep=" ")}")
    conn.send(data)


def decode_request(data: bytes) -> MoveRequest:
    params = msg_parser.task_request_msg.unpack(data)
    task_id = params[0]
    vt = params[1]
    origin = (params[2], params[3], params[4])
    dest = (params[5], params[6], params[7])
    return MoveRequest(typ=vt, task_id=task_id, origin=origin, dest=dest)


def client_loop(conn: socket.socket):
    while True:
        data = conn.recv(1024)
        if not data:
            print("close connection")
            return
        print(f"got {len(data)} bytes of data")
        try:
            req = decode_request(data)
            print(req)
            send_task_started(conn, req, ok=(req.task_id % 2 == 0))
            send_machine_state(conn, msg=MachineStateMsg(req.task_id))
            send_task_ended(conn, req, ok=(req.task_id % 2 == 1))

        except Exception as e:
            print(f"error: {e}")


def server_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 9000))
    server.listen(1)
    while True:
        print("Waiting for a connection")
        conn, addr = server.accept()
        print(f"Connected with {addr[0]}:{str(addr[1])}")
        client_loop(conn)
