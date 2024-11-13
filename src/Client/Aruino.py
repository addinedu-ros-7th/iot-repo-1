import sys
import cv2
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
# import mysql.connector
from datetime import datetime
# import time
# import threading
import socket
import numpy as np
import time
import base64

socket_thread_flag = True
form_class = uic.loadUiType("Main.ui")[0]
form_cam_Class = uic.loadUiType("Cam.ui")[0]

server_address = "192.168.2.29"
server_port = 8081

class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0, parent=None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        self.count = 0
        while self.running == True:
            self.update.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False

class WindowClass(QMainWindow, form_class):  # GUI 클래스
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setIcon()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.timeout.connect(self.fetchSyncData)
        self.timer.start(1000) # 1000ms = 1s

        self.updateTime()

        messages = []
        messages.append("Client First Init")
        messages.append("1")

        response = self.requestTCP(messages)
        response = response.split("&&")
        self.name = response[1]
        self.age = response[2]
        print("request :", response)
        self.initUI()
        
    def initUI(self):
        self.btnCameraPage.clicked.connect(self.cameraPage)
        self.btnSetting.clicked.connect(self.settingPage)
        self.btnGpsPage.clicked.connect(self.gpsPage)
        self.btnPlayPage.clicked.connect(self.playPage)

        self.btnFeed.clicked.connect(self.feeding)

        self.labelFood.hide()

        self.labelName.setText(self.name)
        self.labelAge.setText(self.age)

    def sendTCP(self, messages):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
        client_socket.close()

    def requestTCP(self, messages):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        # print("response :", response)
        client_socket.close()
        return response
    
    def fetchSyncData(self):
        self.response = self.requestTCP(["Sync Data"])
        # print("request :", self.response)
        response = self.response.split("&&")
        if response[0] == "Sync Data":
            temp = response[2]
            humidity = response[1]

        # print("temperature :", temp, "humidity :", humidity)

    def fetchPulse(self):
        try:
            self.remote
            self.cur = self.remote.cursor(buffered=True)
            self.labelPulse.setText("00")
        except:
            self.labelPulse.setText("--")

    def updateTime(self):
        self.now = datetime.now().strftime('%Y년 %m월 %d일  %H : %M : %S  ')
        self.labelDateTime.setText(self.now)

    def setIcon(self):
        self.btnCameraPage.setIcon(QIcon("../../data/icon/webcam.png"))
        self.btnCameraPage.setIconSize(QSize(50, 50))
        self.btnPlayPage.setIcon(QIcon("../../data/icon/ball.png"))
        self.btnPlayPage.setIconSize(QSize(50, 50))
        self.btnGpsPage.setFont(QFont("ubuntu", 25, weight=QFont.Bold))
        self.btnGpsPage.setText("GPS")
        self.btnSetting.setIcon(QIcon("../../data/icon/setting.png"))

        self.labelDog.setPixmap(QPixmap("../../data/icon/dog-sit.png"))
        self.labelDog.setStyleSheet("background-color: transparent;")

        self.btnFeed.setIcon(QIcon("../../data/icon/pet-food.png"))
        self.btnHeart.setIcon(QIcon("../../data/icon/heart.png"))

        self.labelFood.setPixmap(QPixmap("../../data/icon/pet-food-filling.png"))
        self.labelFoodEmpty.setPixmap(QPixmap("../../data/icon/pet-bowl.png"))
        self.labelWater.setPixmap(QPixmap("../../data/icon/water-bowl.png"))
        
        self.labelPulseIcon.setPixmap(QPixmap("../../data/icon/pulse.png"))
        self.labelPawIcon.setPixmap(QPixmap("../../data/icon/paws.png"))
        self.labelPawIcon2.setPixmap(QPixmap("../../data/icon/paws.png"))

    def feeding(self):
        self.labelFoodEmpty.hide()
        self.labelFood.show()

    def cameraPage(self):
        self.hide()
        self.cam = CamWindowClass(self)
        # self.cam.exec()
        self.cam.show()

    def gpsPage(self):
        pass

    def playPage(self):
        pass

    def settingPage(self):
        pass

class CamWindowClass(QMainWindow, form_cam_Class):
    def __init__(self, windowClass, ):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.setIcon()
        self.windowClass = windowClass

        self.isCameraOn = False
        self.camera = Camera(self)
        self.camera.daemon = True

        self.camera.update.connect(self.updateCamera)
        self.isCameraOn = True
        self.camera.running = True
        self.camera.start()

    def initUI(self):
        self.btnMainPage.clicked.connect(self.mainPage)

        self.pixmap = QPixmap()
        self.labelCamera.setPixmap(self.pixmap)

        self.btnRight.setCheckable(True)
        self.btnDown.setCheckable(True)
        self.btnUp.setCheckable(True)
        self.btnLeft.setCheckable(True)

        self.btnRight.pressed.connect(lambda : self.cameraMove("right"))
        self.btnDown.pressed.connect(lambda : self.cameraMove("down"))
        self.btnUp.pressed.connect(lambda : self.cameraMove("up"))
        self.btnLeft.pressed.connect(lambda : self.cameraMove("left"))

        self.btnRight.released.connect(lambda : self.cameraStop("right"))
        self.btnDown.released.connect(lambda : self.cameraStop("down"))
        self.btnUp.released.connect(lambda : self.cameraStop("up"))
        self.btnLeft.released.connect(lambda : self.cameraStop("left"))

        self.btnGood.clicked.connect(lambda : self.sendSound("good"))
        self.btnComeOn.clicked.connect(lambda : self.sendSound("comeon"))

    def setIcon(self):
        self.btnMainPage.setIcon(QIcon("../../data/icon/home.png"))
        self.btnRight.setIcon(QIcon("../../data/icon/arrow-right.png"))
        self.btnDown.setIcon(QIcon("../../data/icon/arrow-down.png"))
        self.btnUp.setIcon(QIcon("../../data/icon/right-arrow.png"))
        self.btnLeft.setIcon(QIcon("../../data/icon/play.png"))
        self.btnFeed.setIcon(QIcon("../../data/icon/pet-food.png"))
        self.btnPlay.setIcon(QIcon("../../data/icon/ball.png"))
               
        self.labelPulseIcon.setPixmap(QPixmap("../../data/icon/pulse.png"))
    
    def sendSound(self, key):
        self.sound = QSoundEffect()
        match(key):
            case "good":
                self.sound.setSource(QUrl.fromLocalFile("../../data/sound/dog-barking-twice.wav"))
            case "comeon":
                self.sound.setSource(QUrl.fromLocalFile("../../data/sound/meow.wav"))
        self.sound.play()

    def cameraMove(self, key):
        messages = []
        messages.append("WebCam Control")  # key
        messages.append(key)    # value
        messages.append("start")

        self.sendTCP(messages)

    def cameraStop(self, key):
        messages = []
        messages.append("WebCam Control")  # key
        messages.append(key)    # value
        messages.append("stop")

        self.sendTCP(messages)

    def sendTCP(self, messages):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
        client_socket.close()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf
    
    def requestTCP(self, messages, iscamera=False):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))

        if not iscamera:
            response = client_socket.recv(1024).decode('utf-8')
            client_socket.close()
            return response
        else:
            length = self.recvall(client_socket, 64)
            length1 = length.decode('utf-8')
            stringData = self.recvall(client_socket, int(length1))
            stime = self.recvall(client_socket, 64)
            # print('camera send time: ' + stime.decode('utf-8'))
            # now = time.localtime()
            # print('receive time: ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
            data = np.frombuffer(base64.b64decode(stringData), np.uint8)
            decimg = cv2.imdecode(data, 1)
            return decimg

    def updateCamera(self):
        image = self.requestTCP(["Request WebCam Image"], iscamera=True)
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)
        self.pixmap = self.pixmap.fromImage(qimage)
        self.labelCamera.setPixmap(self.pixmap)

    def mainPage(self):
        self.hide()
        self.main = WindowClass()
        self.main.show()
        self.isCameraOn = False
        self.camera.stop()

def receiveTCPEvent(client_socket, windowClass):
    while socket_thread_flag == True:
        data = client_socket.recv(1024).decode('utf-8')
        print(data)

if __name__ == "__main__":
    app = QApplication(sys.argv)     
    myWindows = WindowClass()   
    myWindows.show()
    sys.exit(app.exec_())