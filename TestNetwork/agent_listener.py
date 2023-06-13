import socket
import subprocess
import os
import time
import pickle

def save_data(file_data, filename = 'received_file.pkl'):
    with open(filename, 'wb') as file:
        file.write(file_data)
    return os.path.abspath(filename)  # Trả về đường dẫn tuyệt đối của file

def read_data(sock, buffer_size = 4096):
    file_data = b'' # khoi tao bytes string de luu du lieu

    while True:
        data = sock.recv(buffer_size)
        if not data:
            break
        file_data += data

    print('received: ' +  str(len(file_data) / (1024 * 1024)) + 'MB')

    return file_data

def agent_program():
    host = socket.gethostname()  # Địa chỉ IP của agent
    port = 5000  # port lắng nghe
    buffer_size = 50000000

    agent_socket = socket.socket()  # tạo một socket object
    agent_socket.bind((host, port))  # gán IP và port cho socket

    agent_socket.listen(1)

    while True:
        conn, address = agent_socket.accept()  # Chấp nhận kết nối từ server
        address = address[0] # 0 la address, 1 la port

        print("Connection from: " + str(address))
        
        file_data = read_data(conn, buffer_size)  # Nhận dữ liệu từ server
        
        if file_data:
            start_t = time.time()

            file_path = save_data(file_data) # Xử lý và lưu file nhận được

            subprocess.run(['python3', 'agent_train.py', file_path, 'output.pkl'])  # local train

            # send back new model weights to server

            client_socket = socket.socket()  # tạo một socket object
            client_socket.connect((address, port))  # Kết nối tới máy chủ
            
            file_name = 'output.pkl'  # Tên file cần gửi

            while (time.time() - start_t) < 20:
                pass # doi x giay truoc khi gui de dam bao server da chuyen sang che do lang nghe

            try:
                with open(file_name, 'rb') as file:
                    client_socket.send(file.read())  # Gửi file
            except:
                print('Error sending weights to server!')

            client_socket.close()  # Đóng kết nối

        conn.close()  # Đóng kết nối

    agent_socket.close()  # Đóng socket

if __name__ == '__main__':
    agent_program()


