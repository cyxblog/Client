import os


def copyFile(filePath, savePath, fileType):
    fileName = filePath.split('/')[-1]
    if fileName.split('.')[-1] == fileType:
        with open(filePath, "rb") as readFile:
            data = readFile.read()
        with open(savePath + fileName, "wb") as saveFile:
            saveFile.write(data)
    return


# 获得文件大小
def getFileSize(filePath, length):
    if filePath is None:
        size = length
    else:
        size = os.path.getsize(filePath)
    if size >= 1024 * 1024 * 1024:
        size_unit = str(round(size / (1024 * 1024 * 1024), 2)) + "GB"
    elif size >= 1024 * 1024:
        size_unit = str(round(size / (1024 * 1024), 2)) + "MB"
    elif size >= 1024:
        size_unit = str(round(size / 1024, 2)) + "KB"
    else:
        size_unit = str(size) + "B"
    return size, size_unit
