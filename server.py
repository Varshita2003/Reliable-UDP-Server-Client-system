import socket
import time
import os
import sys
class PacketGenerator:
    def __init__(self, filename, packet_size):
        self.filename = filename
        self.packet_size = packet_size
    
    def generate_packets(self):
        packets = []
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.packet_size)
                if not data:
                    break
                packets.append(data)

        print(len(packets), "no of packets")
        return packets
    
def go_back_n(sock, filename, packet_size, window_size, addr, timeout):
    packet_gen = PacketGenerator(filename, packet_size)
    packets = packet_gen.generate_packets()
    
    # seq_num = 0
    base = 0
    next_seq_num = 0
    window_end = min(base + window_size, len(packets))
    
    while base < len(packets):
        for i in range(base, window_end):
            packet_with_seq = str(next_seq_num).zfill(4).encode() + packets[i] 
            sock.sendto(packet_with_seq, addr)
            print(f"Sent packet {i} with sequence number {next_seq_num}")
            next_seq_num += 1

        try:
            sock.settimeout(timeout)
            ack, _ = sock.recvfrom(1024)
            ack_seq_num = int(ack.decode())
            print(f"Received ACK for packet {ack_seq_num}")

            if ack_seq_num >= base:
                base = ack_seq_num + 1
                window_end = min(base + window_size, len(packets))
                next_seq_num = base
            else:
                print(f"Ignoring outdated ACK for packet {ack_seq_num}")
        except socket.timeout:
            print("Timeout occurred, retransmitting...")
            next_seq_num = base

    print("All packets sent and ACKed")
    sock.sendto(b'SERVER_CLOSED', addr)
    sock.settimeout(None)
    print("Server closed")





def stop_and_wait(sock, filename, packet_size, addr, timeout=0.1, max_attempts=3):
    packet_gen = PacketGenerator(filename, packet_size)
    packets = packet_gen.generate_packets()
    
    for packet in packets:
        attempts = 0
        while attempts < max_attempts:
            sock.sendto(packet, addr)
            start_time = time.time()
            sock.settimeout(timeout)
            try:
                ack, _ = sock.recvfrom(1024)
                if ack.decode() == 'ACK':
                    print("Packet ACKed!")
                    break
            except socket.timeout:
                print("Timeout occurred, retransmitting...")
            finally:
                attempts += 1
            elapsed_time = time.time() - start_time

    sock.sendto(b'SERVER_CLOSED', addr)
    sock.settimeout(None)
    print("Server closed")


def selective_repeat(sock, filename, packet_size, window_size, addr):
    packet_gen = PacketGenerator(filename, packet_size)
    packets = packet_gen.generate_packets()
    
    seq_num = 0
    acks = [False] * len(packets)
    
    while True:
        for i in range(seq_num, min(seq_num + window_size, len(packets))):
            sock.sendto(packets[i], addr)
            time.sleep(0.1)  # Simulating network delay
        
        ack, _ = sock.recvfrom(1024)
        ack_seq_num = int(ack.decode())
        
        if ack_seq_num >= seq_num:
            print(f"Packet {ack_seq_num} ACKed")
            acks[ack_seq_num] = True
            while seq_num < len(packets) and acks[seq_num]:
                seq_num += 1
        else:
            print(f"Received outdated ACK for packet {ack_seq_num}")



def main():
    if len(sys.argv) != 5:
        print("Usage: python server.py <packet_size> <protocol_name> <window_size> <timeout>")
        return

    packet_size = int(sys.argv[1])
    protocol_name = sys.argv[2]
    window_size = int(sys.argv[3])
    timeout = float(sys.argv[4])

    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print("UDP server started")
    
    while True:
        data, addr = sock.recvfrom(1024)
        print(addr)
        if protocol_name == 'SW':
            stop_and_wait(sock, 'loco.jpg', packet_size, addr, timeout=timeout)
        elif protocol_name == 'GBN':
            go_back_n(sock, 'loco.jpg', packet_size, window_size, addr, timeout=timeout)
        elif protocol_name == 'SR':
            selective_repeat(sock, 'loco.jpg', packet_size, window_size, addr, timeout=timeout)
        else:
            print("Invalid protocol name:", protocol_name)
            break

    print('Socket closed')

if __name__ == "__main__":
    main()
