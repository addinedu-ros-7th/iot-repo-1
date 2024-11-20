import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import cv2, imutils
import PyQt5
from PyQt5.QtCore import *

import time
import serial
import threading
import socket
import mysql.connector
import numpy as np
from datetime import datetime

import base64

from_class = uic.loadUiType("project/iot-repo-1/src/Server/AruinoService.ui")[0]
tcp_controller_read_flag = True
tcp_client_read_flag = True
sefial_read_flag0 = True

client_first_init_flag = False

class Camera(QThread):
    update = pyqtSignal()

    def __init__(self, sec=0, parent=None):
        super().__init__()
        self.main = parent
        self.running = True
    def run(self):
        while self.running == True:
            self.update.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False

class WindowClass(QMainWindow, from_class):
    def __init__(self, py_serial0, py_serial1, server_socket0, server_socket1):
        super().__init__()
        self.setupUi(self)

        self.le_feedTimes = [
            self.le_feedTime1,
            self.le_feedTime2,
            self.le_feedTime3,
            self.le_feedTime4,
            self.le_feedTime5
        ]

        for obj in self.le_feedTimes: obj.hide()
            
        self.Client_flag = False
        self.Controller_flag = False
        self.ledClient.setStyleSheet(f"background-color: {"yellow" if self.Client_flag else "gray"};border: 1px solid black;") 
        self.ledController.setStyleSheet(f"background-color: {"yellow" if self.Client_flag else "gray"};border: 1px solid black;") 

        self.isCameraOn = False
        self.camera = Camera(self)
        self.camera.daemon = True
        self.img = np.zeros((100,100))
        self.qimg = None
        self.count = 0
        self.pixmap = QPixmap()

        self.server_socket0 = server_socket0
        self.server_socket1 = server_socket1
        self.py_serial = py_serial1
        self.py_serial_feeder = py_serial0

        self.petID = "1"
        self.petName = ""
        self.petBirth = ""
        self.petWeight = ""
        self.petSpecies = ""
        self.contactNumber = ""

        # Comunicator
        self.up_down_angle = 90
        self.left_right_angle = 90

        # Feeder
        self.feeder_humidity = 0
        self.feeder_temperature = 0
        self.feeder_hic = 0
        self.feeder_water_level = 0
        self.feeder_food_level = 0

        self.now_time = ""
        self.recent_feed_time = "99:99"
        self.only_now_time = "999:99"
        self.feeding_schedule = []

        # Pet Checker
        self.pet_calorie_sum = 0
        self.status_log = [0,0,0]
        self.pet_check_cnt = 0
        self.pet_temperature = 0.
        self.pet_heart_rate = 0
        self.pet_calorie = 0.
        self.pet_status = ""
        self.pet_lay = 0
        self.pet_walk = 0
        self.pet_run = 0

        self.remote = mysql.connector.connect(
            host = "database-1.c3micoc2s6p8.ap-northeast-2.rds.amazonaws.com",
            user = "aru",
            password = "1234",
            database = "aruino_test"
        )
        self.cur = self.remote.cursor(buffered=True)

        self.camera.update.connect(self.updateCamera)
        self.isCameraOn = True
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture("/dev/video2")
        # self.video = cv2.VideoCapture(0)

        self.test_btn.clicked.connect(self.test_fn)
        self.pushButton_6.clicked.connect(self.test_fn2)
        self.pushButton_9.clicked.connect(self.test_fn3)

        self.btn_up.pressed.connect(lambda: self.test_cam_fn("up", "start"))
        self.btn_down.pressed.connect(lambda: self.test_cam_fn("down", "start"))
        self.btn_left.pressed.connect(lambda: self.test_cam_fn("left", "start"))
        self.btn_right.pressed.connect(lambda: self.test_cam_fn("right", "start"))

        self.btn_up.released.connect(lambda: self.test_cam_fn("up", "end"))
        self.btn_down.released.connect(lambda: self.test_cam_fn("down", "end"))
        self.btn_left.released.connect(lambda: self.test_cam_fn("left", "end"))
        self.btn_right.released.connect(lambda: self.test_cam_fn("right", "end"))

    def test_cam_fn(self, pos, se):
        print( pos, se)
        key10 = 1 if pos == "up" else 2 if pos == "down" else 3 if pos == "left" else 4
        key01 = 1 if se == "start" else 0

        key = key10 * 10 + key01
        message = "WebCam Control"
        print(key)
        sendSerial(self.py_serial, key, message)


    def test_fn3(self):
        print("##################################################")
        print("################It's Time to Feed!! 54###############")
        print("##################################################")
        sendSerial(self.py_serial_feeder, 54, "")
    
    def test_fn2(self):
        print("##################################################")
        print("################It's Time to Feed!! 53###############")
        print("##################################################")
        sendSerial(self.py_serial_feeder, 53, "")

    def test_fn(self):
        print("test btn pushed!!!")
        # sendSerial(self.py_serial_feeder, 53, "u,90,90")
        print("Feeder Sync Start!!")
        sendSerial(self.py_serial_feeder, 1, "")

    def updateCamera(self):
        self.now_time = str(datetime.now())[:-7]
        self.labelDateTime.setText(self.now_time)
        retval, img = self.video.read()

        if retval:
            self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h,w,c = img.shape
            self.qimg = QImage(self.img.data, w,h,w*c, QImage.Format_RGB888)
            self.pixmap = self.pixmap.fromImage(self.qimg)
            self.pixmap = self.pixmap.scaled(self.labelCam.width(), self.labelCam.height())
            self.labelCam.setPixmap(self.pixmap)

        self.only_now_time = self.now_time.split(" ")[1][:5] # 09:51 -> 9시 51분

        # print("only_now_time", self.only_now_time)
        # print("recent_feed_time", self.recent_feed_time)

        if self.recent_feed_time == self.only_now_time:
            print("##################################################")
            print("################It's Time to Feed!!###############")
            print("##################################################")
            sendSerial(self.py_serial_feeder, 53, "u,400,10") # 53u,400,10

            if len(self.feeding_schedule) >= 1:
                self.recent_feed_time = "99:99"
                for time in reversed(self.feeding_schedule):
                    # print(only_now_time, time[:5], only_now_time < time[:5])
                    if self.only_now_time < time[:5]:
                        self.recent_feed_time = time[:5]
                if self.recent_feed_time == "99:99":
                    self.recent_feed_time = time[:5]
                elif self.recent_feed_time <= self.only_now_time:
                    self.recent_feed_time = "99:99"
            else:
                self.recent_feed_time = "99:99"
            #  print("recent_feed_time:", self.recent_feed_time)
            self.recent_feed_time = "99:99"
            print(self.recent_feed_time)


    def initUI(self):
        self.labelID.setText(str(self.petID))
        self.labelName.setText(str(self.petName))
        self.labelAge.setText(str(self.petBirth))
        self.labelWeight.setText(str(self.petWeight))
        self.labelSpecies.setText(str(self.petSpecies))
        self.labelContactNumber.setText(str(self.contactNumber))

    def initUI_feedTime(self):
        for obj in self.le_feedTimes: obj.hide()
        for i, val in enumerate(self.feeding_schedule):
            self.le_feedTimes[i].show()
            self.le_feedTimes[i].setText(str(val))


    def closeEvent(self, event):
        global tcp_controller_read_flag, tcp_client_read_flag, sefial_read_flag0
        print("소켓 해제")
        tcp_controller_read_flag = False
        tcp_client_read_flag = False
        sefial_read_flag0 = False

        self.py_serial.close()
        self.server_socket0.close()
        self.server_socket1.close()
        print("소켓 해제 완료")

    def fetchClientFirstInit(self, id):
        self.cur.execute(f"SELECT * FROM pet where pet_id = {int(id)}")
        petInfo = self.cur.fetchall()
        self.petID = petInfo[0][0]
        self.petName = petInfo[0][1]
        self.petBirth = petInfo[0][2]
        self.petWeight = petInfo[0][3]
        self.petSpecies = petInfo[0][4]
        self.contactNumber = petInfo[0][5]

        self.cur.execute(f"SELECT * FROM feeding_schedule where pet_id = {int(id)}")
        self.feeding_schedule = [row[2] for row in self.cur.fetchall()]

        if len(self.feeding_schedule) > 0:
            self.recent_feed_time = "99:99"
            for time in reversed(self.feeding_schedule):
                # print(only_now_time, time[:5], only_now_time < time[:5])
                if self.only_now_time < time[:5]:
                    self.recent_feed_time = time[:5]
            if self.recent_feed_time == "99:99":
                self.recent_feed_time = time[:5]
        else:
            self.recent_feed_time = "99:99"
    
        self.initUI()
        self.initUI_feedTime()

        # 01 start Sync Data
        print("Feeder Sync Start!!")
        sendSerial(self.py_serial_feeder, 1, "")

        response = []
        for val in petInfo[0]:
            response.append(str(val))
        for val in self.feeding_schedule:
            response.append(str(val))
        return "&&".join(response)
    
    def requestFetchPlace(self, id):
        self.cur.execute(f"SELECT webcam_position_ID, position_name FROM webcam_position WHERE pet_id = {int(id)};")
        positions = [str(row[0]) + "&&" + str(row[1]) for row in self.cur.fetchall()]
        response = []
        for val in positions:
            response.append(str(val))
        return "&&".join(response)
    
    def savePlace(self, id, name):
        self.cur.execute(f'''INSERT INTO webcam_position VALUES (NULL, {int(id)}, "{str(name)}", {self.up_down_angle}, {self.left_right_angle});''')
        self.remote.commit()
    
    def deletePlace(self, pet_id, position_id):
        self.cur.execute(f'''DELETE FROM webcam_position WHERE webcam_position_ID = {int(position_id)} AND pet_id = {int(pet_id)};''')
        self.remote.commit()

    def getPosition(self, pet_id, position_id):
        self.cur.execute(f"SELECT vertical_angle, horizen_angle FROM webcam_position WHERE webcam_position_ID = {int(position_id)} AND pet_id = {int(pet_id)};")
        position = self.cur.fetchall()[0]
        return f"{position[0]},{position[1]}"
    
    def updateFeedingSchedule(self, ft_list):
        id = ft_list[0]

        self.cur.execute(f'''DELETE FROM feeding_schedule WHERE pet_id = {int(id)};''')
        self.remote.commit()

        for t in ft_list[1:]:
            self.cur.execute(f'''INSERT INTO feeding_schedule VALUES (NULL, {int(id)}, '{str(t)}', 50);''')
            self.remote.commit()

    def updatePET(self, info_list):
        sql = f'''UPDATE pet 
                SET 
                    pet_name="{str(info_list[1])}", 
                    pet_birthday="{str(info_list[2])}", 
                    pet_weight={float(info_list[3])}, 
                    pet_species="{str(info_list[4])}", 
                    pet_contact_number="{str(info_list[5])}" 
                WHERE pet_id={int(info_list[0])};'''
        self.cur.execute(sql)
        self.remote.commit()

    def insertDB(self, table_name, values):
        s = ",".join(["%s" for _ in range(len(values))])
        self.cur.execute(f"INSERT INTO {table_name} VALUES (NULL, {s})", tuple(values))
        self.remote.commit()
    
    def getRecentPetID(self):
        self.cur.execute(f"SELECT pet_id FROM pet ORDER BY pet_id DESC LIMIT 1;")
        id = self.cur.fetchall()[0][0]
        # print(id)
        return str(id)

    def getLog(self, key, pet_id):
        self.cur.execute(f"SELECT * FROM petchecker WHERE pet_id = {int(pet_id)} ORDER BY petchecker_id DESC LIMIT 7;")
        temp_li = [key]
        for row in reversed(self.cur.fetchall()):
            # print(row)
            temp_li.append(",".join([str(row[i]) for i in range(2,7)]))

        return "&&".join(temp_li)

def receiveTCPControllerEvent(server_socket0, myWindows):
    global tcp_controller_read_flag, client_first_init_flag
    print("tcp 8080 대기 중")

    # 클라이언트 연결 대기
    print("컨트롤러 연결 대기")
    client_socket, client_address = server_socket0.accept()
    # client_socket.settimeout(5.0)
    print(f"컨트롤러 {client_address}가 연결되었습니다.")
    
    while tcp_controller_read_flag is True:
        if not tcp_controller_read_flag:
            break
        try:
            # 클라이언트로부터 요청 받기
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                continue
            
            # 요청 파싱
            parts = data.split("&&")
            # print(parts)
            if len(parts) != 0:
                myWindows.Controller_flag = not myWindows.Controller_flag
                myWindows.ledController.setStyleSheet(f"background-color: {"yellow" if myWindows.Controller_flag else "gray"};border: 1px solid black;") 

                # key = parts[0]
                # message = parts[1]
                response = "01" + "Idle"
                # every 1sec
                if parts[0] == "PetChecker Sync Data":
                    myWindows.pet_temperature = float(parts[1])
                    myWindows.pet_heart_rate = int(parts[2])
                    myWindows.pet_calorie = float(parts[3])
                    myWindows.pet_status = parts[4]
                    myWindows.pet_lay = int(parts[5])
                    myWindows.pet_walk = int(parts[6])
                    myWindows.pet_run = int(parts[7])


                    myWindows.labelTempBody.setText(parts[1])
                    myWindows.labelPulse.setText(parts[2])

                    myWindows.labelActivity.setText(parts[4])

                    myWindows.pet_calorie_sum += myWindows.pet_calorie
                    if myWindows.pet_status == "쉬는 중":
                        myWindows.status_log[0] += 1
                    elif myWindows.pet_status == "걷는 중":
                        myWindows.status_log[1] += 1
                    elif myWindows.pet_status == "달리는 중":
                        myWindows.status_log[2] += 1


                    myWindows.pet_check_cnt += 1
                    # print(myWindows.pet_check_cnt)
                    if myWindows.pet_check_cnt >= 60:
                        values = [myWindows.petID, 
                                  myWindows.now_time, 
                                  myWindows.pet_calorie_sum, 
                                  myWindows.status_log[0],
                                  myWindows.status_log[1],
                                  myWindows.status_log[2]]
                        myWindows.insertDB("petchecker", values)

                        myWindows.pet_check_cnt =0
                        myWindows.status_log = [0,0,0]
                        myWindows.pet_calorie_sum = 0

                    if client_first_init_flag:
                        client_first_init_flag = False
                        response = "02" + str(myWindows.petName) + "&" + str(myWindows.contactNumber)
                    
 
            else:
                response = "00" + "MessageError"

            # 응답 클라이언트에게 전송
            client_socket.send(response.encode("utf-8"))

        except Exception as e:
            print(f"오류 발생: {e}")

        finally:
            pass
            # 클라이언트 소켓 닫기
            # print("연결종료")
            # client_socket.close()
    server_socket0.close()
    client_socket.close()
    print("TCP0 종료")
    return

def receiveTCPClientEvent(server_socket1, myWindows, serial_socket):
    global tcp_client_read_flag, client_first_init_flag
    print("tcp 8081 대기 중")
    

    while tcp_client_read_flag is True:
        # 클라이언트 연결 대기
        # print("클라이언트 연결 대기")
        client_socket, client_address = server_socket1.accept()
        # client_socket.settimeout(0.01)
        # time.sleep(0.1) 

        myWindows.labelClientAddr.setText(client_address[0])
        # print(f"클라이언트 {client_address}가 연결되었습니다.")
        # client_socket.settimeout(5.0)

        if not tcp_client_read_flag:
            break
        try:
            # 클라이언트로부터 요청 받기
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                continue

            
            # 요청 파싱
            parts = data.split("&&")
            if len(parts) != 0:

                # print(parts)
                myWindows.Client_flag = not myWindows.Client_flag
                myWindows.ledClient.setStyleSheet(f"background-color: {"yellow" if myWindows.Client_flag else "gray"};border: 1px solid black;") 

                # if not parts[0] == "Sync Data" and not parts[0] == "Request WebCam Image":
                print(parts)

                if parts[0] == "Client First Init":
                    response = myWindows.fetchClientFirstInit(parts[1])
                    client_socket.send(response.encode("utf-8"))
                    client_first_init_flag = True

                    print(myWindows.recent_feed_time)
                elif parts[0] == "Update Pet ":
                    # TODO: UPDATE pet SET pet_name="Ham, Dong-Gyun" WHERE pet_id=1;
                    f'''
                    UPDATE pet 
                    SET 
                        pet_name={str(0)}, 
                        pet_birthday={str(0)}, 
                        pet_weight={float(0)}, 
                        pet_species={str(0)}, 
                        pet_contact_number={str(0)} 
                    WHERE pet_id={0};
                    '''
                    pass
                elif parts[0] == "insert Pet ":
                    # TODO: UPDATE pet SET pet_name="Ham, Dong-Gyun" WHERE pet_id=1;
                    pass
                elif parts[0] == "Sync Data":
                    response = []
                    response.append("Sync Data")
                    response.append(str(myWindows.feeder_humidity))
                    response.append(str(myWindows.feeder_temperature))
                    response.append(str(myWindows.feeder_hic))
                    response.append(str(myWindows.feeder_water_level))
                    response.append(str(myWindows.feeder_food_level))

                    response.append(str(myWindows.pet_temperature))
                    response.append(str(myWindows.pet_heart_rate))
                    response.append(str(myWindows.pet_calorie))
                    response.append(str(myWindows.pet_status))

                    response = "&&".join(response)

                    client_socket.send(response.encode("utf-8"))
                elif parts[0] == "WebCam Control":
                    key10 = 1 if parts[1] == "up" else 2 if parts[1] == "down" else 3 if parts[1] == "left" else 4
                    key01 = 1 if parts[2] == "start" else 0

                    key = key10 * 10 + key01
                    message = parts[0] # "WebCam Control"
                    sendSerial(serial_socket, key, message)
                elif parts[0] == "Request WebCam Image":

                    resize_frame = cv2.resize(myWindows.img, dsize=(320, 250), interpolation=cv2.INTER_AREA)

                    # now = time.localtime()
                    # stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                    _, imgencode = cv2.imencode('.jpg', resize_frame, encode_param)
                    data = np.array(imgencode)
                    stringData = base64.b64encode(data)
                    length = str(len(stringData))
                    client_socket.sendall(length.encode('utf-8').ljust(64))
                    client_socket.send(stringData)
                    # client_socket.send(stime.encode('utf-8').ljust(64))
                elif parts[0] == "WebCam Control Saved Place":
                    # 1. DB에 저장되어 있는 x, y값 가져올 것
                    # 2. 시리얼로 보낼 것

                    key = "53"
                    message = myWindows.getPosition(parts[1], parts[2])
                    # print(key, message)
                    sendSerial(serial_socket, key, message)
                    pass
                elif parts[0] == "WebCam Fetch Place":
                    response = myWindows.requestFetchPlace(parts[1])
                    client_socket.send(response.encode("utf-8"))
                elif parts[0] == "WebCam Save Place":
                    myWindows.savePlace(parts[1], parts[2])

                    response = myWindows.requestFetchPlace(parts[1])
                    client_socket.send(response.encode("utf-8"))
                elif parts[0] == "WebCam Delete Place":
                    myWindows.deletePlace(parts[1], parts[2])

                    response = myWindows.requestFetchPlace(parts[1])
                    client_socket.send(response.encode("utf-8"))
                elif parts[0] == "Feeding Schedule":
                    myWindows.updateFeedingSchedule(parts[1:])
                    _ = myWindows.fetchClientFirstInit(parts[1])
                    print(myWindows.recent_feed_time)
                elif parts[0] == "User Modify":
                    myWindows.updatePET(parts[1:])

                    response = myWindows.fetchClientFirstInit(parts[1])
                    client_socket.send(response.encode("utf-8"))
                    client_first_init_flag = True
                elif parts[0] == "User Register":
                    myWindows.insertDB("pet", parts[1:])

                    id = myWindows.getRecentPetID()
                    response = myWindows.fetchClientFirstInit(id)
                    client_socket.send(response.encode("utf-8"))
                    client_first_init_flag = True
                elif parts[0] == "Activity Log":
                    # print("Activity Log!!!!")
                    response = myWindows.getLog(parts[0], parts[1])
                    # print(response)
                    client_socket.send(response.encode("utf-8"))
            else:
                response = "유효하지 않은 요청"
                print("Key Error")

            # 응답 클라이언트에게 전송
            # client_socket.send(response.encode("utf-8"))

        except Exception as e:
            print(f"오류 발생: {e}")

        finally:
            pass
            # 클라이언트 소켓 닫기
            # print("클라이언트 연결종료")
            client_socket.close()
    
    server_socket1.close()
    client_socket.close()
    print("TCP1 종료")
    return

def sendSerial(serial_socket, key=0, message=""):
    output = f"{key:02}" + message
    serial_socket.write(output.encode())
    time.sleep(0.1)

def receiveSerialEvent(py_serial, myWindows):
    global sefial_read_flag0
    serial_read_data = ["start serial"]
    print("serial 대기 중")
    while sefial_read_flag0 is True:
        datos = py_serial.read_until().decode('ascii').strip()
        # print(datos)
        serial_read_data.append(datos)
        if datos == "end serial":
            # print("Serial Read!!")
            # print("Serial Read!!", serial_read_data)

            # check Key
            if serial_read_data[1] == "Feeder Sencing Data":
                # myWindows.labelTempBody.setText(serial_read_data[3][:2])
                # db에 저장하면 좋은가
                myWindows.feeder_humidity = serial_read_data[2]
                myWindows.feeder_temperature = serial_read_data[3]
                myWindows.feeder_hic = serial_read_data[4]
                myWindows.feeder_water_level = serial_read_data[5]
                # myWindows.food_level = serial_read_data[6]

                myWindows.labelEnvTemp.setText(str(serial_read_data[3]) + "°C")
                myWindows.labelEnvHum.setText(str(serial_read_data[2]) + "%")
                myWindows.labelWaterBowlLevel.setText(str(serial_read_data[5]))
            elif serial_read_data[1] == "WebCam Control":
                myWindows.up_down_angle = serial_read_data[2]
                myWindows.left_right_angle = serial_read_data[3]

                myWindows.labelCamCurV.setText(serial_read_data[2])
                myWindows.labelCamCurH.setText(serial_read_data[3])

                # print(myWindows.up_down_angle, myWindows.left_right_angle)
            elif serial_read_data[1] == '3':
                '''
                TODO:
                1. 배식기에서 온습도(h, t, hic) 정보, 압력센서 정보, 수위 센서 정보, 초음파 센서 정보, 현재 서보들의 각도 정보 받아옴
                2. 이를 DB에 저장해야함
                '''
                pass

            serial_read_data = ["start serial"]
    return

if __name__=="__main__":
    # GUI 생성
    app = QApplication(sys.argv)

    # 시리얼 포트, 버레이트 설정
    py_serial0 = serial.Serial("/dev/ttyACM0", 9600)    # Feeder
    py_serial1 = serial.Serial("/dev/ttyACM1", 9600)    # Comunicator
    # py_serial0 = 0

    # 서버 설정
    host0 = "192.168.2.29"  # 서버의 IP 주소 또는 도메인 이름
    port0 = 8080       # 포트 번호
    # 서버 소켓 생성
    server_socket0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket0.bind((host0, port0))
    server_socket0.listen(5)
    # server_socket0.settimeout(5.0)

    # 서버 설정
    host1 = "192.168.2.29"  # 서버의 IP 주소 또는 도메인 이름
    port1 = 8081       # 포트 번호
    # 서버 소켓 생성
    server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket1.bind((host1, port1))
    server_socket1.listen(5)
    # server_socket1.settimeout(5.0)

    # 쓰레드 생성 및 시작
    myWindows = WindowClass(py_serial0, py_serial1, server_socket0, server_socket1)
    serial0_thread = threading.Thread(target=receiveSerialEvent,
                                     args=(py_serial0, myWindows))
    serial1_thread = threading.Thread(target=receiveSerialEvent,
                                     args=(py_serial1, myWindows))
    tcp_controller_thread = threading.Thread(target=receiveTCPControllerEvent, 
                                  args=(server_socket0, myWindows))
    tcp_cient_thread = threading.Thread(target=receiveTCPClientEvent, 
                                  args=(server_socket1, myWindows, py_serial1))

    myWindows.show()
    serial0_thread.start()
    serial1_thread.start()
    tcp_controller_thread.start()
    tcp_cient_thread.start()
    sys.exit(app.exec_())



