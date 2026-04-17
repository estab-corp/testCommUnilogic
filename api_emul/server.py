import socket

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 9000))
    server.listen(1)
    while True:
        print("Waiting for a connection")
        conn, addr = server.accept()
        print(f"Connected with {addr[0]}:{str(addr[1])}")
        while True:
            data = conn.recv(1024)
            if not data:
                print("close connection")
                break
            print(f"got data {data}")
