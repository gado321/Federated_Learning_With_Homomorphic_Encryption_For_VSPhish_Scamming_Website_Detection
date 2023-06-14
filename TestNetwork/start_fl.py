import socket
import subprocess
import os
import time
import pickle
import numpy as np
from itertools import zip_longest
import threading

def read_data(sock, buffer_size = 4096):
    file_data = b'' # khoi tao bytes string de luu du lieu
    
    while True:
        data = sock.recv(buffer_size)
        if not data:
            break
        file_data += data

    print('received: ' +  str(len(file_data) / (1024 * 1024)) + 'MB')

    return file_data

def avg_recursive(*arrays):
    if all(isinstance(arr, list) for arr in arrays):
        return [avg_recursive(*values) for values in zip_longest(*arrays, fillvalue=0)]
    else:
        # fedavg here
        sum = 0
        for i in arrays:
            sum += i
        return sum / len(arrays)

def save_data(file_data, filename):
    with open(filename, 'wb') as file:
        file.write(file_data)
    return os.path.abspath(filename)  # Trả về đường dẫn tuyệt đối của file

def thread_sendFile(sock, filename):
    with open(filename, 'rb') as file:
        sock.send(file.read())  # Gửi file

    sock.close()  # Đóng kết nối

def thread_receiveFile(sock, buffer_size, repliesCnt, start_t):
    
    file_data = read_data(sock, buffer_size)  # Nhận dữ liệu từ cac agents
    
    if file_data:
        file_path = save_data(file_data, str(repliesCnt) + ".pkl")

        print(str(time.time() - start_t))
    sock.close()  # Đóng kết nối

def server_program():
    #print("Nhap so luong round can train:")
    #rounds = int(input())
    rounds = 2
    #print("Nhap so luong agent tham gia train:")
    #numOfAgents = int(input())
    numOfAgents = 3
    port = 5000  # port cua cac agent
    agentsIP = ['192.168.1.2', '192.168.1.3', '192.168.1.4']
    buffer_size = 50000000 #~20MB


    '''for i in range(numOfAgents):
        print("Nhap ip agent " + str(i) + " :")
        host = input()  # IP của agent
        agentsIP.append(host)'''

    # Khoi tao model weights ban dau
    filename = 'weights.pkl'
    subprocess.run(['python3', 'create_model_weights.py', filename])


    for round in range(rounds):
        print("round #" + str(round))
        for i in range(numOfAgents):
            print("agent #" + str(i))
            client_socket = socket.socket()  # tạo một socket object
            client_socket.connect((agentsIP[i], port))  # Kết nối tới agents

            sendFile_thread = threading.Thread(target = thread_sendFile, args = (client_socket, filename))
            sendFile_thread.start()
        # lang nghe ket noi de nhan lai model tu cac agent
        server_socket = socket.socket()  # tạo một socket object
        server_socket.bind((socket.gethostname(), port))  # gán IP và port cho socket

        server_socket.listen(1)

        repliesCnt = 0

        start_t = time.time()

        while True: # round time = local training time + file sending time + epsilon
            # Can phai xu ly de neu 1 message lost van co the hoat dong, vi neu khong no se loop mai mai
            # Can set thoi gian toi da
            conn, address = server_socket.accept()  # Chấp nhận kết nối từ cac agents
            address = address[0] # 0 la ip address, 1 la port
            print("Connection from: " + str(address))
            repliesCnt += 1

            receiveFile_thread = threading.Thread(target = thread_receiveFile, args = (conn, buffer_size, repliesCnt, time.time()))
            receiveFile_thread.start()
            if (repliesCnt == numOfAgents):
                break
        print('Accept connections done!')
        start_t = time.time()
        while (time.time() - start_t) < 120:
            pass

        print('Receive weights done!')
        # Load weights
        agentsWeights = []
        for i in range(numOfAgents):
            try:
                with open(str(i + 1) + '.pkl', 'rb') as file:
                    agentsWeights.append(pickle.load(file))
            except:
                print("Cannot load file " + str(i) + ".pkl")
        
        numOfAgents = min(numOfAgents, len(agentsWeights)) # Set lai so luong agents weights thuc te nhan duoc
        print('Actual agent quantity: ' + str(numOfAgents))
        # FedAvg
        # update global model with mean of weights
        avg_weights = avg_recursive(*agentsWeights)  # append the average weights

        # save aggreated weights

        with open(filename, 'wb') as file:
            pickle.dump(avg_weights, file)
        
        server_socket.close()
if __name__ == '__main__':
    server_program()



