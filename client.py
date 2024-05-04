import socket
import time

def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    MESSAGE = 'GBN'  # Change to 'GBN' or 'SR' for different protocols
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    start_time = time.time()  # Record the start time
    
    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
    
    if MESSAGE == 'SW':
        count = 0
        with open('received_loco.jpg', 'wb') as file:
            while True:
                data, addr = sock.recvfrom(25600)
                if data == b'SERVER_CLOSED':
                    break
                count += 1
                print(count)
                file.write(data)
                if(count==2):
                    time.sleep(0.05)
                sock.sendto(b'ACK', addr)
        
        print("File received successfully")

    if MESSAGE == 'GBN' or MESSAGE == 'SR':
        with open('received_loco.jpg', 'wb') as file:
            base = 0
            next_seq_num = 0
            while True:
                data, addr = sock.recvfrom(3*25600) # window size * packet size
                if data == b'SERVER_CLOSED':
                    break
                seq_num = int(data[:4].decode())  # Extract sequence number
                packet_data = data[4:]  # Extract packet data
                
                if seq_num == next_seq_num:
                    file.write(packet_data)
                    print(f"Received packet {seq_num}")
                    sock.sendto(str(seq_num).encode(), addr)  # Send ACK with sequence number
                    next_seq_num += 1
                else:
                    print(f"Ignoring duplicate or out-of-order packet {seq_num}")
        
        print("File received successfully")

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

    sock.close()

if __name__ == "__main__":
    main()
