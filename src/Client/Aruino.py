import sys
import cv2
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import pyqtgraph as pg
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
form_log_Class = uic.loadUiType("Log.ui")[0]

server_address = "192.168.2.29"
#"192.168.0.156"
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

        self.btnUser1.hide()
        self.btnUser2.hide()
        self.btnUser3.hide()
        self.btnUser4.hide()
    
        self.feeding_times = []

        self.editInit.setValidator(QIntValidator(1,20))
        self.btnInit.setText("입력")
        self.btnInit.clicked.connect(self.userInit)
        self.editInit.returnPressed.connect(self.userInit)

        self.active = [0] * 20

        self.count = 0

    def userInit(self):
        self.petID = self.editInit.text()

        try:
            self.editInit.hide()
            self.btnInit.hide()
            self.labelInit_2.hide()
            self.firstInit()
            self.id_flag = True
        except(ConnectionRefusedError):
            self.editInit.show()
            self.btnInit.show()
            self.labelInit_2.show()
            QMessageBox.warning(self, "Server closed", "서버가 닫혀있습니다.")
            return
        
        print(self.id_flag)
        print("done")

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
        print("first init response :", self.petInfo)

        # self.feeding_times = []
        for i in range(len(self.petInfo) - 6):
            self.feeding_times.append(self.petInfo[i+6])

        print("done first init")
        self.initUI()
        print("done init ui")
        
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
        self.btnLogPage.clicked.connect(self.logPage)

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

        self.timer.start(1000)
        print("timer start")

        self.setGraph()

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
        # print("request sync data")
        response = self.requestTCP(["Sync Data"])
        # print("request :", response)
        self.sync_data = response.split("&&")
        sync_data = self.sync_data
        
        if self.count == 1:
            print(self.sync_data)
            print(self.feeder_water_level)

        if sync_data[0] == "Sync Data":
            humidity = sync_data[1]
            temp = sync_data[2]
            self.hic = sync_data[3]
            self.feeder_water_level = sync_data[4]
            self.feeder_food_level = sync_data[5]
            self.temp_body = sync_data[6]
            self.pulse = sync_data[7]
            self.activity = sync_data[8]
            self.activity_label = sync_data[9]
            
            # print("Sync Data", sync_data)

            if len(self.temp_body) >= 4:
                self.temp_body = self.temp_body[:4]

            self.labelTemp.setText(f"현재 온도 : {temp}°C")
            self.labelHumid.setText(f"현재 습도 : {humidity}%")
            self.labelActivity.setText(self.activity_label)
            self.labelTempBody.setText(self.temp_body)
            self.labelPulse.setText(self.pulse)
            self.labelCalories.setText(self.activity)

            # if self.activity == "쉬는 중":
            #     active = 1
            # elif self.activity == "걷는 중":
            #     active = 2
            # elif self.activity == "뛰는 중":
            #     active = 3
            # else:
            #     return

            self.active = self.active[1:]
            self.active.append(float(self.activity))
            self.data_line.setData(self.active)
            # self.widgetActivity.plot(self.active, background=None)

            # print("getting sync data")
            
            # self.updateGraph()
            self.count += 1
            self.updateGraph()

        if self.count % 5 == 0:
            print(self.count, self.sync_data)

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
        self.btnLogPage.setIcon(QIcon("../../data/icon/file.png"))
        self.btnLogPage.setIconSize(QSize(50, 50))
        self.btnSetting.setIcon(QIcon("../../data/icon/setting.png"))

        self.labelDog.setPixmap(QPixmap("../../data/icon/dog-sit.png")) 
        self.labelDog.setStyleSheet("background-color: transparent;")

        self.btnHeart.setIcon(QIcon("../../data/icon/heart.png"))
        
        self.labelPulseIcon.setPixmap(QPixmap("../../data/icon/pulse.png"))
        self.labelPawIcon.setPixmap(QPixmap("../../data/icon/paws.png"))
        self.labelPawIcon2.setPixmap(QPixmap("../../data/icon/paws.png"))

        self.labelFood.setPixmap(QPixmap("../../data/icon/pet-bowl.png").scaled(60, 60))
        self.labelWater.setPixmap(QPixmap("../../data/icon/water-bowl.png").scaled(60, 60))

    def setGraph(self):
        self.plotFood = self.findChild(pg.PlotWidget, "widgetFoodLevel")
        self.plotWater = self.findChild(pg.PlotWidget, "widgetWaterLevel")
        self.plotActivity = self.findChild(pg.PlotWidget, "widgetActivity")

        self.plotFood.setBackground('w')
        self.plotWater.setBackground('w')
        self.plotActivity.setBackground(background=None)
        self.plotActivity.setYRange(5,30)
        self.plotActivity.getPlotItem().hideAxis('bottom')
        self.plotActivity.getPlotItem().hideAxis('left')
        self.data_line = self.plotActivity.plot(self.active, background=None, pen= 'k', width=2)

        self.plotFood.getPlotItem().hideAxis('left')
        # self.plotFood.getPlotItem().invertX(True)
        # self.plotFood.getPlotItem().invertY(True)

        self.plotWater.getPlotItem().hideAxis('left')
        # self.plotWater.getPlotItem().invertX(True)
        # self.plotWater.getPlotItem().invertY(True)

        self.plotFood.setXRange(0, 100)
        self.plotWater.setXRange(0, 800)
        self.plotFood.setYRange(0, 1)
        self.plotWater.setYRange(0, 1)

        # if not self.sync_data:
        #     self.feeder_food_level = 50
        #     self.feeder_water_level = 20
        # print(self.feeder_water_level)

    def updateGraph(self):
        x = np.linspace(0, 1, 2)
        water_level = int(self.feeder_water_level)
        water_level_li = [water_level] * 2 #self.water_level
        # food_level = [self.feeder_food_level] * 2 # self.food_level
        curve_w1 = self.plotWater.plot(water_level_li, x, pen=(65, 105, 225))
        curve_w2 = self.plotWater.plot([0,0], [0, water_level], pen=(65, 105, 225))

        # curve_f1 = self.plotFood.plot(food_level, x, pen=(245, 194, 107))
        # curve_f2 = self.plotFood.plot([0,0], [0, self.feeder_food_level], pen=(245, 194, 107))

        # self.plotFood.addItem(pg.FillBetweenItem(curve_f1, curve_f2, brush=(245, 194, 107)))
        self.plotWater.addItem(pg.FillBetweenItem(curve_w1, curve_w2, brush=(65, 105, 225)))
        # print("good")

    def cameraPage(self):
        self.cam = CamWindowClass(self)
        self.cam.show()
        self.hide()

    def settingPage(self):
        self.setting = SettingWindowClass(self)
        self.setting.show()

    def registerPage(self):
        self.register = RegisterWindowClass(self)
        self.register.frameGeometry().moveCenter(QDesktopWidget().availableGeometry().center())
        self.register.move(self.frameGeometry().topLeft())
        self.register.show()

    def logPage(self):
        self.log = LogWindowClass(self)
        self.log.show()

class LogWindowClass(QMainWindow, form_log_Class):
    def __init__(self, windowClass):
        super().__init__()
        self.setupUi(self)
        self.windowClass = windowClass

        self.setWindowTitle("Weekly Log")

        self.initUI()
        self.retreiveActivityLog()

    def initUI(self):
        # self.widget = pg.GraphicsLayoutWidget()

        self.plotCalories = self.findChild(pg.PlotWidget, "plotCalories")
        self.plotFeed = self.findChild(pg.PlotWidget, "plotFeed")

        self.plotCalories.setBackground('w')
        self.plotFeed.setBackground('w')

        # self.plot1 = pg.PlotWidget(background='w', title="Calories")
        self.plotCalories.setXRange(1, 8, -1)
        self.plotCalories.setYRange(0, 100)
        # self.plot2 = pg.PlotWidget(background='w', title="Feeding")
        self.plotFeed.setXRange(1, 8, -1)
        self.plotFeed.setYRange(0, 100)

        self.graph_layout = self.findChild(pg.GraphicsLayoutWidget, "widget")

        self.graph_layout.setBackground('w')
        self.plotLay = self.graph_layout.addPlot(title="Laying Down")
        self.graph_layout.nextRow()
        self.plotWalk = self.graph_layout.addPlot(title="Walking")
        self.graph_layout.nextRow()
        self.plotRun = self.graph_layout.addPlot(title="Running")

        self.x = list(range(7))
        self.y = [0] * 7
    
    def retreiveActivityLog(self):
        self.day = []
        self.calories = []
        self.lay = []
        self.walk = []
        self.run = []

        response = self.windowClass.requestTCP(["Activity Log", str(self.windowClass.petID)])
        self.log_data = response.split("&&")
        print(self.log_data)
        # print("request activity log")
        if self.log_data[0] == "Activity Log":
            for each in self.log_data[1:]:
                tmp_list = each.split(",")
                print(tmp_list)
                self.day.append(tmp_list[0].split(" ")[0])
                self.calories.append(float(tmp_list[1]))
                self.lay.append(int(tmp_list[2]))
                self.walk.append(int(tmp_list[3]))
                self.run.append(int(tmp_list[4]))
                

            yesterday = int(self.day[0][-2:])
            weekago = int(self.day[6][-2:])

            print(yesterday, weekago)

            self.plotCalories.setXRange(yesterday, weekago, -1)
            self.plotFeed.setXRange(yesterday, weekago, -1)

            self.labelYesterday.setText(self.day[0][-2:] + "일")
            self.labelMidDay.setText(self.day[4][-2:] + "일")
            self.labelWeekAgo.setText(self.day[6][-2:] + "일")
            self.labelYesterday.hide()
            self.labelMidDay.hide()
            self.labelWeekAgo.hide()

            # print("getting activity log", self.response)

            self.data_calories = self.plotCalories.plot(self.x, self.calories, pen='r')
            self.data_feed = self.plotFeed.plot(self.x, self.lay, self.walk, self.run, pen='r')
            # self.plotCalories.plot(self.calories)
            # self.plotFeed.plot(self.lay, self.walk, self.run)

            self.data_lay = self.plotLay.plot(self.x, self.lay, pen='g')
            self.data_walk = self.plotWalk.plot(self.x, self.walk, pen='b')
            self.data_run = self.plotRun.plot(self.x, self.run, pen='y')

            self.plotLay.setXRange(yesterday, weekago, -1)
            self.plotWalk.setXRange(yesterday, weekago, -1)
            self.plotRun.setXRange(yesterday, weekago, -1)


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
        # print("Setting Page - feeding_times :", self.windowClass.feeding_times)
        
        self.initUI()

    def initUI(self):
        for i in range(5):
            self.btnAdds[i].hide()
            self.timeFeedings[i].hide()
         
        if self.windowClass.feeding_times:
            # print("1. setting init", self.windowClass.feeding_times)    
            for i, val in enumerate(self.windowClass.feeding_times):
                # print(val)
                self.timeFeedings[i].show()
                tmp_li = val.split(":")
                self.timeFeedings[i].setTime(QTime(int(tmp_li[0]), int(tmp_li[1]), int(tmp_li[2])))
                self.timeFeedings[i].timeChanged.connect(self.setTimeFeeding)
                self.btnAdds[i].show()
                self.btnAdds[i].setText("-")
                self.btnAdds[i].disconnect()
                self.btnAdds[i].clicked.connect(self.Delete)
            # print("2. setting init", self.windowClass.feeding_times)
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
            # print("setTimeFeeding", self.windowClass.feeding_times[i])
            self.windowClass.feeding_times[i] = self.timeFeedings[i].time().toString("hh:mm:ss")
        #     print("after setTimeFeeding", self.windowClass.feeding_times[i])
        #     print("timeFeedings", self.timeFeedings[i].time().toString("hh:mm:ss"))
            
        # print("settime",self.windowClass.feeding_times)

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
        self.setTimeFeeding()
        retval = QMessageBox.question(self, 'Feed Setting', '배식 시간 설정을 설정하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if retval == QMessageBox.Yes:
            feeding_schedule = ["Feeding Schedule", self.windowClass.petID]

            for i in range(len(self.windowClass.feeding_times)):
                feeding_schedule.append(self.windowClass.feeding_times[i])

            message = feeding_schedule
            print("feeding setting", message)
            self.windowClass.sendTCP(message)
        else:
            pass

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
        # print("Register Page - windowClass :", windowClass)
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
            # print(response)
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

        self.setWindowTitle("Web Cam Monitoring")
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

        for btnPlace in self.btnPlaces:
            btnPlace.setFont(QFont("Ubuntu", 8))
            btnPlace.setText("즐겨찾는 장소")
            
        self.btnPlace1.clicked.connect(lambda : self.loadPlace(0))
        self.btnPlace2.clicked.connect(lambda : self.loadPlace(1))
        self.btnPlace3.clicked.connect(lambda : self.loadPlace(2))

        self.btnSavePlace.clicked.connect(self.savePlace)
        self.btnDeletePlace.clicked.connect(self.deletePlace)

    def setIcon(self):
        self.btnMainPage.setIcon(QIcon("../../data/icon/home.png"))
        self.btnRight.setIcon(QIcon("../../data/icon/arrowRight.png"))
        self.btnDown.setIcon(QIcon("../../data/icon/arrowDown.png"))
        self.btnUp.setIcon(QIcon("../../data/icon/arrowUp.png"))
        self.btnLeft.setIcon(QIcon("../../data/icon/arrowLeft.png"))
        self.btnFeed.setIcon(QIcon("../../data/icon/pet-food.png"))
        self.btnPlay.setIcon(QIcon("../../data/icon/ball.png"))

        for i in range(len(self.btnSounds)):
            self.btnSounds[i].setText("-")

        self.btnGood.setText("음성 저장")
               
        self.labelPulseIcon.setPixmap(QPixmap("../../data/icon/pulse.png"))

        # self.labelTempBody.setText(self.windowClass.temp_body)
        # self.labelPulse.setText(self.windowClass.pulse)

    def fetchPlaces(self):
        messages = ["WebCam Fetch Place"]
        messages.append(self.windowClass.petID)
        response = self.requestTCP(messages)
        places = response.split("&&")
        self.place_id_list = []
        self.place_name_list = []

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
            self.btnPlaces[i].setFont(QFont("Ubuntu", 10))
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
                self.btnPlaces[i].setFont(QFont("Ubuntu", 8))
                self.btnPlaces[i].setText("즐겨찾는 장소")

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
        self.pixmap = self.pixmap.scaled(670, 520, Qt.KeepAspectRatio)
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