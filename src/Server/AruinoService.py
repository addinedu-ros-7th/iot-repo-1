
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

from_class = uic.loadUiType("project/iot-repo-1/src/Client/Main.ui")[0]
tcp_read = True


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

def receiveTCPEvent(server_socket, myWindows):
    global tcp_read
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
                key = parts[0]
                message = parts[1]
                response = f"어서와! {key}"

                # 클라이언트 이름과 메시지 출력
                print(f"클라이언트 Key: {key}")
                print(f"클라이언트 메시지: {message}")
                myWindows.label_14.setText(key)
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
    host = "0.0.0.0"  # 서버의 IP 주소 또는 도메인 이름
    port = 8080       # 포트 번호

    # 서버 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.settimeout(2)
    server_socket.bind((host, port))
    server_socket.listen(5)

    # 쓰레드 생성 및 시작
    tcp_thread = threading.Thread(target=receiveTCPEvent, 
                                  args=(server_socket, myWindows))
    tcp_thread.start()

    print("tcp 대기 중")

    # GUI 시작
    myWindows.show()
    sys.exit(app.exec_())
    print("Program End.")



