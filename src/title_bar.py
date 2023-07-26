import sys
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,
                          pyqtSignal, QEvent)
from PyQt6.QtGui import QColor, QPixmap, QPalette, QIcon
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow, QFrame,
                             QMessageBox, QPushButton, QSplashScreen, QSplitter, QSizePolicy,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QTabWidget)

# Citation: inspiration for title bar widget in progress
# https://stackoverflow.com/questions/58901806/how-to-make-my-title-less-window-drag-able-in-pyqt5

class TitleBar(QWidget):
    # Create a custom signal to be emitted when the title bar is clicked
    titleBarClicked = pyqtSignal(QEvent)

    # Create a custom signal to be emitted when the "close" button is clicked
    close_signal = pyqtSignal()

    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #     self.parent = parent

    def __init__(self):
        super().__init__()
        self.offset = None

        # Set the margins and padding to 0
        self.setContentsMargins(0, 0, 0, 0)

        self.setAutoFillBackground(True)
        self.setStyleSheet(
            """
            QWidget{
                background-color: lightgray;
                color:dimgray;
                font:12px bold;
                font-weight:bold;
                border-radius: 5px;
                height: 25px;
                padding: 5px;
            }
            """
        )

        self.minimize=QPushButton(self)
        self.minimize.setIcon(QIcon('assets/min.png'))

        self.maximize=QPushButton(self)
        self.maximize.setIcon(QIcon('assets/max.png'))

        # CLOSE PROGRAM BUTTON - Creates button, adds image asset,
        # and finally connect to closeProgram method that will
        # emit the closeProgram signal to ProgramFrame
        close=QPushButton(self)
        close.setIcon(QIcon('assets/close.png'))
        close.clicked.connect(self.closeProgram)

        # Title bar label
        label=QLabel(self)
        label.setText("MLS Data Sorter")
        
        # Window buttons layout: minimize/maximize/close
        window_buttons_layout = QHBoxLayout(self)
        window_buttons_layout.addWidget(label)
        window_buttons_layout.addWidget(self.minimize)
        window_buttons_layout.addWidget(self.maximize)
        window_buttons_layout.addWidget(close)

        # Set margins/padding to zero for window buttons layout
        window_buttons_layout.setContentsMargins(0, 0, 0, 0)

    # Emits the custom close signal when the "close" button is clicked
    # (Close program is handled by ProgramFrame, which receives this signal)
    def closeProgram(self):
        self.close_signal.emit()