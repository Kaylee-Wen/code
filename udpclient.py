import socket
import time
import statistics
import random
import sys


def establish_connection(sock, server_address):
    # 三次握手过程
    # 第一次握手：客户端发送SYN
    sock.sendto(b"SYN", server_address)
    print("Sent SYN")

    # 第二次握手：服务器返回SYN-ACK
    try:
        response, _ = sock.recvfrom(2048)
        if response.decode() == "SYN-ACK":
            print("Received SYN-ACK")
            # 第三次握手：客户端发送ACK
            sock.sendto(b"ACK", server_address)
            print("Sent ACK")
            return True
    except socket.timeout:
        print("Handshake failed")
        return False
    return False


def main(server_ip, server_port):
    server_address = (server_ip, server_port)
    version = 2
    timeout = 0.1  # 100 毫秒
    num_requests = 12
    filler = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=200))  # 其他内容为200字节

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    if not establish_connection(sock, server_address):
        print("Connection establishment failed")
        return

    received_packets = 0
    rtts = []
    first_response_time = None
    last_response_time = None

    for seq_no in range(1, num_requests + 1):
        message = f"{seq_no:04x}{version:02x}{filler}"  # 将Seq no和Ver调整为16进制格式
        attempts = 0
        while attempts < 3:  # 初次发送失败后仅重传两次
            start_time = time.time()
            sock.sendto(message.encode(), server_address)
            try:
                response, _ = sock.recvfrom(2048)
                end_time = time.time()
                rtt = (end_time - start_time) * 1000  # RTT以毫秒为单位
                rtts.append(rtt)
                received_packets += 1
                response_seq_no = int(response[:4], 16)
                response_ver = int(response[4:6], 16)
                server_time = response[6:].decode()

                if first_response_time is None:
                    first_response_time = server_time
                last_response_time = server_time

                print(f"Sequence no: {response_seq_no}, ServerIP: {server_ip}:{server_port}, RTT: {rtt:.2f} ms")
                break
            except socket.timeout:
                attempts += 1
                print(f"Sequence no: {seq_no}, request time out")
                if attempts == 3:
                    print(f"Sequence no: {seq_no}, request failed after 3 attempts")

    # 总结信息
    print("\n[Summary]")
    print(f"Received UDP packets: {received_packets}")
    packet_loss_rate = (1 - received_packets / num_requests) * 100
    print(f"Packet loss rate: {packet_loss_rate:.2f}%")
    if rtts:
        max_rtt = max(rtts)
        min_rtt = min(rtts)
        avg_rtt = sum(rtts) / len(rtts)
        std_dev_rtt = statistics.stdev(rtts) if len(rtts) > 1 else 0.0
        print(f"Max RTT: {max_rtt:.2f} ms")
        print(f"Min RTT: {min_rtt:.2f} ms")
        print(f"Avg RTT: {avg_rtt:.2f} ms")
        print(f"RTT Std Dev: {std_dev_rtt:.2f} ms")

        # 计算服务器响应时间差
        first_time_struct = time.strptime(first_response_time, '%H-%M-%S')
        last_time_struct = time.strptime(last_response_time, '%H-%M-%S')

        # 计算时间差（直接计算小时、分钟、秒的差值）
        first_seconds = first_time_struct.tm_hour * 3600 + first_time_struct.tm_min * 60 + first_time_struct.tm_sec
        last_seconds = last_time_struct.tm_hour * 3600 + last_time_struct.tm_min * 60 + last_time_struct.tm_sec
        response_time_span_seconds = last_seconds - first_seconds

        print(f"Server Response Time Span: {response_time_span_seconds}秒")

    # 模拟TCP连接释放过程
    sock.sendto(b"FIN", server_address)
    try:
        response, _ = sock.recvfrom(2048)
        if response.decode() == "ACK":
            print("Connection closed gracefully")
    except socket.timeout:
        print("Failed to receive FIN-ACK from server")

    # 关闭连接
    sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    main(server_ip, server_port)
