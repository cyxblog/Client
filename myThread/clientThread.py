import threading
import time
from PyQt5 import QtCore


class ClientThread(QtCore.QThread):
    # 定义进度条数值信号
    recv_json_data = QtCore.pyqtSignal(str)

    def __init__(self, threadId, socket):
        super(ClientThread, self).__init__()
        self.threadId = threadId
        self.socket = socket

    def run(self):
        # self.setPriority(QtCore.QThread.HighPriority)
        while True:
            data = self.recv_data(self.socket)
            dataLength = len(data)
            if dataLength == 0:
                break
            print(str(self.threadId) + " Thread:" + str(data))
        self.socket.close()

    def recv_data(self, socket):
        data = socket.recv_msg()
        if len(str(data)) != 0:
            self.recv_json_data.emit(data)
        return data
