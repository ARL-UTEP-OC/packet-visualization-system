from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar, QDesktopWidget, QPushButton, \
    QGridLayout


class LoadWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Workspace")
        self.setWindowIcon(QIcon(":logo.png"))
        self.setGeometry(20, 20, 400, 50)
        self.widget = QWidget()

        self.layout = QGridLayout()

        self.progress = QProgressBar()
        self.status = QLabel("Loading")

        self.ok = QPushButton("OK")
        self.ok.clicked.connect(self.close)
        self.ok.setFixedWidth(100)
        self.ok.setEnabled(False)

        self.widget.setLayout(self.layout)

        self.layout.addWidget(self.progress, 0, 0, 1, 2)
        self.layout.addWidget(self.status, 1, 0)
        self.layout.addWidget(self.ok, 1, 1)

        self.setCentralWidget(self.widget)

        # Center window on the screen
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
