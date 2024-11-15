import sys
import cv2
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from datetime import datetime
import socket
import numpy as np
import time
import base64

socket_thread_flag = True
form_class = uic.loadUiType("Main.ui")[0]
form_cam_Class = uic.loadUiType("Cam.ui")[0]
form_setting_Class = uic.loadUiType("Setting.ui")[0]
form_register_Class = uic.loadUiType("Register.ui")[0]

server_address = "192.168.2.29"
server_port = 8081

def getAge(dateBirth):
    birth = datetime.strptime(dateBirth, '%Y-%m-%d').date()
    today = datetime.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return str(age)

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

        self.setWindowTitle("Aruino - Your Smart Pet Sitter")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.timeout.connect(self.fetchSyncData)
         # 1000ms = 1s

        self.updateTime()
        self.id_flag = False

        self.labelDateTime.hide()
        self.btnUser1.clicked.connect(lambda: self.userSelect(1))
        self.btnUser2.clicked.connect(lambda: self.userSelect(2))
        self.btnUser3.clicked.connect(lambda: self.userSelect(3))
        self.btnUser4.clicked.connect(lambda: self.userSelect(4))
        self.btnRegister.clicked.connect(self.registerPage)

    def userSelect(self, key):
        match(key):
            case 1:
                self.petID = "1"
            case 2:
                self.petID = "2"
            case 3:
                self.petID = "3"
            case 4:
                self.petID = "4"

        self.id_flag = True
        print(self.id_flag)

        self.firstInit()
        self.timer.start(1000)

    def firstInit(self):
        messages = []
        messages.append("Client First Init")
        messages.append(self.petID)

        response = self.requestTCP(messages)
        self.petInfo = response.split("&&")
        self.name = self.petInfo[1]
        self.birth = self.petInfo[2]
        self.weight = self.petInfo[3]
        self.species = self.petInfo[4]
        self.contact_number = self.petInfo[5]
        self.age = getAge(self.birth)
        print("request :", self.petInfo)

        self.feeding_times = []
        for i in range(len(self.petInfo) - 6):
            self.feeding_times.append(self.petInfo[i+6])

        self.initUI()
        if self.species == "cat":
            self.labelDog.setPixmap(QPixmap("../../data/icon/cat.png"))
            self.btnHeart.move(470,300)
            self.btnHeart.setIconSize(QSize(50, 50))
        
    def initUI(self):
        self.labelDateTime.show()

        self.labelInit.hide()
        self.btnUser1.hide()
        self.btnUser2.hide()
        self.btnUser3.hide()
        self.btnUser4.hide()
        self.btnRegister.hide()

        self.btnCameraPage.clicked.connect(self.cameraPage)
        self.btnSetting.clicked.connect(self.settingPage)
        self.btnGpsPage.clicked.connect(self.gpsPage)
        self.btnPlayPage.clicked.connect(self.playPage)

        self.btnFeed.clicked.connect(self.feeding)

        self.labelFood.hide()

        self.labelName.setText(self.name)
        self.labelAge.setText(self.age)
        self.labelNameInfo.hide()
        self.labelAgeInfo.hide()

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
        response = self.requestTCP(["Sync Data"])
        # print("request :", self.response)
        self.response = response.split("&&")
        sync_data = self.response
        if sync_data[0] == "Sync Data":
            temp = sync_data[2]
            humidity = sync_data[1]

            self.labelTemp.setText(temp)
            self.labelHumid.setText(humidity)

    def updateTime(self):
        self.now = datetime.now().strftime('%Y년 %m월 %d일  %H : %M : %S  ')
        self.labelDateTime.setText(self.now)

    def setIcon(self):
        self.btnUser1.setIcon(QIcon("../../data/icon/paws-hollow.png"))
        self.btnUser2.setIcon(QIcon("../../data/icon/paws.png"))
        self.btnUser3.setIcon(QIcon("../../data/icon/paws.png"))
        self.btnUser4.setIcon(QIcon("../../data/icon/paws.png"))

        self.btnCameraPage.setIcon(QIcon("../../data/icon/video.png"))
        self.btnCameraPage.setIconSize(QSize(50, 50))
        self.btnPlayPage.setIcon(QIcon("../../data/icon/file.png"))
        self.btnPlayPage.setIconSize(QSize(50, 50))
        self.btnGpsPage.setFont(QFont("ubuntu", 25, weight=QFont.Bold))
        self.btnGpsPage.setText("GPS")
        self.btnGpsPage.hide()
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
        self.cam.show()

    def gpsPage(self):
        pass

    def playPage(self):
        pass

    def settingPage(self):
        self.setting = SettingWindowClass(self)
        self.setting.show()

    def registerPage(self):
        self.register = RegisterWindowClass(self)
        self.register.frameGeometry().moveCenter(QDesktopWidget().availableGeometry().center())
        self.register.move(self.frameGeometry().topLeft())
        self.register.show()

class SettingWindowClass(QMainWindow, form_setting_Class):
    def __init__(self, windowClass):
        super().__init__()
        self.setupUi(self)

        self.add_1 = True
        self.add_2 = False
        self.add_3 = False
        self.add_4 = False
        self.add_5 = False
        
        self.setWindowTitle("Setting")

        self.windowClass = windowClass # WindowClass()
        self.id_flag = self.windowClass.id_flag
        self.petID = self.windowClass.petID
        # self.petInfo = self.windowClass.petInfo
        
        self.initUI()

    def initUI(self):

        self.btnAdds = [
            self.btnAdd1,
            self.btnAdd2,
            self.btnAdd3,
            self.btnAdd4,
            self.btnAdd5
        ]
        self.timeFeedings = [
            self.timeFeeding1,
            self.timeFeeding2,
            self.timeFeeding3,
            self.timeFeeding4,
            self.timeFeeding5
        ]

        for i in range(5):
            self.btnAdds[i].hide()
            self.timeFeedings[i].hide()
            self.timeFeedings[i].timeChanged.connect(self.setTimeFeeding)


        print(len(self.windowClass.feeding_times))
        if self.windowClass.feeding_times:
            for i, val in enumerate(self.windowClass.feeding_times):
                self.timeFeedings[i].show()
                tmp_li = val.split(":")
                self.timeFeedings[i].setTime(QTime(int(tmp_li[0]), int(tmp_li[1]), int(tmp_li[2])))
                self.btnAdds[i].show()
                self.btnAdds[i].setText("-")
                self.btnAdds[i].disconnect()
                self.btnAdds[i].clicked.connect(self.Delete)
            self.btnAdds[i+1].show()
            self.btnAdds[i+1].setText("+")
            self.btnAdds[i+1].disconnect()
            self.btnAdds[i+1].clicked.connect(self.Add)
        else:
            self.btnAdds[0].show()
            self.btnAdds[0].setText("+")
            self.btnAdds[0].disconnect()
            self.btnAdds[0].clicked.connect(self.Add)

        self.btnClose.clicked.connect(self.hide)
        self.btnUserRegister.clicked.connect(self.userRegister)
        self.btnFeedSetting.clicked.connect(self.feedSetting)

        self.labelID.setText(self.windowClass.petID)
        self.labelName.setText(self.windowClass.name)
        self.labelBirth.setText(self.windowClass.birth)
        self.labelAge.setText(self.windowClass.age)
        self.labelWeight.setText(self.windowClass.weight)
        self.labelSpecies.setText(self.windowClass.species)
        self.labelContactNumber.setText(self.windowClass.contact_number)

    def userRegister(self):
        retval = QMessageBox.question(self, 'User Edit', '반려동물 정보를 수정하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if retval == QMessageBox.Yes:
            self.hide()
            self.register = RegisterWindowClass(self)
            self.register.show()
        else:
            pass

    def setTimeFeeding(self):
        for i in range(len(self.windowClass.feeding_times)):
            self.windowClass.feeding_times[i] = self.timeFeedings[i].time().toString("hh:mm:ss")

    def Delete(self):
        btn_names = [val.objectName() for val in self.btnAdds]
        idx = btn_names.index(self.sender().objectName())

        self.windowClass.feeding_times.pop(idx)

        tmp_feeding_times = self.windowClass.feeding_times.copy()

        for i in range(5):
            self.btnAdds[i].hide()
            self.timeFeedings[i].hide()

        if tmp_feeding_times:
            for i in range(len(tmp_feeding_times)):
                self.timeFeedings[i].show()
                tmp_li = tmp_feeding_times[i].split(":")
                self.timeFeedings[i].setTime(QTime(int(tmp_li[0]), int(tmp_li[1]), int(tmp_li[2])))
                self.btnAdds[i].show()
                self.btnAdds[i].setText("-")
                self.btnAdds[i].disconnect()
                self.btnAdds[i].clicked.connect(self.Delete)
            self.btnAdds[i+1].show()
            self.btnAdds[i+1].setText("+")
            self.btnAdds[i+1].disconnect()
            self.btnAdds[i+1].clicked.connect(self.Add)
        else:
            self.btnAdds[0].show()
            self.btnAdds[0].setText("+")
            self.btnAdds[0].disconnect()
            self.btnAdds[0].clicked.connect(self.Add)

    def Add(self):
        len_times = len(self.windowClass.feeding_times)
        # 타임 에디트 추가
        self.timeFeedings[len_times].show()
        self.timeFeedings[len_times].setTime(QTime(0, 0, 0))
        self.windowClass.feeding_times.append("00:00:00")
        # 플마버튼 추가
        self.btnAdds[len_times].setText("-")
        self.btnAdds[len_times].disconnect()
        self.btnAdds[len_times].clicked.connect(self.Delete)
        if len_times + 1 < 5:
            self.btnAdds[len_times + 1].show()
            self.btnAdds[len_times + 1].setText("+")
            self.btnAdds[len_times + 1].disconnect()
            self.btnAdds[len_times + 1].clicked.connect(self.Add)

    def feedSetting(self):

        feed_index1 = 1
        feeding_amount1 = self.editFeed.text()
        feeding_time1 = self.timeFeeding1.time()
        feeding_time1 =feeding_time1.toPyTime()

        feed_index2 = 2
        feeding_amount2 = self.editFeed.text() if self.add_1 else 0
        feeding_time2 = self.timeFeeding2.time() 
        feeding_time2 =feeding_time2.toPyTime() if self.add_1 else None

        feed_index3 = 3
        feeding_amount3 = self.editFeed.text() if self.add_1 else 0
        feeding_time3 = self.timeFeeding3.time()
        feeding_time3 =feeding_time3.toPyTime() if self.add_1 else None

        feeding_schedule = [self.petID, 
            feed_index1, feeding_amount1, feeding_time1, 
            feed_index2, feeding_amount2, feeding_time2, 
            feed_index3, feeding_amount3, feeding_time3]

        message = ["Feeding Schedule"]
        for val in feeding_schedule:
            message.append(str(val))
        self.windowClass.sendTCP(message)

    def mainPage(self):
        self.hide()
        self.main = WindowClass()
        self.main.show()

class RegisterWindowClass(QMainWindow, form_register_Class):
    def __init__(self, windowClass):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("Register")

        self.windowClass = windowClass
        print(self.windowClass.id_flag)
        self.initUI()

    def initUI(self):
        self.btnCancle.clicked.connect(self.returnSetting)
        self.btnUserRegister.clicked.connect(self.userRegister)

        self.cbSpecies.addItem("강아지")
        self.cbSpecies.addItem("고양이")

        if self.windowClass.id_flag == True:
            self.labelID.setText(self.windowClass.petID)
            self.editName.setText(self.windowClass.name)
            self.dateEditBirth.setText(self.windowClass.birth)
            self.labelAge.setText(self.windowClass.age)
            self.editWeight.setText(self.windowClass.weight)
            self.cbSpecies.setText(self.windowClass.species)
            self.editContactNumber.setText(self.windowClass.contact_number)

        self.labelID.setText("1")
        self.dateEditBirth.dateChanged.connect(self.getAge)

        self.editContactNumber.textChanged.connect(self.legExCheck)
        self.len_prev = 0

    def getAge(self):
        birth_qt = self.dateEditBirth.date()
        birth = birth_qt.toPyDate()
        today = datetime.today()
        self.age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        self.labelAge.setText(str(self.age))

    def legExCheck(self):
        tmp = self.editContactNumber.text()
        if len(tmp) == 3 and self.len_prev == 2:
            self.editContactNumber.setText(tmp + "-")
        elif len(tmp) == 8 and self.len_prev == 7:
            self.editContactNumber.setText(tmp + "-")
        self.len_prev = len(tmp)

    def userRegister(self):
        name = self.editName.text()
        birth = self.dateEditBirth.date().toPyDate()
        weight = self.editWeight.text()
        species_ko = self.cbSpecies.currentText()
        contact_number = self.editContactNumber.text()
        if species_ko == "강아지":
            species = "dog"
        elif species_ko == "고양이":
            species = "cat"

        user_register = [self.petID, name, birth, weight, species, contact_number]
        message = ["User Register"]
        for val in user_register:
            message.append(str(val))
        self.windowClass.sendTCP(message)

        self.returnSetting()

    def returnSetting(self):
        self.hide()
        if self.windowClass.id_flag == True:
            self.setting = SettingWindowClass(self.windowClass)
            self.setting.show()

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

        self.btnPlace1.hide()
        self.btnPlace2.hide()
        self.btnPlace3.hide()
        
        self.btnGpsPage.hide()

        self.btnPlace1.clicked.connect(lambda : self.roadPlace(1))
        self.btnPlace2.clicked.connect(lambda : self.roadPlace(2))
        self.btnPlace3.clicked.connect(lambda : self.roadPlace(3))

    def setIcon(self):
        self.btnMainPage.setIcon(QIcon("../../data/icon/home.png"))
        self.btnRight.setIcon(QIcon("../../data/icon/arrow-right.png"))
        self.btnDown.setIcon(QIcon("../../data/icon/arrow-down.png"))
        self.btnUp.setIcon(QIcon("../../data/icon/right-arrow.png"))
        self.btnLeft.setIcon(QIcon("../../data/icon/play.png"))
        self.btnFeed.setIcon(QIcon("../../data/icon/pet-food.png"))
        self.btnPlay.setIcon(QIcon("../../data/icon/ball.png"))
               
        self.labelPulseIcon.setPixmap(QPixmap("../../data/icon/pulse.png"))

    def roadPlace(self, key):
        messages = ["WebCam Control Saved Place"]
        messages.append(str(key))
        self.sendTCP(messages)
    
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
        self.isCameraOn = False
        self.camera.stop()

        self.main.labelInit.hide()
        self.main.btnUser1.hide()
        self.main.btnUser2.hide()
        self.main.btnUser3.hide()
        self.main.btnUser4.hide()
        self.main.btnRegister.hide()
        self.main.show()

def receiveTCPEvent(client_socket, windowClass):
    while socket_thread_flag == True:
        data = client_socket.recv(1024).decode('utf-8')
        print(data)

if __name__ == "__main__":
    app = QApplication(sys.argv)     
    myWindows = WindowClass()   
    myWindows.show()
    sys.exit(app.exec_())