import sys
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,
                          pyqtSignal, QEvent, pyqtSlot)
from PyQt6.QtGui import QColor, QPixmap, QPainter, QBitmap, QPalette, QIcon
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
        self.setMinimumWidth(910)
        self.setMinimumHeight(670)

        # Set a rounded rectangle mask
        mask = QPixmap(self.size())
        mask.fill(Qt.GlobalColor.white)  # Filling with white color to create a rounded rectangle
        p = QPainter(mask)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(Qt.GlobalColor.black)  # Filling with black color to create a rounded rectangle
        p.drawRoundedRect(mask.rect(), 10, 10)
        p.end()
        self.setMask(QBitmap(mask))

        self.setStyleSheet(
            """
            QWidget{
                background-color: lightgray;
            }
            """
        )


        # Fixes error that ProgrameFrame has no attribute offset
        # (The window can't be moved by user without calculating the offset,
        # and if the offset variable doesn't exist yet, that's a problem)
        self.offset = None

        # Set the margins and padding to 0
        self.setContentsMargins(0, 0, 0, 0)

        # Create a QVBoxlayout for the layout of items belong to self (ProgramFrame instance)
        frame_layout = QVBoxLayout(self)

        # Instantiate our custom title bar and the program's main menu/content window
        # Note: the title_bar needs to be stored as a class member during its instantiation using
        # "self" with dot notation. This isn't required to JUST display, but IS required
        # for the title bar to be able to communicate back easily to the program frame to
        # perform actions like closing the program when a user clicks the exit button
        self.title_bar = TitleBar() # "I, the program frame, gave myself a title bar"
        main_menu = MainMenu() # "I, the program frame, made a main_menu"

        # Attach our title bar and main menu to the frame's layout object
        frame_layout.addWidget(self.title_bar)
        frame_layout.addWidget(main_menu)
        frame_layout.setContentsMargins(0, 0, 0, 0) # Eliminates frame around whole program

        # Show our frame
        self.show()

        # Connect the close signal from the TitleBar to the closeProgram method/slot/thing
        self.title_bar.close_signal.connect(self.closeProgram)

    def closeProgram(self):
        # Close the entire program
        self.close()

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