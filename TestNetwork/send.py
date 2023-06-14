import socket

def client_program():
    print("Nhap ip node nhan:")
    host = input()  # IP của máy chủ
    port = 5000  # port của máy chủ

    client_socket = socket.socket()  # tạo một socket object
    client_socket.connect((host, port))  # Kết nối tới máy chủ

    file_name = 'send_file.txt'  # Tên file cần gửi
    with open(file_name, 'rb') as file:
        client_socket.send(file.read())  # Gửi file

    client_socket.close()  # Đóng kết nối

if __name__ == '__main__':
    client_program()



