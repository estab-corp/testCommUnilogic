import socket
import time
import struct


def main():
    host = '192.168.250.101'
    port = 9000
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print("connected")
    val = 0

    while True:
        test_tx = struct.pack("=HBL", val, 250, 400)
        s = bytes([val, 0, 254, 0, 127])
        # print(f"data= '{test_tx}'")
        client.send(test_tx)
        # print(s)
        val += 1
        print("recv")

        data = client.recv(6)
        print(data)
        print(f"Done receive {data} {len(data)}")
        if len(data) == 6:
            test_rx0, test_rx1, test_rx2, = struct.unpack("=BBL", data)
            print(test_rx0, test_rx1, test_rx2)
        time.sleep(2)


if __name__ == "__main__":
    main()
