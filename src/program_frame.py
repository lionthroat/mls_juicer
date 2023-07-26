import sys
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,
                          pyqtSignal, QEvent)
from PyQt6.QtGui import QColor, QPixmap, QPalette, QIcon
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow, QFrame,
                             QMessageBox, QPushButton, QSplashScreen, QSplitter, QSizePolicy,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QTabWidget)
                             
from title_bar import TitleBar
from main_menu import MainMenu

###############################################################################
#
# Class: ProgramFrame
# -----------------------
# Description: Contains our custom title bar and rest of the program GUI
# Citation: Inspired by the nested structure of this program. I originally
#           made the TitleBar a child to MainMenu, which displayed fine
#           but didn't work. Then I had them totally separate, which
#           put my TitleBar instance floating around independently like a ghost.
#           This solution introduces a third class, a frame to instantiate
#           both the TitleBar and MainMenu inside in a vertical layout (QVBoxLayout).
# https://stackoverflow.com/questions/9377914/how-to-customize-title-bar-and-window-of-desktop-application
#
###############################################################################
class ProgramFrame(QWidget):
    def __init__(self):
        super().__init__()
        # This hides the default frame created by the operating system (FramelessWindowHint)
        # Then, WindowStaysOnTopHint tells your machine to open this program on top (in front of)
        # other programs/terminals
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Fixes error that ProgrameFrame has no attribute offset
        # (The window can't be moved by user without calculating the offset,
        # and if the offset variable doesn't exist yet, that's a problem)
        self.offset = None

        # Create a QVBoxlayout for the layout of items belong to self (ProgramFrame instance)
        frame_layout = QVBoxLayout(self)

        # Instantiate our custom title bar and the program's main menu/content window
        title_bar = TitleBar()
        main_menu = MainMenu()

        # Attach our title bar and main menu to the frame's layout object
        frame_layout.addWidget(title_bar)
        frame_layout.addWidget(main_menu)

        # Show our frame
        self.show()

    def handleTitleBarClicked(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()

    def mousePressEvent(self, event):
        # Now triggers for title bar too
        # print("program frame mouse press event", flush=True)
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)