import socket
import select
import struct


def handle_client(client_socket):
    data = client_socket.recv(1024)
    if not data:
        return False

    msg_type = struct.unpack('!H', data[:2])[0]
    if msg_type == 1:  # Type=1 表示 Initialization 报文
        n_blocks = struct.unpack('!I', data[2:6])[0]
        client_socket.sendall(struct.pack('!H', 2))  # Type=2 表示 agree 报文
    elif msg_type == 3:  # Type=3 表示 ReverseRequest 报文
        length = struct.unpack('!I', data[2:6])[0]
        to_reverse = data[6:6 + length].decode('utf-8')
        reversed_data = to_reverse[::-1]
        response = struct.pack('!HI', 4, len(reversed_data)) + reversed_data.encode(
            'utf-8')  # Type=4 表示 reverseAnswer 报文
        client_socket.sendall(response)

    return True


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 12000))
    server.listen(5)
    server.setblocking(False)

    print("Server listening on port 12000")

    inputs = [server]
    outputs = []

    while True:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        for s in readable:
            if s is server:
                client_socket, addr = server.accept()
                print(f"Accepted connection from {addr}")
                client_socket.setblocking(False)
                inputs.append(client_socket)
            else:
                if not handle_client(s):
                    inputs.remove(s)
                    s.close()

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()


if __name__ == "__main__":
    main()
