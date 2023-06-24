FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
    openssh-server \
    vim \
    net-tools \
    iputils-ping \
    curl \
    python3 \
    python3-pip

RUN mkdir /var/run/sshd
RUN echo 'root:21521955' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Cài đặt các thư viện Python
RUN pip3 install numpy matplotlib scikit-learn tensorflow keras opencv-python-headless jupyter netifaces

# Tạo thư mục "training" và sao chép các tệp tin vào container
RUN mkdir /training
COPY ./training/send_data.py /training/send_data.py
COPY ./training/get_data.py /training/get_data.py
COPY ./training/send_ckks_key.py /training/send_ckks_key.py
COPY ./training/get_ckks_key.py /training/get_ckks_key.py

# Thiết lập quyền thực thi cho các tệp tin
RUN chmod +x /training/send_data.py
RUN chmod +x /training/get_data.py
RUN chmod +x /training/send_ckks_key.py
RUN chmod +x /training/get_ckks_key.py

EXPOSE 5000 12345 22 8888

RUN pip3 install tenseal
#RUN pip3 install flask
#RUN pip3 install requests

CMD ["/usr/sbin/sshd", "-D"]
#CMD ["python3", "blockchain.py", "--port", "5000"]