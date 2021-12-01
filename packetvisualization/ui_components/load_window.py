from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QProgressBar


class LoadWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(20, 20, 400, 50)
        self.widget = QWidget()

        self.layout = QVBoxLayout()

        self.progress = QProgressBar()
        # self.progress.setGeometry()

        self.status = QLabel("Loading")

        self.widget.setLayout(self.layout)

        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.status)

        self.setCentralWidget(self.widget)
