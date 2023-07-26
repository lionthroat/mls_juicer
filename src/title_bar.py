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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
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

        close=QPushButton(self)
        close.setIcon(QIcon('assets/close.png'))

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

    # When uncommented, the does trigger print statement on click, but
    # it also diverts the interaction handling to the title bar,
    # instead of the program frame. And the title bar doesn't
    # have the methods to move anything around right now,
    
    # def mousePressEvent(self, event):
    #     print("title bar mouse press", flush=True)
    #     if event.type() == QEvent.Type.MouseButtonPress:
    #         # Emit the custom signal when the title bar is clicked
    #         self.titleBarClicked.emit(event)