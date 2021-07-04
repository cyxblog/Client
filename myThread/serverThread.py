import time

from PyQt5 import QtCore


class ServerThread(QtCore.QThread):
    # 定义进度条数值信号
    recv_json_data = QtCore.pyqtSignal(str)

    def __init__(self, threadId, socket):
        super(ServerThread, self).__init__()
        self.threadId = threadId
        self.socket = socket

    def run(self):
        while True:
            client, address = self.socket.accept()
            print("%s:%d接入" % (address[0], address[1]))
            jsonData = client.recv(1024).decode('utf-8')
            print(str(self.threadId) + " Thread:" + str(jsonData))
            self.recv_json_data.emit(jsonData)
            client.close()
