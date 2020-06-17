import sys
import socket
import threading
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

save_flag = False  # 그림 파일 저장 여부를 확인하는 플래그


class DrawImage(QMainWindow):
    """그림판"""

    def __init__(self):
        super().__init__()
        self.image = QImage(QSize(200, 200), QImage.Format_RGB32)  # 그림판 생성
        self.image.fill(Qt.white)  # 초기상태: 빈화면 (배경 흰색으로 채움)
        self.drawing = False  # 그림 상태
        self.brush_size = 5  # 펜 굵기
        self.brush_color = Qt.black  # 펜 색깔: 검은색
        self.last_point = QPoint()  # 마우스 포인터
        self.initUI()  # UI 초기화

    def initUI(self):
        # '파일' 메뉴바: '저장', '지우기'
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('파일')

        # '저장'
        save_action = QAction('저장', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save)
        filemenu.addAction(save_action)

        # '지우기'
        clear_action = QAction('지우기', self)
        clear_action.setShortcut('Ctrl+C')
        clear_action.triggered.connect(self.clear)
        filemenu.addAction(clear_action)

        # 그림판 창 초기화
        self.setWindowTitle('Simple Painter')
        self.move(300, 300)
        self.setGeometry(300, 300, 200, 200)

    def paintEvent(self, e):
        # 그림 그리기
        canvas = QPainter(self)
        canvas.drawImage(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, e):
        # 마우스 왼쪽 버튼 누르고 있을 때, 그림 그리는 상태임(True)을 정의
        if e.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = e.pos()

    def mouseMoveEvent(self, e):
        # 마우스 커서 위치 따라 그림 그리기
        if (e.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(self.last_point, e.pos())
            self.last_point = e.pos()
            self.update()

    def mouseReleaseEvent(self, e):
        # 마우스 왼쪽 버튼에서 손을 떼면, 그림을 그리는 상태가 아님(False)
        if e.button() == Qt.LeftButton:
            self.drawing = False

    def save(self):
        global save_flag
        path = 'catch_image.png'  # 그림 파일명을 'catch_image.png'로 해서 저장
        self.image.save(path)
        save_flag = True  # 저장 플래그를 True로 바꿈('그리기' 버튼에 활용하기 위함)
        self.destroy()  # 저장하면 창 자동으로 끄기

    def clear(self):
        # 그림판 백지 상태로 만들기('지우기')
        self.image.fill(Qt.white)
        self.update()


class MyApp(QWidget):
    """
    그림
    """

    def __init__(self):
        super().__init__()
        self.HOST = '127.0.0.1'  # ip 주소
        self.PORT = 9999  # 포트
        # 소켓 준비
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        self.dialog = DrawImage()  # 그림판 생성
        self.initUI()  # UI 초기화
        self.file_name = ""  # 파일명을 담아놓는다(사진, 그림 파일)

    def initUI(self):
        self.setWindowTitle('DRAW')  # 창 제목

        self.vbox = QVBoxLayout()  # 위젯들을 담을 레이아웃

        # '그리기' 버튼: 이 버튼을 누르면 그림판이 뜨도록
        self.btn_draw = QPushButton('그리기', self)
        self.btn_draw.setEnabled(False)
        self.btn_draw.clicked.connect(self.draw)
        self.vbox.addWidget(self.btn_draw)

        # '사진' 역할에서 보낸 사진을 띄울 이미지 레이블
        self.pixmap_photo = QPixmap(200, 200)
        self.lbl_photo = QLabel()
        self.lbl_photo.setPixmap(self.pixmap_photo)
        self.vbox.addWidget(self.lbl_photo)

        # 내가 그린 그림을 띄울 이미지 레이블
        self.pixmap_img = QPixmap(200, 200)
        self.lbl_img = QLabel()
        self.lbl_img.setPixmap(self.pixmap_img)
        self.vbox.addWidget(self.lbl_img)

        # 정답 보여주는 텍스트 레이블
        self.lbl_answer = QLabel('')
        self.vbox.addWidget(self.lbl_answer)

        # 채팅창 시작
        self.btn_start = QPushButton('시작!', self)
        self.btn_start.clicked.connect(self.startChat)
        self.vbox.addWidget(self.btn_start)

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

    def draw(self):
        # '그리기' 버튼 누르면 실행되는 코드
        global save_flag
        self.btn_draw.setText('그림 확인 및 전송')  # 버튼 텍스트를 '그리기'에서 '그림 확인'으로 바꿈
        self.file_name = 'catch_image.png'  # 그림 파일명
        self.dialog.show()  # 그림판 창 띄우기
        if save_flag:  # 그림 파일이 한 번 저장됐으면,
            self.btn_draw.setEnabled(False)  # 버튼 비활성화
            self.lbl_img.setPixmap(QPixmap(self.file_name))  # 그림 레이블로 보여주기
            '''그림을 서버로 전송'''
            self.client_socket.sendall('/0001%wait for image'.encode())
            sleep(1)
            f = open(file=self.file_name, mode='rb')
            body = f.read()
            self.client_socket.sendall(body)
            f.close()

    def send_msg(self):
        # '전송' 버튼 누르면 실행되는 코드
        msg = self.text_chat.toPlainText()  # 입력창의 텍스트를 가져와서 msg에 저장
        msg = '/0003%' + msg  # 채팅 메시지는 '/0003%메시지' 형태로
        self.client_socket.sendall(msg.encode())  # 서버로 전송

        # 안전 종료 코드
        if msg.endswith('/stop'):
            self.lbl_chat.setText("프로그램이 종료되었습니다. 창을 닫아주세요.")
            self.btn_draw.close()
            self.btn_chat.close()

    def read_msg(self):
        while True:  # 채팅 메시지는 실시간으로 계속 받아와야 하므로 무한 루프로
            data = self.client_socket.recv(1024)
            msg = data.decode()
            # print(msg)
            if msg == '/0001%photo':
                # 서버에서 사진을 보낼 경우(저장)
                self.file_name = 'photo_from_server.png'
                photo = self.client_socket.recv(50000)
                print('photo received')
                f = open(file=self.file_name, mode='wb')
                f.write(photo)
                f.close()
                self.lbl_photo.setPixmap(QPixmap(self.file_name))
                self.btn_draw.setEnabled(True)
            elif msg == '/0001%image':
                # 서버에서 그림을 보낼 경우(그냥 기다림)
                img = self.client_socket.recv(50000)
                self.lbl_chat.setText('다른 플레이어에게 그림을 전달하는 중입니다.')
            elif msg.startswith('/0001%answer'):
                # 정답을 레이블로 보여줌
                answer = msg.split('%')
                self.lbl_answer.setText(answer[2])
            elif msg == '/0001%CAUGHT':
                # 다른 플레이어가 정답을 맞췄을 때
                self.lbl_chat.setText('정답! 게임 종료')
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
