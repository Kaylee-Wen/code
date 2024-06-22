import socket
import time
import random
import threading
import sys


def handle_client(sock, client_address, data):
    print(f"Connection from {client_address}")
    if data == b"SYN":
        sock.sendto(b"SYN-ACK", client_address)
        print("Sent SYN-ACK")
    elif data == b"ACK":
        print("Connection established")
    elif data.startswith(b"FIN"):
        sock.sendto(b"ACK", client_address)
        print("Sent FIN-ACK, closing connection")
        return
    else:
        msg = data.decode()
        seq_no = int(msg[:4], 16)
        ver = int(msg[4:6], 16)
        filler = msg[6:206]  # 其他内容部分为200字节
        print(f"Received: {seq_no} from {client_address}")

        # 随机决定是否丢弃报文
        if random.random() < 0.5:  # 50%的丢包率
            print(f"Packet {seq_no} dropped")
            return

        # 回复客户端
        server_time = time.strftime('%H-%M-%S')
        response = f"{seq_no:04x}{ver:02x}{server_time}"
        sock.sendto(response.encode(), client_address)
        print(f"Responded: {response} to {client_address}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    server_address = ('0.0.0.0', port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_address)

    print(f"Server listening on {server_address}")
    while True:
        data, client_address = sock.recvfrom(2048)
        threading.Thread(target=handle_client, args=(sock, client_address, data)).start()


if __name__ == "__main__":
    main()
