import os
import sys
import datetime
import json
import random

from utils.fileUtils import copyFile, getFileSize
from utils.dataUtils import data2Json

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtWidgets, QtGui
from view.homepage import Ui_HomePage
from view.addContactPage import Ui_AddContactPage
from view.loginPage import Ui_LoginPage
from view.registerPage import Ui_RegisterPage
from view.personnalInfoPage import Ui_PersonalInfoPage
from mySocket.clientSocket import ClientSocket
from myThread.clientThread import ClientThread
from mySocket.serverSocket import ServerSocket
from myThread.serverThread import ServerThread
from myDB.MyDB import MyDB


# 主界面
class HomePage(QMainWindow, Ui_HomePage):

    def __init__(self):
        super(HomePage, self).__init__()
        self.setupUi(self)

        # 登录状态
        self.isLogin = False

        # 用户名
        self.userName = ""

        # 向后端发送数据的socket
        self.clientSocket = None
        # 向后端发送数据的子线程
        self.clientThread = None

        # 从后端接收的socket
        self.serverSocket = None
        # 从后端发送数据的子线程
        self.serverThread = None

        # 消息类型
        self.msgType = "send_strategy"
        # 文件分片方式
        self.divideMethod = 8
        # 文件分片组数
        self.groupNum = 3
        # 数据标识
        self.identification = 1011
        # 数据传输忍受时间
        self.timer = 10000

        # 与后端通信数据
        self.jsonData = None
        # 进度条字典
        self.progress_bar_list = {}
        # 文件传输成功标志字典
        self.succeed_flag_list = {}

        # 初始化子窗口
        self.addContactPage = AddContactPage()
        self.loginPage = LoginPage()
        self.personalInfoPage = PersonalInfoPage()

        # 对应事件
        self.addContactButton.clicked.connect(self.addContactButtonClicked)
        self.addContactPage.contactSignal.connect(self.addContactItem)
        self.loginPage.loginSignal.connect(self.getLoginInfo)
        self.fileButton.clicked.connect(self.openFile)
        self.contactList.itemClicked.connect(self.onContactItemClicked)
        self.sendButton.clicked.connect(self.sendMsg)
        self.loginButton.clicked.connect(self.showLoginPage)
        self.personalInfoButton.clicked.connect(self.showPersonalInfoPage)

    # 接收文件显示进度
    def showTransferProgress(self, data):
        jsonData = json.loads(data)
        msgType = jsonData['MsgType']
        index = jsonData['Identification']

        value = jsonData['Percentage']
        if msgType == 'sendProgress':  # 发送进度
            self.progress_bar_list[index].setValue(value)
            if value >= 100:
                self.progress_bar_list[index].hide()
                self.succeed_flag_list[index].setText("发送成功！")
                self.succeed_flag_list[index].show()
                self.progress_bar_list[index].setValue(0)
            else:
                self.progress_bar_list[index].show()
        elif msgType == 'receiveProgress':  # 接收进度
            if index not in self.progress_bar_list.keys():
                senderName = jsonData['SenderName']
                fileName = jsonData['FileName']
                size, fileSize = getFileSize(None, jsonData['FileDataLength'])
                self.addMsgItem(1, index, 1, senderName, None, fileName, fileSize)
                self.progress_bar_list[index].setValue(value)
            if index in self.progress_bar_list.keys():
                self.progress_bar_list[index].setValue(value)
                if value >= 100:
                    self.progress_bar_list[index].hide()
                    self.succeed_flag_list[index].setText("接收成功！")
                    self.succeed_flag_list[index].show()
                    self.progress_bar_list[index].setValue(0)
                else:
                    self.progress_bar_list[index].show()

    # 打开个人信息界面
    def showPersonalInfoPage(self):
        self.personalInfoPage.show()

    # 打开登录页面
    def showLoginPage(self):
        self.loginPage.show()

    # 打开添加联系人页面
    def addContactButtonClicked(self):
        if self.isLogin:
            self.addContactPage.show()

    # 获取登录信息
    def getLoginInfo(self, userName, isLogin):
        try:
            # # 初始化与后端连接的发送socket
            # self.clientSocket = ClientSocket()
            #
            # # 创建发送线程
            # self.clientThread = ClientThread(1, self.clientSocket)
            # self.clientThread.recv_json_data.connect(self.progress_data_changed)
            # self.clientThread.start()

            # 初始化接收socket
            self.serverSocket = ServerSocket()

            # 创建接收线程
            self.serverThread = ServerThread(2, self.serverSocket)
            self.serverThread.recv_json_data.connect(self.showTransferProgress)
            self.serverThread.start()

        except IOError:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, '提示', '服务未启动!')
            msg_box.exec_()
        else:
            self.userName = userName
            self.personalInfoPage.usernameLabel.setText(userName)
            self.setWindowTitle(userName)
            self.isLogin = isLogin
            self.loginPage.userNameInput.setText("")
            self.loginPage.passwordInput.setText("")
            self.addContactPage.username = userName
            if isLogin:
                myDB = MyDB()
                allFriends = myDB.queryAllFriends(userName)
                for friendInfo in allFriends:
                    self.addContactItem(friendInfo[1])
                myDB.close()

    # 增加联系人列表项
    def addContactItem(self, account):
        self.contactList.setIconSize(QtCore.QSize(50, 50))
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(205, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        item.setText(account)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/profile.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        self.contactList.addItem(item)

    # 打开文件选择器
    def openFile(self):
        if not self.chattingUserName.text() == "":
            filePath, fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(),
                                                                       "所有文件(*);;图片(*.jpg *.png)")
            # try:
            #     # 初始化与后端连接的发送socket
            #     self.clientSocket = ClientSocket()
            # except IOError:
            #     print("与后端连接失败！")
            #     return
            #
            # # 创建发送线程
            # self.clientThread = ClientThread(1, self.clientSocket)
            # self.clientThread.recv_json_data.connect(self.progress_data_changed)
            # self.clientThread.start()

            if (not filePath == "") and os.path.exists(filePath):
                file_name_list = filePath.split('/')
                file_name = file_name_list[-1]
                file_size, file_size_unit = getFileSize(filePath, None)
                self.identification = random.randint(0, 2147483647)
                self.jsonData = data2Json(self.msgType,
                                          self.userName,
                                          self.chattingUserName.text(),
                                            "./待发送/" + file_name,
                                            file_size,
                                          self.divideMethod,
                                          self.groupNum,
                                          self.identification,
                                            self.timer)
                print(self.jsonData)
                self.addMsgItem(0, self.identification, 1, self.userName, None, file_name, file_size_unit)
                # self.clientSocket.send_msg(self.jsonData)

    # 联系人列表点击事件
    def onContactItemClicked(self):
        items = self.contactList.selectedItems()
        for item in items:
            user = item.text()
            msgItem = QtWidgets.QListWidgetItem()
            msgItem.setSizeHint(QtCore.QSize(200, 80))
            self.chattingUserName.setText(user)
            # self.msgList.clear()

    # 发送消息
    def sendMsg(self):
        msg = self.editMsgWindow.toPlainText()
        if not (self.editMsgWindow.toPlainText() == "" or self.chattingUserName.text() == ""):
            self.editMsgWindow.setText("")
            self.addMsgItem(0, None, 0, self.userName, msg, None, None)
            self.clientSocket.sendMsg(msg)

    # 增加消息项
    def addMsgItem(self, userType, index, msgType, userName, msg, fileName, fileSize):
        currentTime = datetime.datetime.now()
        timeStr = datetime.datetime.strftime(currentTime, '%Y-%m-%d %H:%M:%S')
        item = QtWidgets.QListWidgetItem()
        item_widget = QtWidgets.QWidget()
        timeLabel = QtWidgets.QLabel()
        timeLabel.setText(timeStr)
        timeLabel.setStyleSheet("*{"
                                "   color: green;"
                                "}")
        userNameLabel = QtWidgets.QLabel()
        userNameLabel.setText(userName)
        if userType == 0:  # 本用户名为蓝色
            userNameLabel.setStyleSheet("*{"
                                        "   color: blue;"
                                        "}")
        else:  # 其他用户名为红色
            userNameLabel.setStyleSheet("*{"
                                        "   color: red;"
                                        "}")
        if msgType == 0:
            msgBrowser = QtWidgets.QTextBrowser()
            msgBrowser.setText(msg)
            msgBrowser.setStyleSheet("*{"
                                     "  border-style:none;"
                                     "  background-color:#f5f5f5;"
                                     "}")
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(timeLabel)
            vbox.addWidget(userNameLabel)
            vbox.addWidget(msgBrowser)
            vbox.setAlignment(QtCore.Qt.AlignLeft)
            item_widget.setLayout(vbox)
        elif msgType == 1:
            vbox = QtWidgets.QVBoxLayout()
            file_name = QtWidgets.QLabel()
            file_name.setText(fileName)
            file_name.setStyleSheet("QLabel{"
                                    " border-bottom:1px solid #000000;"
                                    "}")
            file_size = QtWidgets.QLabel()
            file_size.setText(fileSize)
            vbox.addWidget(file_name)
            vbox.addWidget(file_size)
            vbox.setAlignment(QtCore.Qt.AlignLeft)
            file_info = QtWidgets.QWidget()
            file_info.setLayout(vbox)
            hbox = QtWidgets.QHBoxLayout()
            file_img = QtWidgets.QLabel()
            file_img.setMaximumSize(QtCore.QSize(50, 50))
            file_img.setPixmap(QtGui.QPixmap("images/file.png").scaled(50, 50))
            hbox.addWidget(file_img)
            hbox.addWidget(file_info)
            file_widget = QtWidgets.QWidget()
            file_widget.setLayout(hbox)
            file_widget.setStyleSheet("QWidget{"
                                      " background-color:#66cccc"
                                      "}")
            vbox2 = QtWidgets.QVBoxLayout()
            vbox2.setAlignment(QtCore.Qt.AlignLeft)
            vbox2.addWidget(file_widget)
            # 初始化一个进度条
            progress_bar = QtWidgets.QProgressBar()
            progress_bar.setMaximumSize(QtCore.QSize(200, 10))
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            progress_bar.setStyleSheet("*{background-color:#ffffff}")
            self.progress_bar_list[index] = progress_bar
            vbox2.addWidget(progress_bar)
            flagLabel = QtWidgets.QLabel()
            flagLabel.setStyleSheet("*{color:green}")
            flagLabel.hide()
            self.succeed_flag_list[index] = flagLabel
            vbox2.addWidget(flagLabel)
            info_widget = QtWidgets.QWidget()
            info_widget.setLayout(vbox2)
            vbox3 = QtWidgets.QVBoxLayout()
            vbox3.addWidget(timeLabel)  # 时间
            vbox3.addWidget(userNameLabel)  # 用户名
            vbox3.addWidget(info_widget)  # 文件信息
            vbox3.setAlignment(QtCore.Qt.AlignLeft)
            vbox3.addStretch()
            item_widget.setLayout(vbox3)
            item.setSizeHint(QtCore.QSize(300, 200))
            # self.progress_bar.show()
        self.msgList.addItem(item)
        self.msgList.setItemWidget(item, item_widget)
        self.msgList.scrollToBottom()

    # 主窗口关闭时，子窗口同时关闭
    def closeEvent(self, event):
        if self.clientSocket:
            self.clientSocket.close()
            self.clientThread.exit(0)
        if self.serverThread:
            self.serverSocket.close()
            self.serverThread.exit(0)
        sys.exit(0)


# 添加联系人界面
class AddContactPage(QMainWindow, Ui_AddContactPage):
    # 定义信号
    contactSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(AddContactPage, self).__init__()
        self.setupUi(self)

        # 用户名
        self.username = ""

        # 添加用户事件
        self.addButton.clicked.connect(self.get_info_slot)
        # 添加用户名文件
        self.selectUserButton.clicked.connect(self.selectUserNameFile)
        # 添加公钥文件
        self.selectPublicKeyButton.clicked.connect(self.selectPublicKeyFile)

    # 选择用户名文件
    def selectUserNameFile(self):
        filePath, fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(),
                                                                   "所有文件(*);")
        if filePath.split('/')[-1].split('.')[-1] == "txt":
            with open(filePath, "r") as file:
                username = file.read()
            self.friendUsername.setText(username)
        return

    # 选择公钥文件
    def selectPublicKeyFile(self):
        filePath, fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(),
                                                                   "所有文件(*);")
        self.publicKeyAddr.setText(filePath)
        return

    # 添加按钮回调方法
    def get_info_slot(self):
        publicKeyAddr = self.publicKeyAddr.text()
        publiKeyFileType = publicKeyAddr.split('/')[-1].split('.')[-1]

        if publiKeyFileType == "pem" and self.friendUsername.text() != "" and self.username != "":

            # 添加到数据库
            myDB = MyDB()
            myDB.addFriend(self.username, self.friendUsername.text(), publicKeyAddr, self.notes.text())
            myDB.close()

            copyFile(publicKeyAddr, "./friendsFiles/", "pem")   # 复制好友的公钥文件
            self.contactSignal.emit(self.friendUsername.text())
            self.friendUsername.setText("")
            self.close()
        else:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, '提示', '请选择正确的文件路径！')
            msg_box.exec_()


# 登录界面
class LoginPage(QMainWindow, Ui_LoginPage):
    # 定义信号
    loginSignal = QtCore.pyqtSignal(str, bool)

    def __init__(self):
        super(LoginPage, self).__init__()
        self.setupUi(self)

        self.registerPage = RegisterPage()
        self.registerButton.clicked.connect(self.show_register_page)
        self.loginButton.clicked.connect(self.login)

    # 打开注册页面
    def show_register_page(self):
        self.registerPage.show()

    # 登录
    def login(self):
        myDB = MyDB()
        userInfo = myDB.queryUser(self.userNameInput.text(), self.passwordInput.text())
        myDB.close()
        print(userInfo)
        if len(userInfo) != 0:  # 登录成功
            self.loginSignal.emit(self.userNameInput.text(), True)
            self.close()
        else:  # 登录失败
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, '提示', '账号密码不匹配！请重新输入。')
            msg_box.exec_()


# 注册界面
class RegisterPage(QMainWindow, Ui_RegisterPage):
    def __init__(self):
        super(RegisterPage, self).__init__()
        self.setupUi(self)

        # 选择用户名文件
        self.selectUserButton.clicked.connect(self.selectUsernameFile)
        # 选择公钥文件
        self.selectPublicKeyButton.clicked.connect(self.selectPublicKeyFile)
        # 选择私钥文件
        self.selectPrivateKeyButton.clicked.connect(self.selectPrivateKeyFile)
        # 选择密码文件 TODO

        # 注册事件
        self.registerButton.clicked.connect(self.register)

    # 注册响应
    def register(self):
        # userNameAddr = self.userName.text()
        publicKeyAddr = self.publicKeyAddr.text()
        privateKeyAddr = self.privateKeyAddr.text()
        password = self.password.text()
        publicKeyFileType = publicKeyAddr.split('/')[-1].split('.')[-1]
        privateKeyFileType = privateKeyAddr.split('/')[-1].split('.')[-1]

        if self.userName.text() != "" and publicKeyFileType == "pem" \
                and privateKeyFileType == "key" and self.password.text() != "":
            # copyFile(userNameAddr, "./myFiles/", "txt")
            copyFile(publicKeyAddr, "./myFiles/", "pem")    # 复制自己的公钥文件
            copyFile(privateKeyAddr, "./myFiles/", "key")   # 复制自己的私钥文件

            # 存入数据库
            myDB = MyDB()
            myDB.addUser(self.userName.text(), publicKeyAddr, privateKeyAddr, password)
            myDB.close()

            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, '提示', '注册成功')
            msg_box.exec_()
            self.hide()
        else:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, '提示', '无法注册，请将信息填写正确!')
            msg_box.exec_()

    # 选择用户名所在文件
    def selectUsernameFile(self):
        filePath, fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(),
                                                                   "所有文件(*);")
        if filePath.split('/')[-1].split('.')[-1] == "txt":
            with open(filePath, "r") as file:
                username = file.read()
            self.userName.setText(username)
        return

    # 选择公钥所在文件
    def selectPublicKeyFile(self):
        filePath, fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(),
                                                                   "所有文件(*);")
        self.publicKeyAddr.setText(filePath)
        return

    # 选择私钥所在文件
    def selectPrivateKeyFile(self):
        filePath, fileType = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(),
                                                                   "所有文件(*);")
        self.privateKeyAddr.setText(filePath)
        return

    # 选择密码所在文件 TODO


# 个人信息界面
class PersonalInfoPage(QMainWindow, Ui_PersonalInfoPage):
    def __init__(self):
        super(PersonalInfoPage, self).__init__()
        self.setupUi(self)


# 进度条Widget
class ProgressBarWidget(QtWidgets.QProgressBar):

    def __init__(self):
        super(ProgressBarWidget, self).__init__()
        # 声明一个时钟
        self.timer = QtCore.QBasicTimer()
        # 初始化一个进度条
        self.setMaximumSize(QtCore.QSize(200, 10))
        self.setMinimum(0)
        self.setMaximum(100)
        self.setStyleSheet("*{background-color:#ffffff}")
        # 初始化进度值
        self.pv = 0

    # 进度条启动
    def start(self):
        # 开启时钟
        self.timer.start(50, self)

    # 重写计时器槽方法
    def timerEvent(self, e):
        if self.pv >= 100:
            self.timer.stop()
            self.pv = 0
        else:
            self.pv += 1
            self.setValue(self.pv)


if __name__ == '__main__':
    # 创建QApplication类的实例
    app = QApplication(sys.argv)
    # 创建一个窗口
    homepage = HomePage()
    homepage.show()
    # 进入程序的主循环,并通过exit函数确保主循环安全结束
    sys.exit(app.exec_())
