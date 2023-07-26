import sys
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,
                          pyqtSignal, QEvent)
from PyQt6.QtGui import QColor, QPixmap, QPalette, QIcon
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout, QSpacerItem,
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
    minimize_signal = pyqtSignal()
    maximize_restore_signal = pyqtSignal()
    
    # def __init__(self, parent=None):
    #     super().__init__(parent)
    #     self.parent = parent

    def __init__(self):
        super().__init__()
        self.offset = None

        # Set the margis to zero (left margin, top margin, right margin, bottom margin)
        self.setContentsMargins(10, 9, 0, 0)
        self.setAutoFillBackground(True)

        # Title bar label
        self.window_title = QLabel(self)
        self.window_title.setText("MLS Data Sorter")
        self.window_title.setFixedSize(250,55)
        self.window_title.setStyleSheet(
            """
            QWidget{
                padding: 10px;
                color: white;
            }
            """
        )

        # CONTAINER LAYOUT: Windows buttons: minimize/maximize/close
        self.window_buttons_layout = QHBoxLayout(self)

        # Add spacer item to push buttons to the right
        #                    (left margin, top margin, left padding policy, top padding policy)
        spacer = QSpacerItem(800, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        self.window_buttons_layout.addItem(spacer)

        # Minimize button
        self.minimize = QPushButton(self)
        self.minimize.setIcon(QIcon('assets/min.png'))
        self.minimize.clicked.connect(self.minimizeWindowSignalEmit)
        self.minimize.setFixedSize(25, 25)
        # self.minimize.setStyleSheet(
        #     """
        #     QWidget{
        #         background-color: darkgray;
        #         color:lightgray;
        #         font:12px bold;
        #         font-weight:bold;
        #         border-radius: 5px;
        #         height: 95px;
        #         padding: 5px;
        #     }
        #     """
        # )

        # Maximize button
        self.maximize = QPushButton(self)
        self.maximize.setIcon(QIcon('assets/max.png'))
        self.minimize.clicked.connect(self.maximizeRestoreWindowSignalEmit)
        self.maximize.setFixedSize(25, 25)
        # self.maximize.setStyleSheet(
        #     """
        #     QWidget{
        #         border-radius: 5px;
        #         padding: 5px;
        #     }
        #     """
        # )

        # CLOSE PROGRAM BUTTON - Creates button, adds image asset,
        # and finally connect to closeProgram method that will
        # emit the closeProgram signal to ProgramFrame
        self.close = QPushButton(self)
        self.close.setIcon(QIcon('assets/close.png'))
        self.close.clicked.connect(self.closeProgramSignalEmit)
        self.close.setFixedSize(25, 25)

        self.window_buttons_layout.addWidget(self.minimize)
        self.window_buttons_layout.addWidget(self.maximize)
        self.window_buttons_layout.addWidget(self.close)
        self.window_buttons_layout.addStretch(1) #adding stretch made the spacer work

    # Emits the custom close signal when the "close" button is clicked
    # (Close program is handled by ProgramFrame, which receives this signal)
    def closeProgramSignalEmit(self):
        self.close_signal.emit()

    def minimizeWindowSignalEmit(self):
        print("minimize")
        #self.minimize_signal.emit()

    def maximizeRestoreWindowSignalEmit(self):
        print("maximize")
        #self.maximize_restore_signal.emit()