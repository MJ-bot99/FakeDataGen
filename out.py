import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Generator sign in")
        self.setGeometry(100, 100, 448, 314)
        self.setStyleSheet(self.get_main_style())
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # Title
        title = QLabel("Fake Data Generator")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Generate data easily")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(30)

        # Form Wrapper
        form = QFrame()
        form.setObjectName("form")

        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # Tab buttons
        tab = QHBoxLayout()
        tab.setSpacing(0)

        btn_signin = QPushButton("Sign IN")
        btn_signin.setObjectName("TabSignIN")
        btn_signin.setFont(QFont("Arial", 14))

        btn_signup = QPushButton("Sign UP")
        btn_signup.setObjectName("TabSignUP")
        btn_signup.setFont(QFont("Arial", 14))

        tab.addWidget(btn_signin)
        tab.addWidget(btn_signup)

        form_layout.addLayout(tab)

        main_layout.addWidget(form)

    def get_main_style(self):
        return """
            QWidget {
                background-color: #F8F9FA;
            }

            #title {
                font-size: 28px;
                font-weight: bold;
                color: #333;
            }
            #subtitle {
                font-size: 14px;
                color: #666;
            }

            #form {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 15px;
            }

            #TabSignIN {
                background-color: white;
                color: #333;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                padding: 10px 20px;
            }

            #TabSignUP {
                background-color: #F8F9FA;
                color: #666;
                border: 1px solid #E0E0E0;
                border-left: none;
                padding: 10px 20px;
            }
        """