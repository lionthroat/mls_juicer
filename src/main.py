import sys
import time
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,  # Qt is for alignment
                          pyqtSignal)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSplashScreen, QSplitter,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QTabWidget)

from splash_screen import SplashScreen
from program_frame import ProgramFrame

def main():
    app = QApplication(sys.argv)

    # Create and show the splash screen
    splash = SplashScreen()
    splash.show()

    # Simulate 7-second loading time
    loading_time_ms = 5000
    QTimer.singleShot(loading_time_ms, splash.hide)

    time.sleep(6)

    # Create and show the Frame that further instantiates the TitleBar and MainMenu
    frame = ProgramFrame()

    # Now that the frame has its layout, and the layout has 2 elements, show it
    frame.show()

    # Redirect the standard output to the terminal. (bc PyQt6 can otherwise
    # repress print statements that go to terminal)
    sys.stdout = sys.__stdout__
    
    # Actually start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()