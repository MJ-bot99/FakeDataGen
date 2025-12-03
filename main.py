import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from out import LoginForm

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial",10))
    window = LoginForm()
    window.show()
    sys.exit(app.exec_())