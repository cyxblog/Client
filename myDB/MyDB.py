import sqlite3


class MyDB:
    def __init__(self):
        self.conn = sqlite3.connect('./myDB/client.db')
        self.cur = self.conn.cursor()

        try:
            # 用户表
            createUserTableSQL = '''CREATE TABLE IF NOT EXISTS user
                                (username TEXT,
                                publicKeyAddr TEXT,
                                privateKeyAddr TEXT,
                                password TEXT);'''
            self.cur.execute(createUserTableSQL)
            # 好友表
            createFriendsTableSQL = '''CREATE TABLE IF NOT EXISTS friends
                                    (username TEXT,
                                    friendName TEXT,
                                    publicKeyAddr TEXT,
                                    notes TEXT);'''
            self.cur.execute(createFriendsTableSQL)
            self.conn.commit()
        except:
            pass

    # 添加注册用户
    def addUser(self, username, publicKeyAddr, privateKeyAddr, password):
        addUserSQL = "INSERT INTO user VALUES('" + username + "','" + publicKeyAddr + "','" \
                     + privateKeyAddr + "','" + password + "')"
        print(addUserSQL)
        self.cur.execute(addUserSQL)
        self.conn.commit()

    # 添加好友
    def addFriend(self, username, friendName, publicKeyAddr, notes):
        addFriendSQL = "INSERT INTO friends VALUES('" + username + "','" + friendName + "','" \
                       + publicKeyAddr + "','" + notes + "')"
        self.cur.execute(addFriendSQL)
        self.conn.commit()

    # 删除好友
    def deleteFriend(self, username):
        deleteFriendSQL = "DELETE FROM friends WHERE username=" + username
        self.cur.execute(deleteFriendSQL)
        self.conn.commit()

    # TODO
    def update(self):
        pass

    # 查询用户
    def queryUser(self, username, password):
        queryUserSQL = "SELECT * FROM user WHERE username='" + username + "'" \
                        + " and password='" + password + "'"
        self.cur.execute(queryUserSQL)
        data = self.cur.fetchall()
        return data

    # 查询所有好友
    def queryAllFriends(self, username):
        queryUserSQL = "SELECT * FROM friends WHERE username='" + username + "'"
        self.cur.execute(queryUserSQL)
        data = self.cur.fetchall()
        return data

    # 关闭连接和游标
    def close(self):
        self.cur.close()
        self.conn.close()
