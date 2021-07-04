import socket


class ServerSocket:
    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '0.0.0.0'
        port = 8881  # alice:8881 bob:8883
        self.serverSocket.bind((host, port))
        self.serverSocket.listen(5)

    def accept(self):
        print("等待连接...")
        client, address = self.serverSocket.accept()
        return client, address

    def close(self):
        self.serverSocket.close()
