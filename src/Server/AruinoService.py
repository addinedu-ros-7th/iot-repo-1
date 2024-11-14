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
    def __init__(self, py_serial, server_socket0, server_socket1):
        super().__init__()
        self.setupUi(self)

        self.isCameraOn = False
        self.camera = Camera(self)
        self.camera.daemon = True
        self.img = np.zeros((100,100))
        self.qimg = None
        self.count = 0
        self.pixmap = QPixmap()

        self.server_socket0 = server_socket0
        self.server_socket1 = server_socket1
        self.py_serial = py_serial

        self.petID = None
        self.petName = None
        self.petBirth = None
        self.petWeight = None
        self.petSpecies = None
        self.contactNumber = None

        # Comunicator
        self.up_down_angle = 90
        self.left_right_angle = 90

        # Feeder
        self.feeder_humidity = 0
        self.feeder_temperature = 0
        self.feeder_hic = 0
        self.feeder_water_level = 0
        self.feeder_food_level = 0

        # Pet Checker
        self.pet_temperature = 0
        self.pet_heart_rate = 0

        self.remote = mysql.connector.connect(
            host = "database-1.c3micoc2s6p8.ap-northeast-2.rds.amazonaws.com",
            user = "aru",
            password = "1234",
            database = "aruino"
        )
        self.cur = self.remote.cursor(buffered=True)

        self.camera.update.connect(self.updateCamera)
        self.isCameraOn = True
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture("/dev/video2")

    def updateCamera(self):
        # self.label.setText("Camera Running : " + str(self.count))
        # self.count += 1
        self.labelDateTime.setText(str(datetime.now())[:-7])
        retval, img = self.video.read()

        if retval:
            self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            h,w,c = img.shape
            self.qimg = QImage(self.img.data, w,h,w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(self.qimg)
            self.pixmap = self.pixmap.scaled(self.labelCam.width(), self.labelCam.height())

            self.labelCam.setPixmap(self.pixmap)
            # print(self.qimg)
            # print(img)
        # self.count += 1

        # send(qimg)

    def initUI(self):
        self.labelID.setText(str(self.petID))
        self.labelName.setText(str(self.petName))
        self.labelAge.setText(str(self.petBirth))
        self.labelWeight.setText(str(self.petWeight))
        self.labelSpecies.setText(str(self.petSpecies))
        self.labelContactNumber.setText(str(self.contactNumber))

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
        print("hello fetch")
        self.cur.execute(f"SELECT * FROM pet where id = {id}")
        print(self.cur)
        petInfo = self.cur.fetchall()
        self.petID = petInfo[0][0]
        self.petName = petInfo[0][1]
        self.petBirth = petInfo[0][2]
        self.petWeight = petInfo[0][3]
        self.petSpecies = petInfo[0][4]
        self.contactNumber = petInfo[0][5]
        self.initUI()

        response = []
        for val in petInfo[0]:
            response.append(str(val))
        print(response)
        return "&&".join(response)

    def requstDB(self, feed_index, feeding_amount, feeding_time):
        self.cur.execute("INSERT INTO feeding VALUES (%s, %s, %s)", (feed_index, feeding_amount, feeding_time))
        pass

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
            print(parts)
            if len(parts) != 0:
                # key = parts[0]
                # message = parts[1]
                response = "01" + "Idle"
                if parts[0] == "PetChecker Sync Data":
                    '''
                    TODO:
                    목걸이에서 위치, 심장박동, 체온, 가속도 등의 정보를 보냄
                    이를 받아 DB에 insert해야함

                    심장박동, 체온 등 건강 이상 증세가 보이면, 반복되면, 대응해야함
                    '''
                    # myWindows.x = parts[1]
                    # myWindows.y = parts[2]
                    # print("x:", myWindows.x)
                    # print("y:", myWindows.y)
                    print(parts[1:])

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
        myWindows.labelClientAddr.setText(client_address)
        # client_socket.settimeout(5.0)
        # print(f"클라이언트 {client_address}가 연결되었습니다.")
        if not tcp_client_read_flag:
            break
        try:
            # 클라이언트로부터 요청 받기
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                continue

            # 요청 파싱
            parts = data.split("&&")
            print(parts)
            if len(parts) != 0:
                if parts[0] == "Client First Init":
                    response = myWindows.fetchClientFirstInit(parts[1])
                    client_socket.send(response.encode("utf-8"))
                    client_first_init_flag = True
                    
                elif parts[0] == "Sync Data":
                    response = []
                    response.append("Sync Data")
                    response.append(str(myWindows.h))
                    response.append(str(myWindows.t))
                    response.append(str(myWindows.hic))
                    response.append(str(myWindows.x))
                    response.append(str(myWindows.y))
                    response = "&&".join(response)

                    client_socket.send(response.encode("utf-8"))
                elif parts[0] == "WebCam Control":
                    key10 = 1 if parts[1] == "up" else 2 if parts[1] == "down" else 3 if parts[1] == "left" else 4
                    key01 = 1 if parts[2] == "start" else 0

                    key = key10 * 10 + key01
                    message = parts[0] # "WebCam Control"
                    sendSerial(serial_socket, key, message)
                elif parts[0] == "Request WebCam Image":

                    resize_frame = cv2.resize(myWindows.img, dsize=(670, 520), interpolation=cv2.INTER_AREA)

                    # now = time.localtime()
                    stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                    _, imgencode = cv2.imencode('.jpg', resize_frame, encode_param)
                    data = np.array(imgencode)
                    stringData = base64.b64encode(data)
                    length = str(len(stringData))
                    client_socket.sendall(length.encode('utf-8').ljust(64))
                    client_socket.send(stringData)
                    client_socket.send(stime.encode('utf-8').ljust(64))
                elif parts[0] == "Request DB":
                    pass
                
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
                myWindows.h = serial_read_data[2]
                myWindows.t = serial_read_data[3]
                myWindows.hit = serial_read_data[4]
                myWindows.water_level = serial_read_data[5]
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
    py_serial0 = serial.Serial("/dev/ttyACM0", 9600)
    py_serial1 = serial.Serial("/dev/ttyACM1", 9600)
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
    myWindows = WindowClass(py_serial0, server_socket0, server_socket1)
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



