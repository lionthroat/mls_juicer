from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,  # Qt is for alignment
                          pyqtSignal, QEvent)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSplashScreen, QSplitter,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QTabWidget)
                             
class SceneryBanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #FFFFFF;")
        layout = QVBoxLayout()
        pixmap = QPixmap("assets/scenery_banner_static.png")

        # Create a QLabel to display the program's name image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setStyleSheet("background-color: #000000;")
        self.label.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)