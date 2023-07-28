import os
import pickle  # To remember user information
import re
import statistics  # For calculating median prices, days on market, etc.
import sys
import time
from datetime import datetime, timedelta  # For finding last month's solds
from functools import \
    partial  # for dynamically generating buttons w/o immediately calling their functions
import cv2  # For locating MLS elements to interact with, boxes, tables, buttons, etc.
import matplotlib.dates as mdates
import matplotlib.pyplot as plt  # For making simple charts (not print quality)
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd  # For reading in and manipulating CSV data from MLS exports
import pyautogui  # For interacting with MLS: entering search criteria, clicking search buttons, etc.
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import (QDate, QEvent, QObject, Qt,  # Qt is for alignment
                          QTimer, pyqtSignal)
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPixmap
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSplashScreen,
                             QSplitter, QStackedWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from user_profile import UserProfile

class ProfilesManager(QWidget):
    profile_switched = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.curr_user = UserProfile()

    def setup_select_user_page(self, select_user_page):
        self.save_button_style = (
            """QPushButton {
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            font-weight: bold;
            font-size: 36px;
            }"""
            "QPushButton:hover { background-color: #726784; }"
        )
        new_user_button_style = (
            """QPushButton {
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            width: 30%;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )
        self.make_profile_label_style = (
            """
            color: #FFFFFF;
            border: none;
            padding: 15px;
            font-size: 32px;
            """
        )
        self.new_user_edit_style = (
            """
            color: #FFFFFF;
            padding: 15px;
            font-size: 32px;
            border: none;
            margin-right: 5px;
            border-bottom: 1px solid white;
            """
        )

        # Load the custom font file and assign a family name
        font_1 = QFontDatabase.addApplicationFont("assets/NeutraText-Book.otf")
        sans_serif = QFontDatabase.applicationFontFamilies(font_1)[0]

        # Create a QFont object using the family name
        self.neutra_book = QFont(sans_serif)

        self.user_content = QVBoxLayout(select_user_page)  # Use the main menu widget as the parent for the layout
        self.user_content.setSpacing(0)

        # Create a QStackedWidget for the main content area to hold different pages
        self.stack = QStackedWidget()

        self.page1 = QWidget()
        self.page2 = QWidget()
        self.page1_UI(self.page1)
        self.page2_UI(self.page2)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.setCurrentIndex(0)

        self.user_content.addWidget(self.stack)
        self.show()

    def page1_UI(self, page):
        layout = QVBoxLayout(page)

        self.select_profile = QLabel('Select a profile:')
        self.select_profile.setFont(self.neutra_book)
        self.select_profile.setStyleSheet(self.make_profile_label_style)

        layout.addWidget(self.select_profile, alignment=Qt.AlignmentFlag.AlignCenter)

        self.smoosh_buttons_box = QHBoxLayout()
        self.smoosh_buttons_box.addStretch(1)

        self.profiles_box = QVBoxLayout()
        self.make_buttons()

        self.smoosh_buttons_box.addLayout(self.profiles_box)

        self.smoosh_buttons_box.addStretch(3)
        layout.addStretch(1)
        layout.addLayout(self.smoosh_buttons_box)

    def page2_UI(self, page):
        self.back_button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            margin-top: 20px;
            width: 200px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        layout = QVBoxLayout(page)
        layout.addStretch(1)

        # Make a new profile label + add to layout
        self.make_profile_label = QLabel('Enter a new profile name:')
        self.make_profile_label.setFont(self.neutra_book)
        self.make_profile_label.setStyleSheet(self.make_profile_label_style)
        layout.addWidget(self.make_profile_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
        # Horizontal layout just for the username input and arrow button
        input_layout = QHBoxLayout()

        # New user input field
        self.new_user_edit = QLineEdit()
        self.new_user_edit.setStyleSheet(self.new_user_edit_style)

        # Save new user arrow button
        self.save_button = QPushButton("→")
        self.save_button.setFixedWidth(55)
        self.save_button.setStyleSheet(self.save_button_style)

        input_layout.addStretch(1) # spacer to smoosh input and button together
        input_layout.addWidget(self.new_user_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        input_layout.addStretch(1) # spacer to smoosh input and button together

        # Select user page: Connect button and enter key press to handler
        self.save_button.clicked.connect(self.handle_username_save_button)
        self.new_user_edit.returnPressed.connect(self.handle_username_save_button)

        layout.addLayout(input_layout)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.switch_profile_views)
        self.back_button.setStyleSheet(self.back_button_style)
        self.back_button.setFixedWidth(200)

        layout.addStretch(1)

        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

    def handle_username_save_button(self):
        username = self.new_user_edit.text().strip() # Strip leading whitespaces (also handles case that input is all whitespace)
        
        self.new_user_edit.clear()
        self.reload_select_user_page()
        self.stack.setCurrentIndex(0)

        if not username:
            QMessageBox.critical(self, "Error", "Please enter a valid username")
            return
        else:
            self.curr_user.set_user_name(username)
            self.curr_user.save_user_name()

            self.save_last_user()

            self.curr_user.data = None
            self.curr_user.load_user_data()

            # Update profile name and profile data
            self.profile_switched.emit()

    def get_existing_user_profiles(self):
        # Get the list of files in the "data/" directory
        files = os.listdir("data/")

        # Filter out the ".h5" files
        hdf5_files = [file for file in files if file.endswith(".h5")]

        return hdf5_files

    def delete_buttons(self):
        # Loop through ALL 4 buttons and delete
        print(f'found {self.profiles_box.count()} objects to delete', flush=True)
        while self.profiles_box.count() > 0:
            item = self.profiles_box.takeAt(0)
            widget = item.widget()
            if widget:
                print(f'delete', flush=True)
                widget.deleteLater()

    def reload_select_user_page(self):
        self.delete_buttons()
        self.make_buttons()

    def make_buttons(self):
        print(f'making buttons', flush=True)
        # Generate 4 profile buttons, regardless of whether there are 3, 2, 1, or 0 profiles already
        files = self.get_existing_user_profiles()
        for i in range(4):
            if i < len(files):
                self.generate_button(files[i])
            else:
                self.generate_empty_button()

    def delete_profile(self, file):
        # Delete the hd5 file for the user profile
        try:
            filepath = f'data/{file}'
            os.remove(filepath)
        except OSError:
            pass

        # Reload the welcome back page to reflect the changes
        self.profile_switched.emit()
        self.reload_select_user_page()

    def generate_button(self, file):
        user_button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            font-size: 18px;
            margin-top: 10px;
            padding-left: 20px;
            padding-right: 20px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        delete_button_style = (
            """QPushButton {
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            font-size: 14px;
            margin-top: 10px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        try:

            username = file.split(".")[0]

            self.user_button = QPushButton(username)
            self.user_button.setFont(self.neutra_book)
            self.user_button.setStyleSheet(user_button_style)
            self.user_button.clicked.connect(partial(self.switch_user_profiles, file))

            # This was a really annoying problem... leaving solution in the code for now...
            # BAD: self.user_button.clicked.connect(self.switch_user_profiles(file))
            # WHY: You are immediately calling the switch_user_profiles
            # method and connecting the clicked signal to its return value,
            # which is None. This happens because the connect method expects a
            # callable (i.e., a function or method) as its argument, but you are
            # invoking the method with (file) after its name.

            # To fix this issue, you should pass the method reference without invoking it.
            # You can use a lambda function or functools.partial to achieve this.
            # Here's how you can modify the generate_button method:
            # Use partial to pass the file argument to the switch_user_profiles method
            # GOOD: self.user_button.clicked.connect(partial(self.switch_user_profiles, file))

            # Add delete profile button
            self.delete_button = QPushButton(f"X - Delete Profile")
            self.delete_button.setStyleSheet(delete_button_style)
            self.delete_button.clicked.connect(partial(self.delete_profile, file))

            layout = QHBoxLayout()
            layout.addWidget(self.user_button)
            layout.addWidget(self.delete_button)
            self.profiles_box.addLayout(layout)

        except Exception as e:
            QMessageBox.critical(self, "Error", f'{e}')
            return

    def generate_empty_button(self):
        self.button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        self.empty_button = QPushButton("(Empty profile slot)")
        self.empty_button.setStyleSheet(self.button_style)
        self.empty_button.clicked.connect(partial(self.switch_profile_views))

        self.profiles_box.addWidget(self.empty_button)

    def load_last_user(self):
        try:
            with open("data/last_user.txt", "r") as f:
                last_user = f.read()
                last_user_name = last_user.strip()
                return last_user_name

        except FileNotFoundError:
            return None

    def save_last_user(self):
        with open("data/last_user.txt", "w") as f:
            last_user = self.curr_user.user
            f.write(last_user)

    def switch_profile_views(self):
        curr = self.stack.currentIndex()
        if curr == 0:
            self.stack.setCurrentIndex(1)
        else:
            self.new_user_edit.clear()
            self.stack.setCurrentIndex(0)

    def switch_user_profiles(self, file):
        self.curr_user.load_switched_user_profile(file)

        # signal pm to update welcome page
        self.profile_switched.emit()