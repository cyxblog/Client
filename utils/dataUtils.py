import json


def data2Json(msgType, senderName, receiverName, filePath, fileLength,
                  divideMethod, groupNum, identification, timer):
    jsonData = {'DivideMethod': divideMethod,  # 分片方式
                'FileDataLength': fileLength,  # 文件长度
                'GroupNum': groupNum,  # 分片有多少组
                'Identification': identification,  # 标识
                'MsgType': msgType,  # 消息类型
                'ReceiverName': receiverName,  # 接收方代号
                'SenderName': senderName,  # 发送方代号
                'SrcFilePath': filePath,  # 文件路径
                'Timer': timer}  # 能接受的最长等待时间
    return json.dumps(jsonData)