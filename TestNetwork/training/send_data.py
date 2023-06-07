import socket
import netifaces

# Port
PORT = 15000

# Tên tệp để gửi
FILE_NAME = "*.h5"

# Xác định địa chỉ broadcast
interfaces = netifaces.interfaces()
broadcast_address = None

for interface in interfaces:
    addresses = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addresses:
        inet_addresses = addresses[netifaces.AF_INET]
        for inet_address in inet_addresses:
            if 'broadcast' in inet_address:
                broadcast_address = inet_address['broadcast']
                break
    if broadcast_address:
        break

if not broadcast_address:
    print("Không tìm thấy địa chỉ broadcast cho mạng của bạn.")
    exit()

# Gửi tệp
with open(FILE_NAME, "rb") as file:
    data = file.read()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(data, (broadcast_address, PORT))
sock.close()
