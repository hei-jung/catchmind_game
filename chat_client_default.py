import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import socket


class MyApp(QWidget):
    """
    채팅화면 기본설정.
    사진/그림/맞추기용 따로 만들어야 함.
    사진: 사진 촬영, 파일로 저장, 그림 쪽에 전송. 정답을 적어서 서버와 그림 쪽에 전송
    그림: 사진 파일 받으면 그림판 열림. 그림 완성하면 사진/맞추기 쪽에 전송
    맞추기: 정답을 맞추기 전까지는 그림만 보임.
    """

    def __init__(self):
        super().__init__()
        self.HOST = '127.0.0.1'
        self.PORT = 9999
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Player Default')
        self.move(300, 300)
        self.resize(600, 600)

        self.vbox = QVBoxLayout()

        self.pixmap_photo = QPixmap(200, 200)
        # self.pixmap_photo = QPixmap("default.png")
        self.pixmap_img = QPixmap(200, 200)
        # self.pixmap_img = QPixmap("default.png")

        self.lbl_photo = QLabel()
        # self.lbl_photo.setGeometry(0,100,10,10)
        self.lbl_photo.setPixmap(self.pixmap_photo)
        self.lbl_img = QLabel()
        # self.lbl_img.setGeometry(50,100,10,10)
        self.lbl_img.setPixmap(self.pixmap_img)
        self.vbox.addWidget(self.lbl_photo)
        self.vbox.addWidget(self.lbl_img)

        self.lbl_answer = QLabel('정답:')
        # self.lbl_answer.setGeometry(150,100,100,30)
        self.vbox.addWidget(self.lbl_answer)

        self.text_answer = QTextEdit()
        # self.text_answer.setGeometry(50,100,300,10)
        self.text_answer.setAcceptRichText(False)
        self.vbox.addWidget(self.text_answer)

        self.btn_answer = QPushButton('제출', self)
        # self.btn_answer.setGeometry(400, 400, 50, 30)
        self.btn_answer.clicked.connect(self.submit)
        self.vbox.addWidget(self.btn_answer)

        self.lbl_chat = QLabel('채팅내용')
        self.vbox.addWidget(self.lbl_chat)

        self.text_chat = QTextEdit()
        self.vbox.addWidget(self.text_chat)

        self.btn_chat = QPushButton('전송', self)
        # self.btn_chat.setGeometry(600, 400, 50, 30)
        self.btn_chat.clicked.connect(self.send_msg)
        self.vbox.addWidget(self.btn_chat)

        self.vbox.addStretch()
        self.setLayout(self.vbox)

        # self.show()

    def submit(self):
        msg = self.text_answer.toPlainText()
        msg = '/0002%' + msg
        self.client_socket.sendall(msg.encode())

    def send_msg(self):
        global flag
        msg = self.text_chat.toPlainText()
        msg = '/0003%' + msg
        self.client_socket.sendall(msg.encode())

        data = self.client_socket.recv(1024)
        msg = data.decode()
        self.lbl_chat.setText(msg)

        # 강제 종료 코드
        if msg.endswith('/stop'):
            self.lbl_chat.setText("프로그램이 종료되었습니다. 창을 닫아주세요.")
            self.client_socket.close()
            self.btn_answer.close()
            self.btn_chat.close()


def run():
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())


run()
