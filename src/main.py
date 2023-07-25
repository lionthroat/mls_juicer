import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from splash_screen import SplashScreen
from main_menu import MainMenu
from mls_data_processor import MLSDataProcessor
from title_bar import TitleBar

def main():
    app = QApplication(sys.argv)

    # Create and show the splash screen
    splash = SplashScreen()
    splash.show()

    # Simulate 7-second loading time
    loading_time_ms = 5000
    QTimer.singleShot(loading_time_ms, splash.hide)

    time.sleep(6)

    # Create and show the main window
    window = MainMenu()
    window.show()

    # Redirect the standard output to the terminal
    sys.stdout = sys.__stdout__
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()