
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import cv2, imutils
import PyQt5
from PyQt5.QtCore import *

import time

import threading
import socket

from_class = uic.loadUiType("/home/hdk/ws/pyqt/data/opencv.ui")[0]




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
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.isCameraOn = False
        self.camera = Camera(self)
        self.camera.daemon = True
        self.count = 0

        self.pixmap = QPixmap()
        self.btn_open.clicked.connect(self.openFile)
        self.btn_camera_onoff.clicked.connect(self.cameraOnOffClicked)
        self.camera.update.connect(self.updateCamera)


    def updateCamera(self):
        # self.label.setText("Camera Running : " + str(self.count))
        # self.count += 1
        retval, img = self.video.read()

        if retval:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            h,w,c = img.shape
            qimg = QImage(img.data, w,h,w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimg)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            self.label.setPixmap(self.pixmap)
        self.count += 1

    def cameraOnOffClicked(self):
        if self.isCameraOn == False:
            print("Camera On")
            self.isCameraOn = True
            self.cameraStart()
            self.video = cv2.VideoCapture(-1)

        elif self.isCameraOn == True:
            print("Camera off")
            self.isCameraOn = False
            self.cameraStop()
            self.video.release()

    def cameraStart(self):
        self.camera.running = True
        self.camera.start()

    def cameraStop(self):
        self.camera.running = False
        self.count = 0

    def openFile(self):
        file = QFileDialog.getOpenFileName(filter='Image (*.*)')

        img = cv2.imread(file[0])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        h,w,c = img.shape
        qimg = QImage(img.data, w, h, w*c, QImage.Format_RGB888)

        self.pixmap = self.pixmap.fromImage(qimg)
        self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

        self.label.setPixmap(self.pixmap)

def receiveTCPEvent(server_socket, tcp_read, myWindows):
    while tcp_read is True:
        # 클라이언트 연결 대기
        client_socket, client_address = server_socket.accept()
        print(f"클라이언트 {client_address}가 연결되었습니다.")
        
        try:
            # 클라이언트로부터 요청 받기
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                continue

            # 요청 파싱
            parts = data.split("&&")
            if len(parts) != 0:
                name = parts[0]
                message = parts[1]
                response = f"어서와! {name}"

                # 클라이언트 이름과 메시지 출력
                print(f"클라이언트 이름: {name}")
                print(f"클라이언트 메시지: {message}")
            else:
                response = "유효하지 않은 요청"

            # 응답 클라이언트에게 전송
            client_socket.send(response.encode("utf-8"))

        except Exception as e:
            print(f"오류 발생: {e}")

        finally:
            pass
            # 클라이언트 소켓 닫기
            print("연결종료")
            client_socket.close()
    return



if __name__=="__main__":
    # GUI 생성
    app = QApplication(sys.argv)
    myWindows = WindowClass()

    # 서버 설정
    tcp_read = True
    host = "0.0.0.0"  # 서버의 IP 주소 또는 도메인 이름
    port = 8080       # 포트 번호

    # 서버 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    # 쓰레드 생성 및 시작
    tcp_thread = threading.Thread(target=receiveTCPEvent, 
                                  args=(server_socket, tcp_read, myWindows))
    tcp_thread.start()

    # GUI 시작
    myWindows.show()
    sys.exit(app.exec_())
    print("Program End.")


