import socket
from api_client import MsgParser


def client_loop(conn: socket.socket):
    while True:
        data = conn.recv(1024)
        if not data:
            print("close connection")
            return
        print(f"got data {data}")


def server_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 9000))
    server.listen(1)
    while True:
        print("Waiting for a connection")
        conn, addr = server.accept()
        print(f"Connected with {addr[0]}:{str(addr[1])}")
        client_loop(conn)
