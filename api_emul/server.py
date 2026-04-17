import socket
from api_client import MsgParser
from api import MoveRequest


msg_parser = MsgParser()


def decode_request(data: bytes):
    params = msg_parser.task_request_msg.unpack(data)
    task_id = params[0]
    vt = params[1]
    origin = (params[2], params[3], params[4])
    dest = (params[5], params[6], params[7])
    req = MoveRequest(typ=vt, task_id=task_id, origin=origin, dest=dest)
    print(req)


def client_loop(conn: socket.socket):
    while True:
        data = conn.recv(1024)
        if not data:
            print("close connection")
            return
        print(f"got {len(data)} bytes of data")
        try:
            decode_request(data)
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
