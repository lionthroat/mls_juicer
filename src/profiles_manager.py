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


class ProfileTools():
    def __init__(self):
        super().__init__()

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
            last_user = self.user_profile.user
            f.write(last_user)

class ProfileUI(QWidget):
    def __init__(self, select_user_page):
        super().__init__()
        save_button_style = (
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
        make_profile_label_style = (
            """
            color: #FFFFFF;
            border: none;
            padding: 15px;
            font-size: 32px;
            """
        )
        new_user_edit_style = (
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

        self.wb_layout = QVBoxLayout(select_user_page)  # Use the main menu widget as the parent for the layout
        self.wb_layout.setSpacing(0)

        # Select user page: Select existing user label
        self.select_existing_label = QLabel('Select an existing user:')
        self.select_existing_label.setFont(self.neutra_book)
        self.select_existing_label.setStyleSheet(make_profile_label_style)
        self.wb_layout.addWidget(self.select_existing_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.user_profiles_list = QHBoxLayout()
        self.user_profiles_list.addStretch(1)

        self.user_profiles_inner = QVBoxLayout()

        # Generate 4 profile buttons, regardless of whether there are 3, 2, 1, or 0 profiles already
        files = self.get_existing_user_profiles()
        for i in range(4):
            if i < len(files):
                self.generate_button(files[i])
            else:
                self.generate_empty_button()

        self.user_profiles_list.addLayout(self.user_profiles_inner)

        self.user_profiles_list.addStretch(1)

        self.wb_layout.addLayout(self.user_profiles_list)

        # Select user page: Welcome, guest! label
        self.make_profile_label = QLabel('Or make a new profile:')
        self.make_profile_label.setFont(self.neutra_book)
        self.make_profile_label.setStyleSheet(make_profile_label_style)

        # Select user page: Name input field
        self.new_user_edit = QLineEdit()
        self.new_user_edit.setStyleSheet(new_user_edit_style)

        # Select user page: Continue arrow button
        self.save_button = QPushButton("→")
        self.save_button.setFixedWidth(55)
        self.save_button.setStyleSheet(save_button_style)

        # Select user page: Adding widgets to stack layout
        self.wb_layout.addWidget(self.make_profile_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
        # Horizontal layout just for the username input and arrow button
        self.name_layout = QHBoxLayout()

        self.name_layout.addStretch(1) # spacer to smoosh input and button together
        self.name_layout.addWidget(self.new_user_edit, alignment=Qt.AlignmentFlag.AlignCenter)
        self.name_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.name_layout.addStretch(1) # spacer to smoosh input and button together

        self.wb_layout.addLayout(self.name_layout)
        self.wb_layout.addStretch(1)

        # Select user page: Connect button and enter key press to handler
        self.save_button.clicked.connect(self.handle_username_save_button)
        self.new_user_edit.returnPressed.connect(self.handle_username_save_button)

        self.show()

    def handle_username_save_button(self):
        username = self.new_user_edit.text().strip() # Strip leading whitespaces (also handles case that input is all whitespace)
        print(username)

        if not username:
            QMessageBox.critical(self, "Error", "Please enter a valid username")
            return
        else:
            self.user_profile.set_user_name(username)
            self.user_profile.save_user_name()

            self.profile_tools.save_last_user()

            self.user_profile.data = None
            self.user_profile.load_user_data()

            self.welcome_label.setText(f'Welcome back, {self.user_profile.user}!')
            self.new_user_button.setText(f'(Not {self.user_profile.user}? Switch profiles)')

            # Select CSV File
            if self.user_profile.data is not None:
                self.csv_file_label.setText("We've got your data")
            else:
                self.csv_file_label.setText("Let's import your data:")

            self.stacked_widget.setCurrentIndex(0)

    def get_existing_user_profiles(self):
        # Get the list of files in the "data/" directory
        files = os.listdir("data/")

        # Filter out the ".h5" files
        hdf5_files = [file for file in files if file.endswith(".h5")]

        return hdf5_files

    def clear_user_profile_buttons(self):
        # Loop through all widgets in the layout and remove the buttons
        print('cleaning up buttons', flush=True)
        for i in reversed(range(self.user_profiles_inner.count())):
            widget = self.user_profiles_inner.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                print('found button to delete', flush=True)
                self.user_profiles_inner.removeWidget(widget)
                widget.deleteLater()  # This ensures proper cleanup and prevents memory leaks

    def reload_select_user_page(self):
        self.clear_user_profile_buttons()

        # Generate 4 profile buttons, regardless of whether there are 3, 2, 1, or 0 profiles already
        # files = self.get_existing_user_profiles()
        # for i in range(4):
        #     if i < len(files):
        #         self.generate_button(files[i])
        #     else:
        #         self.generate_empty_button()

    def delete_profile(self, file):
        # Delete the hd5 file for the user profile
        try:
            os.remove(file)
        except OSError:
            pass

        # Reload the welcome back page to reflect the changes
        self.reload_welcome_back_page()
        self.reload_select_user_page()

    def switch_user_profiles(self, file):
        print(f'checking out switch_user_profiles method', flush=True)
        self.user_profile.load_switched_user_profile(file)

        self.welcome_label.setText(f'Welcome back, {self.user_profile.user}!')
        self.new_user_button.setText(f'(Not {self.user_profile.user}? Switch profiles)')

        # Select CSV File
        if self.user_profile.data is not None:
            self.csv_file_label.setText("We've got your data")
        else:
            self.csv_file_label.setText("Let's import your data:")

        try:
            self.stacked_widget.setCurrentIndex(0)
        except:
            print("nope", flush=True)

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
            delete_button = QPushButton(f"X - Delete Profile")
            delete_button.setStyleSheet(delete_button_style)
            delete_button.clicked.connect(partial(self.delete_profile, file))

            layout = QHBoxLayout()
            layout.addWidget(self.user_button)
            layout.addWidget(delete_button)
            self.user_profiles_inner.addLayout(layout)

        except Exception as e:
            QMessageBox.critical(self, "Error", f'{e}')
            return

    def generate_empty_button(self):
        button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        empty_button = QPushButton("(Empty profile slot)")
        self.wb_layout.addWidget(empty_button)
        empty_button.setStyleSheet(button_style)

