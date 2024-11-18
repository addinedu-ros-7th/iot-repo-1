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

class Pet():
    def __init__(self, name, birth, weight, species, contact_number):
        self._name = name
        self._birth = birth
        self._weight = weight
        self._species = species
        self._contact_number = contact_number
        self._age

    @property
    def age(self):
        birth = datetime.strptime(self._birth, '%Y-%m-%d').date()
        today = datetime.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return str(age)
    
    def changeName(self, name):
        self._name = name

class TCP():
    def send(self, messages):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
        client_socket.close()

    def request(self, messages):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        client_socket.close()
        return response
    
    def split(self, response):
        return response.split("&&")
    
class camTCP(TCP):
    def request(self, messages, iscamera=False):
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
            data = np.frombuffer(base64.b64decode(stringData), np.uint8)
            decimg = cv2.imdecode(data, 1)
            return decimg
        
    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf
        
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

        # print("Main Window", id(self))

        self.setWindowTitle("Aruino - Your Smart Pet Sitter")

        try: 
            print("Main - id_flag :", self.id_flag)
            print("Main - petID :", self.petID)
        except AttributeError:
            print("lost id_flag")
            self.id_flag = False
            print("Main - id_flag :", self.id_flag)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.timeout.connect(self.fetchSyncData)

        self.updateTime()

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
        print("userSelect - id_flag :", self.id_flag)

        self.firstInit()
        # self.timer.start(1000)

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
        self.btnPlayPage.clicked.connect(self.playPage)

        self.labelFood.hide()

        self.labelName.setText(self.name)
        self.labelAge.setText(self.age)
        if self.species == "cat":
            self.labelDog.setPixmap(QPixmap("../../data/icon/cat.png"))
            self.btnHeart.move(470,300)
            self.btnHeart.setIconSize(QSize(50, 50))
        else:
            self.labelDog.setPixmap(QPixmap("../../data/icon/dog-sit.png"))
            self.btnHeart.move(420,240)
            self.btnHeart.setIcon(QIcon("../../data/icon/heart.png"))

        self.labelNameInfo.hide()
        self.labelAgeInfo.hide()

        self.timer.start(1000)

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

            # print("getting sync data")

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

    def cameraPage(self):
        self.cam = CamWindowClass(self)
        self.cam.show()
        self.hide()

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

        # print("Setting Window", id(self))

        self.add_1 = True
        self.add_2 = False
        self.add_3 = False
        self.add_4 = False
        self.add_5 = False
        
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

        self.setWindowTitle("Setting")

        self.windowClass = windowClass

        print("Setting Page - id_flag :", self.windowClass.id_flag)
        
        self.initUI()

    def initUI(self):
        for i in range(5):
            self.btnAdds[i].hide()
            self.timeFeedings[i].hide()
            self.timeFeedings[i].timeChanged.connect(self.setTimeFeeding)
         
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
            self.register = RegisterWindowClass(self.windowClass)
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
        feeding_schedule = ["Feeding Schedule", self.windowClass.petID]

        for i in range(len(self.windowClass.feeding_times)):
            feeding_schedule.append(self.windowClass.feeding_times[i])

        message = feeding_schedule
        self.windowClass.sendTCP(message)

    def mainPage(self):
        self.hide()
        self.main = self.windowClass
        self.main.show()

class RegisterWindowClass(QMainWindow, form_register_Class):
    def __init__(self, windowClass):
        super().__init__()
        self.setupUi(self)

        # print("Register Window", id(self))

        self.setWindowTitle("Register")
        print("Register Page - windowClass :", windowClass)
        self.windowClass = windowClass
        print("Register Page - windowClass.id_flag :", self.windowClass.id_flag)

        self.initUI()

    def initUI(self):
        self.btnCancle.clicked.connect(self.returnSetting)
        self.btnUserRegister.clicked.connect(self.userRegister)

        if self.windowClass.id_flag == True:
            self.btnUserRegister.setText("등록정보 수정")
        else:
            self.btnUserRegister.setText("반려동물 등록")

        self.cbSpecies.addItem("강아지")
        self.cbSpecies.addItem("고양이")

        if self.windowClass.id_flag == True:
            # self.labelID.setText(self.windowClass.petID)
            self.editName.setText(self.windowClass.name)
            self.dateEditBirth.setDate(datetime.strptime(self.windowClass.birth, '%Y-%m-%d').date())
            self.labelAge.setText(self.windowClass.age)
            self.editWeight.setText(self.windowClass.weight)
            self.cbSpecies.setCurrentIndex(0 if self.windowClass.species == "dog" else 1) #self.cbSpecies.setCurrentText(self.windowClass.species)
            self.editContactNumber.setText(self.windowClass.contact_number)

        # self.labelID.setText("1")
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
        elif len(tmp) == 8 and self.len_prev == 9:
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

        if name == "" or birth == "" or weight == "" or species == "" or contact_number == "":
            QMessageBox.warning(self, "Warning", "빈칸을 채워주세요")
            return

        if self.windowClass.id_flag == True:
            user_register = [self.windowClass.petID, name, birth, weight, species, contact_number]
            message = ["User Modify"]
            for val in user_register:
                message.append(str(val))
            response = self.windowClass.requestTCP(message)
            response = response.split("&&")
            print("request :", response)
            self.windowClass.petID = response[0]
            self.windowClass.name = response[1]
            self.windowClass.birth = response[2]
            self.windowClass.weight = response[3]
            self.windowClass.species = response[4]
            self.windowClass.contact_number = response[5]
            self.windowClass.age = getAge(self.windowClass.birth)

            self.initUI()
            self.windowClass.initUI()
            self.returnSetting()
        else:
            user_register = [name, birth, weight, species, contact_number]
            message = ["User Register"]
            for val in user_register:
                message.append(str(val))
            response = self.windowClass.requestTCP(message)
            response = response.split("&&")
            print(response)
            self.windowClass.petID = response[0]
            self.windowClass.name = response[1]
            self.windowClass.birth = response[2]
            self.windowClass.weight = response[3]
            self.windowClass.species = response[4]
            self.windowClass.contact_number = response[5]
            self.windowClass.age = getAge(self.windowClass.birth)

            self.windowClass.initUI()
            self.windowClass.id_flag = True
            self.windowClass.feeding_times = []
            self.hide()

    def returnSetting(self):
        self.hide()
        if self.windowClass.id_flag == True:
            self.setting = SettingWindowClass(self.windowClass)
            self.setting.initUI()
            self.setting.show()

class CamWindowClass(QMainWindow, form_cam_Class):
    def __init__(self, windowClass, ):
        super().__init__()
        self.setupUi(self)
        self.windowClass = windowClass

        self.isCameraOn = False
        self.camera = Camera(self)
        self.camera.daemon = True

        self.camera.update.connect(self.updateCamera)
        self.isCameraOn = True
        self.camera.running = True
        self.camera.start()

        self.btnPlaces = [
            self.btnPlace1,
            self.btnPlace2,
            self.btnPlace3
        ]

        self.btnSounds = [
            self.btnGood,
            self.btnComeOn,
            self.btnSound3,
            self.btnSound4,
            self.btnSound5,
            self.btnSound6
        ]

        self.initUI()
        self.setIcon()
        self.fetchPlaces()

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

        for soundbtn in self.btnSounds:
            soundbtn.hide()

        self.btnGood.show()

        self.btnPlace1.clicked.connect(lambda : self.loadPlace(0))
        self.btnPlace2.clicked.connect(lambda : self.loadPlace(1))
        self.btnPlace3.clicked.connect(lambda : self.loadPlace(2))

        self.btnSavePlace.clicked.connect(self.savePlace)
        self.btnDeletePlace.clicked.connect(self.deletePlace)

    def setIcon(self):
        self.btnMainPage.setIcon(QIcon("../../data/icon/home.png"))
        self.btnRight.setIcon(QIcon("../../data/icon/arrow-right.png"))
        self.btnDown.setIcon(QIcon("../../data/icon/arrow-down.png"))
        self.btnUp.setIcon(QIcon("../../data/icon/right-arrow.png"))
        self.btnLeft.setIcon(QIcon("../../data/icon/play.png"))
        self.btnFeed.setIcon(QIcon("../../data/icon/pet-food.png"))
        self.btnPlay.setIcon(QIcon("../../data/icon/ball.png"))

        for i in range(len(self.btnSounds)):
            self.btnSounds[i].setText("-")

        self.btnGood.setText("저장하기")
               
        self.labelPulseIcon.setPixmap(QPixmap("../../data/icon/pulse.png"))

    def fetchPlaces(self):
        messages = ["WebCam Fetch Place"]
        messages.append(self.windowClass.petID)
        response = self.requestTCP(messages)
        places = response.split("&&")
        self.place_id_list = []
        self.place_name_list = []
        print(len(places))

        if len(places) > 1:
            for i in range(0, len(places), 2):
                self.place_id_list.append(places[i])
                self.place_name_list.append(places[i+1])

        for i in range(len(self.place_id_list)):
            self.btnPlaces[i].setStyleSheet("background-color:white;\
                                            border-radius:40px;\
                                            border-color:#4169E1;\
                                            border-width:7px;\
                                            border-style:solid;")
            self.btnPlaces[i].setText(self.place_name_list[i])

    def loadPlace(self, key):
        messages = ["WebCam Control Saved Place"]
        messages.append(self.windowClass.petID)
        messages.append(self.place_id_list[key])
        self.sendTCP(messages)

    def savePlace(self):
        text, ok = QInputDialog.getText(self, 'Save Place', '장소를 기억할 이름을 입력해주세요.')

        if ok and text:
            self.place_name = text
            messages = ["WebCam Save Place"]
            messages.append(self.windowClass.petID)
            messages.append(self.place_name)
            self.sendTCP(messages)

            self.fetchPlaces()

    def deletePlace(self):
        item, ok = QInputDialog.getItem(self, 'Delete Place', '삭제할 장소를 선택해주세요', self.place_name_list, 0, False)

        if ok and item:
            self.place_name = item

            for i in range(len(self.place_name_list)):
                if self.place_name_list[i] == item:
                    item = self.place_id_list[i]
                    break

            messages = ["WebCam Delete Place"]
            messages.append(self.windowClass.petID)
            messages.append(self.place_id_list[i])
            self.sendTCP(messages)

            # for i in range(3):
            #     self.btnPlaces[i].hide()

            for i in range(len(self.place_id_list)):
                self.btnPlaces[i].setStyleSheet("background-color:white;\
                                                border-radius:40px;\
                                                border-color:#d4d4d4;\
                                                border-width:7px;\
                                                border-style:solid;")
                self.btnPlaces[i].setText("")

            self.fetchPlaces()
    
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
        self.main = self.windowClass
        self.isCameraOn = False
        self.camera.stop()

        self.main.labelInit.hide()
        self.main.btnUser1.hide()
        self.main.btnUser2.hide()
        self.main.btnUser3.hide()
        self.main.btnUser4.hide()
        self.main.btnRegister.hide()

        self.main.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)     
    myWindows = WindowClass()   
    myWindows.show()
    sys.exit(app.exec_())