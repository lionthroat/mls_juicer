from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSplashScreen, QSplitter,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QTabWidget)
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,  # Qt is for alignment
                          pyqtSignal)
import sys

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()

    def init_ui(self):
        self.setWindowTitle("MLS Data Sorter")
        # Set the size and position of the main window
        self.setFixedSize(1000, 600)

        # Center the main window on the user's monitor
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

        self.setStyleSheet("background-color: #6c6870; color: #FFFFFF")

        # Create a vertical splitter to divide the window into two sections
        splitter = QSplitter(self)
        splitter.setHandleWidth(1)

        # NAVPANE: Create the navigation pane on the left-hand side
        navigation_pane = QWidget()
        navigation_pane.setStyleSheet("background-color: #382c47; color: #FFFFFF")
        navigation_pane.setFixedWidth(200)
        splitter.addWidget(navigation_pane)

        # Create the main content area on the right-hand side
        main_content = QWidget()
        splitter.addWidget(main_content)

        # Set the main content widget as the central widget for MLSDataProcessor
        self.setCentralWidget(splitter)

        # Create a QVBoxLayout for the navigation pane
        navigation_layout = QVBoxLayout(navigation_pane)
        navigation_layout.setContentsMargins(0, 0, 0, 0)

        # Add navigation buttons to the navigation pane
        self.main_menu_button = QPushButton("Main Menu")
        self.data_processing_button = QPushButton("Data Processing")
        navigation_layout.addWidget(self.main_menu_button)
        navigation_layout.addWidget(self.data_processing_button)

        # Create a QStackedWidget for the main content area to hold different pages
        self.stacked_widget = QStackedWidget(main_content)

        # Create the main menu page and add it to the stacked widget
        main_menu_page = QWidget()
        self.setup_main_menu_page(main_menu_page)  # Function to set up the main menu UI elements
        self.stacked_widget.addWidget(main_menu_page)

        # Create the data processing page and add it to the stacked widget
        data_processing_page = QWidget()
        self.setup_data_processing_page()  # Function to set up the data processing UI elements
        self.stacked_widget.addWidget(data_processing_page)

        # Set the stacked widget as the main content for MLSDataProcessor
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.addWidget(self.stacked_widget)

        # Connect navigation buttons to their respective pages
        self.main_menu_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.data_processing_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # Set the window flag to stay on top of other windows
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.show()

    def setup_main_menu_page(self, main_menu_page):
        layout = QVBoxLayout(main_menu_page)
        # Last month name for report time period
        self.report_range = QLabel("Main menu content")
        layout.addWidget(self.report_range)

    def setup_data_processing_page(self):
        print("test 2")

def main():
    app = QApplication([])
    main_menu = MainMenu()
    main_menu.init_ui()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()