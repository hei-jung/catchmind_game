import sys
import socket
import threading
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MyApp(QWidget):
    """
    맞추기
    """

    def __init__(self):
        super().__init__()
        self.HOST = '127.0.0.1'  # ip 주소
        self.PORT = 9999  # 포트
        # 소켓 준비
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        self.initUI()  # UI 초기화
        self.file_name = ""  # 파일명을 담아놓는다(사진, 그림 파일)
        self.photo = None  # 정답 맞출 때까지 임시로 사진 데이터를 담아놓는다

    def initUI(self):
        self.setWindowTitle('GUESS')  # 창 제목

        self.vbox = QVBoxLayout()  # 위젯들을 담을 레이아웃

        # 정답을 맞췄을 경우 사진을 띄울 이미지 레이블
        self.pixmap_photo = QPixmap(200, 200)
        self.lbl_photo = QLabel()
        self.lbl_photo.setPixmap(self.pixmap_photo)
        self.vbox.addWidget(self.lbl_photo)

        # 그림 띄울 이미지 레이블
        self.pixmap_img = QPixmap(200, 200)
        self.lbl_img = QLabel()
        self.lbl_img.setPixmap(self.pixmap_img)
        self.vbox.addWidget(self.lbl_img)

        # 정답 제출 / 채팅창 시작
        self.btn_start = QPushButton('시작!', self)
        self.btn_start.clicked.connect(self.startChat)
        self.vbox.addWidget(self.btn_start)

        # '정답:' 텍스트 레이블
        self.lbl_answer = QLabel('정답:')
        self.vbox.addWidget(self.lbl_answer)

        # 답안 입력창
        self.text_answer = QTextEdit()
        self.text_answer.setAcceptRichText(False)
        self.text_answer.setEnabled(False)
        self.vbox.addWidget(self.text_answer)

        # 정답 제출하는 버튼
        self.btn_answer = QPushButton('제출', self)
        self.btn_answer.clicked.connect(self.submit)
        self.btn_answer.setEnabled(False)
        self.vbox.addWidget(self.btn_answer)

        # 실시간 채팅 보여주는 텍스트 레이블
        self.lbl_chat = QLabel('채팅내용')
        self.vbox.addWidget(self.lbl_chat)

        # 채팅 입력창
        self.text_chat = QTextEdit()
        self.text_chat.setEnabled(False)
        self.vbox.addWidget(self.text_chat)

        # 채팅 전송 버튼
        self.btn_chat = QPushButton('전송', self)
        self.btn_chat.setEnabled(False)
        self.btn_chat.setShortcut('Alt+F7')  # 단축키 설정: Alt + F7
        self.btn_chat.clicked.connect(self.send_msg)
        self.vbox.addWidget(self.btn_chat)

        self.vbox.addStretch()  # 레이아웃 안의 위젯 수직 배치
        self.setLayout(self.vbox)  # 레이아웃 구현

    def submit(self):
        msg = self.text_answer.toPlainText()  # 입력창의 텍스트를 가져와서 msg에 저장
        msg = '/0002%' + msg + '%catch'  # 정답 보낼 때는 '/0002%정답%catch' 형태로
        self.client_socket.sendall(msg.encode())  # 서버로 전송

    def send_msg(self):
        # '전송' 버튼 누르면 실행되는 코드
        msg = self.text_chat.toPlainText()  # 입력창의 텍스트를 가져와서 msg에 저장
        msg = '/0003%' + msg  # 채팅 메시지는 '/0003%메시지' 형태로
        self.client_socket.sendall(msg.encode())  # 서버로 전송

        # 안전 종료 코드
        if msg.endswith('/stop'):
            self.lbl_chat.setText("프로그램이 종료되었습니다. 창을 닫아주세요.")
            self.btn_answer.close()
            self.btn_chat.close()

    def read_msg(self):
        while True:  # 채팅 메시지는 실시간으로 계속 받아와야 하므로 무한 루프로
            data = self.client_socket.recv(1024)
            msg = data.decode()
            # print(msg)
            if msg == '/0001%photo':
                # 서버에서 사진 보낼 경우
                self.file_name = 'photo_answer.png'
                self.photo = self.client_socket.recv(50000)
                print('photo received')
                f = open(file=self.file_name, mode='wb')
                f.write(self.photo)
                f.close()
            elif msg == '/0001%image':
                # 서버에서 그림 보낼 경우
                self.file_name = 'img_from_server.png'
                img = self.client_socket.recv(50000)
                print('image received')
                f = open(file=self.file_name, mode='wb')
                f.write(img)
                f.close()
                self.lbl_img.setPixmap(QPixmap(self.file_name))
                # 정답 맞추기 활성화
                self.text_answer.setEnabled(True)
                self.btn_answer.setEnabled(True)
            elif msg.startswith('/0001%answer'):
                # 서버에서 정답을 보냄(그냥 기다림)
                print('server loading answer')
            elif msg == '/0001%CAUGHT':
                # 정답 맞췄을 떄
                self.lbl_chat.setText('정답! 게임 종료')
                self.lbl_photo.setPixmap(QPixmap('photo_answer.png'))
            elif msg == '/stop':
                # 안전 종료 코드
                break
            else:
                self.lbl_chat.setText(msg)  # 텍스트 레이블을 새 메시지로 고쳐줌
        self.client_socket.close()  # 채팅이 종료되면 소켓을 닫음

    def startChat(self):
        # '시작' 버튼 누르면 채팅에 참여할 수 있다.
        self.btn_start.close()  # 버튼 제거
        # 채팅 활성화
        self.text_chat.setEnabled(True)
        self.btn_chat.setEnabled(True)

        t_send = threading.Thread(target=self.send_msg, args=())
        t_send.start()  # 전송 스레드
        t_read = threading.Thread(target=self.read_msg, args=())
        t_read.start()  # 읽기 스레드


def run():
    # 실행 코드
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())


run()
