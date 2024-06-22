import socket
import sys
import random
import struct


def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def write_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)


def main(server_ip, server_port, file_path, lmin, lmax):
    data = read_file(file_path)
    data_length = len(data)

    # 随机生成块大小
    block_sizes = []
    while data_length > 0:
        block_size = random.randint(lmin, lmax)
        block_sizes.append(min(block_size, data_length))
        data_length -= block_sizes[-1]

    n_blocks = len(block_sizes)

    # 建立连接
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, int(server_port)))

    # 发送初始化报文
    init_message = struct.pack('!HI', 1, n_blocks)  # Type=1, N=n_blocks
    client.sendall(init_message)
    response = client.recv(1024)
    response_type = struct.unpack('!H', response[:2])[0]
    if response_type != 2:  # Type=2 表示 agree 报文
        print("Initialization failed")
        return

    reversed_chunks = []
    index = 0
    for i, block_size in enumerate(block_sizes):
        # 发送数据块
        chunk = data[index:index + block_size]
        index += block_size
        req_message = struct.pack('!HI', 3, len(chunk)) + chunk.encode('utf-8')  # Type=3, Length=len(chunk)
        client.sendall(req_message)

        # 接收反转数据
        response = client.recv(1024)
        response_type, length = struct.unpack('!HI', response[:6])
        if response_type == 4:  # Type=4 表示 reverseAnswer 报文
            reversed_chunk = response[6:6 + length].decode('utf-8')
            reversed_chunks.insert(0, reversed_chunk)  # 插入到最前面
            print(f"第{i + 1}块: {reversed_chunk}")

    # 将所有反转块连接成一个字符串
    final_reversed_text = ''.join(reversed_chunks)

    # 写入反转后的数据到文件
    write_file('reversed_' + file_path, final_reversed_text)

    client.close()


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python client.py <server_ip> <server_port> <file_path> <lmin> <lmax>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = sys.argv[2]
    file_path = sys.argv[3]
    lmin = int(sys.argv[4])
    lmax = int(sys.argv[5])

    main(server_ip, server_port, file_path, lmin, lmax)
