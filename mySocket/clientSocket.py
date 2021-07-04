import socket


class ClientSocket:
    def __init__(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '192.168.137.24'
        port = 8882  # alice:8882 bob:8884
        self.clientSocket.connect((host, port))

    def send_msg(self, msg):
        self.clientSocket.send(msg.encode('utf-8'))

    def recv_msg(self):
        data = self.clientSocket.recv(1024).decode('utf-8')
        return data

    def close(self):
        self.clientSocket.close()
