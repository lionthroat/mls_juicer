import ast

class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.add(node.module + "." + alias.name)

def get_class_imports(class_code):
    tree = ast.parse(class_code)
    analyzer = ImportAnalyzer()
    analyzer.visit(tree)
    return analyzer.imports

# Sample class code
class_code = """
import sys
import time
import re
import os
import numpy as np
import statistics   # For calculating median prices, days on market, etc.
import pandas as pd # For reading in and manipulating CSV data from MLS exports
import cv2          # For locating MLS elements to interact with, boxes, tables, buttons, etc.
import pyautogui    # For interacting with MLS: entering search criteria, clicking search buttons, etc.
from PyQt6.QtWidgets import QApplication, QSplashScreen, QStackedWidget, QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import QDate, QTimer, Qt, pyqtSignal, QObject #Qt is for alignment
import matplotlib.pyplot as plt          # For making simple charts (not print quality)
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timedelta # For finding last month's solds
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()

        # Set the background color to bright orange (#F7941D)
        self.setStyleSheet("background-color: #F7941D;")

        # Load the program's name image
        pixmap = QPixmap("logo_title_house.png")

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
"""

if __name__ == "__main__":
    class_imports = get_class_imports(class_code)
    print(class_imports)