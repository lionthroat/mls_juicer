import os
import re
import statistics  # For calculating median prices, days on market, etc.
import sys
import time
from datetime import datetime, timedelta  # For finding last month's solds

import cv2  # For locating MLS elements to interact with, boxes, tables, buttons, etc.
import matplotlib.dates as mdates
import matplotlib.pyplot as plt  # For making simple charts (not print quality)
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd  # For reading in and manipulating CSV data from MLS exports
import pyautogui  # For interacting with MLS: entering search criteria, clicking search buttons, etc.
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,  # Qt is for alignment
                          pyqtSignal)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSplashScreen,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()

        # Set the background color to bright orange (#F7941D)
        self.setStyleSheet("background-color: #F7941D;")

        # Load the program's name image
        pixmap = QPixmap("assets/logo_title_house.png")

        # Create a QLabel to display the program's name image
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a QLabel for the loading text
        self.loading_label = QLabel("Loading...", self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a QTimer to update the loading animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_loading_text)
        self.timer.start(500)  # Change the loading text every 500 milliseconds

        # Set up the layout for the splash screen
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.loading_label)
        self.setLayout(layout)

        # Set the size and position of the splash screen, height x width
        self.setFixedSize(750, 650)

        # Center the splash screen on the user's monitor
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)
        
        # Set the window flag to stay on top of other windows
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def close_splash(self):
        # Close the splash screen
        self.close()
        # Emit the custom signal to indicate the splash screen has closed
        self.finished.emit()

    def update_loading_text(self):
        # Update the loading text with the next animation frame
        current_text = self.loading_label.text()
        if current_text.endswith("..."):
            self.loading_label.setText("Loading")
        else:
            self.loading_label.setText(current_text + ".")