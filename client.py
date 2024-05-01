# import socket

# def main():
#     UDP_IP = "127.0.0.1"
#     UDP_PORT = 5005
#     MESSAGE = "SW"  # Change to 'GBN' or 'SR' for different protocols
    
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
#     sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
    
#     if MESSAGE == 'SW' or MESSAGE == 'GBN' or MESSAGE == 'SR':
#         received_data = b""
#         count = 0
#         while True:
#             data, addr = sock.recvfrom(1024)
#             if data == b'SERVER_CLOSED':
#                 break
#             received_data += data
#             count += 1
#             print(count)    
#             sock.sendto(b'ACK', addr)
        
#         with open('received_loco.jpg', 'wb') as file:
#             file.write(received_data)
        
#         print("File received successfully")

#     sock.close()

# if __name__ == "__main__":
#     main()

import socket

def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    MESSAGE = "SW"  # Change to 'GBN' or 'SR' for different protocols
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
    
    if MESSAGE == 'SW' or MESSAGE == 'GBN' or MESSAGE == 'SR':
        count = 0
        with open('received_loco.jpg', 'wb') as file:
            while True:
                data, addr = sock.recvfrom(25600)
                if data == b'SERVER_CLOSED':
                    break
                count += 1
                print(count)
                file.write(data)
                sock.sendto(b'ACK', addr)
        
        print("File received successfully")

    sock.close()

if __name__ == "__main__":
    main()
