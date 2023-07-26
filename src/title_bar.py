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

        self.setAutoFillBackground(True)
        self.setStyleSheet(
            """
            QWidget{
                color:white;
                font:12px bold;
                font-weight:bold;
                border-radius: 1px;
                height: 11px;
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

        self.minimize.setMinimumHeight(10)
        close.setMinimumHeight(10)
        self.maximize.setMinimumHeight(10)

        label=QLabel(self)
        label.setText("MLS Data Sorter")
        
        hbox=QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)

        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.MinimumExpanding
        )
        self.maxNormal=False

    # Emits the custom close signal when the "close" button is clicked
    # (Close program is handled by ProgramFrame, which receives this signal)
    def closeProgram(self):
        self.close_signal.emit()