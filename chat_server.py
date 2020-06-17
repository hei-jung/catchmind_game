import sys
from PyQt5.QtWidgets import *
import socket
import threading
from time import sleep


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.HOST = '127.0.0.1'  # server ip. local host
        self.PORT = 9999  # server port
        self.clients = []  # 채팅방. 연결된 클라이언트 소켓
        self.initUI()  # UI 초기화
        self.answer = ""  # 정답을 담아놓는다

    def initUI(self):
        self.setWindowTitle('SERVER')  # 제목
        self.move(300, 300)  # 스크린의 x=300px, y=300px 위치로 이동
        self.resize(400, 200)  # 크기: 400x200

        self.openBtn = QPushButton('open server', self)  # 버튼 생성
        self.openBtn.setGeometry(150, 100, 100, 30)  # (x=150, y=100, 가로:100, 세로:30)
        self.openBtn.clicked.connect(self.server_open)  # 버튼 이벤트 핸들러: 서버 오픈

    def broadcast(self, msg):
        # 모든 참가자들에게 채팅 메시지를 전달함
        for s in self.clients:
            s.sendall(msg.encode())

    def client(self, soc, addr):
        self.clients.append(soc)  # 방금 접속한 클라이언트 소켓을 리스트에 담음

        while True:
            data = soc.recv(1024)
            msg = data.decode()
            print('Received from', addr, msg)
            if msg.endswith('/stop'):
                soc.sendall(data)  # 본인한테 /stop 전송
                self.clients.remove(soc)
                msg = str(addr) + ' 님이 퇴장하였습니다.'
                for s in self.clients:
                    s.sendall(msg.encode())
                break
            elif msg.startswith('/0003'):
                # '/0003'으로 시작하는 메시지는 채팅 메시지
                msg = msg.split('%')
                msg = str(addr) + ' : ' + msg[1]
                self.broadcast(msg)
            elif msg == '/0001%wait for photo':
                # '사진' 쪽에서 이미지 파일을 보내줌
                photo = soc.recv(50000)
                print('photo loaded')
                for s in self.clients:
                    s.send('/0001%photo'.encode())
                    sleep(1)
                    s.sendall(photo)
            elif msg == '/0001%wait for image':
                # '그림' 쪽에서 이미지 파일을 보내줌
                img = soc.recv(50000)
                print('image loaded')
                for s in self.clients:
                    s.send('/0001%image'.encode())
                    sleep(1)
                    s.sendall(img)
            elif msg.startswith('/0002') and msg.endswith('%answer'):
                # '사진' 쪽에서 정답을 보내줌
                ans = msg.split('%')
                self.answer = ans[1]
                self.broadcast('/0001%answer%' + ans[1])
            elif msg.startswith('/0002') and msg.endswith('%catch'):
                # '맞추기' 쪽에서 답을 보내줌
                msg = msg.split('%')
                guess = msg[1]
                if self.answer == guess:
                    # 답을 맞췄을 경우
                    self.broadcast('/0001%CAUGHT')

        soc.close()
        print(addr, '퇴장')

    def server_open(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()
        print('server start')
        self.destroy()  # 'open server' 버튼 누르면 창 닫히도록

        # accept로 client의 접속을 기다리다 요청시 처리.
        # client와 1:1통신할 작은 소켓과 연결된 상대방의 주소 반환
        while True:
            client_socket, addr = self.server_socket.accept()
            print('Connected by', addr)
            t = threading.Thread(target=self.client, args=(client_socket, addr))
            t.start()


# 실행
def run():
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())


run()
