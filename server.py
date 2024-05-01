import socket
import time
import os
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

def send_packets(sock, packets, addr):
    for packet in packets:
        sock.sendto(packet, addr)
        time.sleep(0.1)  # Simulating network delay

def stop_and_wait(sock, filename, packet_size, addr):
    packet_gen = PacketGenerator(filename, packet_size)
    packets = packet_gen.generate_packets()
    
    for packet in packets:
        sock.sendto(packet, addr)
        # time.sleep(0.1)  # Simulating network delay
        ack, _ = sock.recvfrom(1024)
        if ack.decode() != 'ACK':
            print("Error: Packet lost, retransmitting...")
            sock.sendto(packet, addr)
            # time.sleep(0.1)  # Simulating network delay
        else:
            print("Packet ACKed")

    sock.sendto(b'SERVER_CLOSED', addr)
    print("Server closed")
    sock.close()


def go_back_n(sock, filename, packet_size, window_size, addr):
    packet_gen = PacketGenerator(filename, packet_size)
    packets = packet_gen.generate_packets()
    
    seq_num = 0
    while seq_num < len(packets):
        for i in range(seq_num, min(seq_num + window_size, len(packets))):
            sock.sendto(packets[i], addr)
            time.sleep(0.1)  # Simulating network delay
        
        ack_received = False
        while not ack_received:
            ack, _ = sock.recvfrom(1024)
            ack_seq_num = int(ack.decode())
            if ack_seq_num == seq_num:
                print(f"Packet {seq_num} ACKed")
                seq_num += 1
            else:
                print(f"Received ACK for packet {ack_seq_num}, expected {seq_num}")

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
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print("UDP server started")
    
    file_size = os.path.getsize('loco.jpg')
    print("File size:", file_size, "bytes")

    while True:
        data, addr = sock.recvfrom(1024)
        print(addr)
        stop_and_wait(sock, 'loco.jpg', 25600, addr)
        break
        # if data.decode() == 'SW':
        #     stop_and_wait(sock, 'loco.jpg', 1024, addr)  # Adjust packet size as needed
        # elif data.decode() == 'GBN':
        #     go_back_n(sock, 'loco.jpg', 1024, 5, addr)  # Adjust window size as needed
        # elif data.decode() == 'SR':
        #     selective_repeat(sock, 'loco.jpg', 1024, 5, addr)  # Adjust window size as needed
        # elif data.decode() == 'exit':
        #     break
   
    # sock.close()
    print('socket closed')

if __name__ == "__main__":
    main()