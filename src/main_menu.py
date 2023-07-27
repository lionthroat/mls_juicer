import os
import re
import statistics  # For calculating median prices, days on market, etc.
import sys
import time
import pickle # To remember user information
from datetime import datetime, timedelta  # For finding last month's solds
from functools import partial # for dynamically generating buttons w/o immediately calling their functions

import cv2  # For locating MLS elements to interact with, boxes, tables, buttons, etc.

import matplotlib.dates as mdates
import matplotlib.pyplot as plt  # For making simple charts (not print quality)
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import pandas as pd  # For reading in and manipulating CSV data from MLS exports
import pyautogui  # For interacting with MLS: entering search criteria, clicking search buttons, etc.
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,  # Qt is for alignment
                          pyqtSignal, QEvent)
from PyQt6.QtGui import QColor, QPixmap, QFontDatabase, QFont
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSplashScreen, QSplitter,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QTabWidget)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from user_profile import UserProfile

# Need to read this to make better visualizations:
# https://www.pythonguis.com/tutorials/pyqt6-plotting-matplotlib/

# Define a utility function to set white background color for widgets
def set_inputstyle(widget):
    widget.setStyleSheet("background-color: white; color: #111111;")

class MainMenu(QMainWindow):
    # Create a custom signal to be emitted when the title bar is clicked
    mainMenuClicked = pyqtSignal(QEvent)

    def __init__(self):
        super().__init__()

        # Determine whether we have a guest or returning user
        self.user_profile = UserProfile() # new instance of user_profile
        name = self.load_last_user()
        if name is not None:
            self.user_profile.load_user_name() # see if they're a new or returning user
        self.user_profile.load_user_data() # try to load a spreadsheet for them

        self.init_ui()

        # Initialize DOM distribution count variables as instance variables
        self.count0to30 = 0
        self.count31to60 = 0
        self.count61to90 = 0
        self.count91to120 = 0
        self.count120plus = 0

        self.month = ''
        self.sonoma_property_count = 0

    # Main Program UI Elements, in tabbed format
    def init_ui(self):
        # Set the size and position of the main window
        # self.setFixedSize(1000, 600)

        # # Center the main window on the user's monitor
        # screen_geometry = QApplication.primaryScreen().availableGeometry()
        # self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)
        self.setStyleSheet("background-color: #5C4F72; color: #FFFFFF")
        self.setContentsMargins(0, 0, 0, 0)


        # Create a vertical splitter to divide the window into two sections
        splitter = QSplitter(self)
        splitter.setContentsMargins(0, 0, 0, 0)
        splitter.setHandleWidth(1)

        # NAVPANE: Create the navigation pane on the left-hand side
        navigation_pane = QWidget()
        navigation_pane.setStyleSheet("background-color: #382c47; color: #FFFFFF; border-top: 1px solid #5C4F72;")
        navigation_pane.setFixedWidth(200)
        navigation_pane.setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(navigation_pane)

        # Create the main content area on the right-hand side and add to splitter
        main_content = QWidget()
        main_content.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(main_content)

        # Set the main content widget as the central widget for MLSDataProcessor
        self.setCentralWidget(splitter)

        # Create a QVBoxLayout for the layout of items belonging to navigation_pane
        navigation_layout = QVBoxLayout(navigation_pane)
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        navigation_layout.setContentsMargins(20, 20, 20, 20)
        navigation_layout.setSpacing(10)

        # Load navpane user image
        # pixmap = QPixmap("assets/user_logo.png")

        # Create a QLabel to display the program's name image
        #self.label = QLabel(self)
        #self.label.setPixmap(pixmap)
        #self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.label.setStyleSheet("border-top: 0px;")

        # Add the logo label to the top of the navigation pane layout
        #navigation_layout.addWidget(self.label)

        ## Create a QVBoxLayout for the buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Create Navigation Pane Buttons
        self.welcome_back_button = QPushButton("Welcome")
        self.import_csv_button = QPushButton("Import CSV")
        self.data_processing_button = QPushButton("Data Processing")
        self.charts_page_button = QPushButton("Charts and Graphs")
        self.export_from_MLS_button = QPushButton("Export from MLS")
        self.select_user_button = QPushButton("Switch User")
        self.update_button_styles(0)

        # Add buttons to navigation page
        navigation_layout.addWidget(self.welcome_back_button)
        navigation_layout.addWidget(self.import_csv_button)
        navigation_layout.addWidget(self.data_processing_button)
        navigation_layout.addWidget(self.charts_page_button)
        navigation_layout.addWidget(self.export_from_MLS_button)
        navigation_layout.addWidget(self.select_user_button)

        ## Add the buttons layout to the navigation pane layout
        navigation_layout.addLayout(buttons_layout)

        # Create a QStackedWidget for the main content area to hold different pages
        self.stacked_widget = QStackedWidget(main_content)

        # 1. Welcome page
        welcome_back_page = QWidget()
        self.setup_welcome_back_page(welcome_back_page)
        self.stacked_widget.addWidget(welcome_back_page)

        # 2. Import data page
        import_csv_page = QWidget()
        self.setup_import_csv_page(import_csv_page)  # Function to set up the main menu UI elements
        self.stacked_widget.addWidget(import_csv_page)

        # 3. Data processing page
        data_processing_page = QWidget()
        self.setup_data_processing_page(data_processing_page)  # Function to set up the data processing UI elements
        self.stacked_widget.addWidget(data_processing_page)

        # 4. Charts page
        charts_page = QWidget()
        self.setup_charts_page(charts_page)
        self.stacked_widget.addWidget(charts_page)

        # 5. Export from MLS page
        export_from_MLS_page = QWidget()
        self.setup_export_from_MLS_page(export_from_MLS_page)
        self.stacked_widget.addWidget(export_from_MLS_page)    

        # 6. Select user page
        select_user_page = QWidget()
        self.setup_select_user_page(select_user_page)
        self.stacked_widget.addWidget(select_user_page)    

        # Set the stacked widget as the main content for MLSDataProcessor
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.addWidget(self.stacked_widget)
        main_content_layout.addStretch(1)

        # Connect navigation buttons to their respective pages
        self.welcome_back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.import_csv_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.data_processing_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.charts_page_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.export_from_MLS_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        self.select_user_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))

        # Connect the currentChanged signal of the stacked widget to the update_button_styles method
        self.stacked_widget.currentChanged.connect(self.update_button_styles)

        # Decide which page to show to user (whether they have a profile or not)
        if self.user_profile.user is not None:
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.stacked_widget.setCurrentIndex(4)

        self.show()

    def get_existing_user_profiles(self):
        # Get the list of files in the "data/" directory
        files = os.listdir("data/")

        # Filter out the ".h5" files
        hdf5_files = [file for file in files if file.endswith(".h5")]

        return hdf5_files

    def update_button_styles(self, index):
        # Define the button styles for the normal and hover states
        button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        hover_style = (
            """QPushButton { background-color: #534361;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
        )

        # Apply the normal style to all buttons
        self.welcome_back_button.setStyleSheet(button_style)
        self.import_csv_button.setStyleSheet(button_style)
        self.data_processing_button.setStyleSheet(button_style)
        self.charts_page_button.setStyleSheet(button_style)
        self.export_from_MLS_button.setStyleSheet(button_style)
        self.select_user_button.setStyleSheet(button_style)

        # Apply the hover style to the button corresponding to the current index
        if index == 0:
            self.welcome_back_button.setStyleSheet(hover_style)
        elif index == 1:
            self.import_csv_button.setStyleSheet(hover_style)
        elif index == 2:
            self.data_processing_button.setStyleSheet(hover_style)
        elif index == 3:
            self.charts_page_button.setStyleSheet(hover_style)
        elif index == 4:
            self.export_from_MLS_button.setStyleSheet(hover_style)
        elif index == 5:
            self.select_user_button.setStyleSheet(hover_style)

    def handle_username_save_button(self):
        username = self.new_user_edit.text().strip() # Strip leading whitespaces (also handles case that input is all whitespace)
        print(username)

        if not username:
            QMessageBox.critical(self, "Error", "Please enter a valid username")
            return
        else:
            self.user_profile.set_user_name(username)
            self.user_profile.save_user_name()
            self.save_last_user()
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

    def setup_welcome_back_page(self, welcome_back_page):
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

        welcome_style = (
            """
            color: #FFFFFF;
            border: none;
            padding: 15px;
            font-size: 32px;
            """
        )

        make_profile_label_style = (
            """
            color: #FFFFFF;
            border: none;
            padding: 15px;
            font-size: 32px;
            """
        )

        # Load the custom font file and assign a family name
        font_1 = QFontDatabase.addApplicationFont("assets/NeutraText-Book.otf")
        sans_serif = QFontDatabase.applicationFontFamilies(font_1)[0]

        # Create a QFont object using the family name
        self.neutra_book = QFont(sans_serif)

        layout = QVBoxLayout(welcome_back_page)  # Use the main menu widget as the parent for the layout

        # layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.layout.setSpacing(0)

        # Welcome message
        self.welcome_label = QLabel(f'Welcome back, {self.user_profile.user}!')
        self.welcome_label.setStyleSheet(welcome_style)
        self.welcome_label.setFont(self.neutra_book)

        # RETURNING USER, Widgets
        # Juice pic
        juice_pixmap = QPixmap("assets/juice.png")
        self.juice_label = QLabel(self)
        self.juice_label.setPixmap(juice_pixmap)
        self.juice_label.setContentsMargins(0, 0, 0, 0)

        # Switch profiles msg
        self.new_user_button = QPushButton(f'(Not {self.user_profile.user}? Switch profiles)')
        self.new_user_button.setStyleSheet(new_user_button_style)
        self.new_user_button.setFixedWidth(200)

        # Go to switch profiles page
        self.new_user_button.clicked.connect(self.handle_new_user_button)

        # Stack page 2: add widgets to stack layout
        layout.addStretch(1)
        layout.addWidget(self.welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.juice_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.new_user_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(3)

    def handle_new_user_button(self):
        self.stacked_widget.setCurrentIndex(5)

    # Set up UI elements for the main menu
    def setup_import_csv_page(self, import_csv_page):
        button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

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

        welcome_style = (
            """
            color: #FFFFFF;
            border: none;
            padding: 15px;
            font-size: 32px;
            """
        )

        select_csv_style = (
            """
            color: #FFFFFF;
            border: none;
            padding: 15px;
            font-size: 28px;
            """
        )

        filename_field_style = (
            """
            color: #FFFFFF;
            background-color: #534361;
            border: 1px;
            border-color: #FFFFFF;
            padding: 15px;
            font-size: 14px;
            border-radius: 20px;
            line-height: 2;
            """
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

        layout = QVBoxLayout(import_csv_page)  # Use the main menu widget as the parent for the layout

        # Select CSV File
        if self.user_profile.data is not None:
            self.csv_file_label = QLabel("We've got your data")
        else:
            self.csv_file_label = QLabel("Let's import your data:")

        self.csv_file_label.setStyleSheet(select_csv_style)
        self.csv_file_label.setFont(self.neutra_book)

        self.csv_file_edit = QLineEdit()
        self.csv_file_button = QPushButton("Browse")

        self.csv_file_button.clicked.connect(self.browse_csv_file)

        self.csv_file_edit.setStyleSheet(filename_field_style)
        layout.addWidget(self.csv_file_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.csv_file_edit)
        layout.addWidget(self.csv_file_button)

        self.go_button = QPushButton("Validate CSV \& Process Data →")
        layout.addWidget(self.go_button)

        # Connect navigation buttons to their respective pages
        self.go_button.clicked.connect(self.handle_go_button)

        # Add button styles
        self.go_button.setStyleSheet(button_style)
        self.csv_file_button.setStyleSheet(button_style)

    def setup_select_user_page(self, select_user_page):
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

        files = self.get_existing_user_profiles()
        for file in files:
            self.generate_button(file)

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

    def generate_button(self, file):
        user_button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            font-size: 14px;
            margin-top: 20px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        try:
            username = file.split(".")[0]

            self.user_button = QPushButton(username)
            self.user_profiles_inner.addWidget(self.user_button)
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

        except Exception as e:
            QMessageBox.critical(self, "Error", f'{e}')
            return

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

    def setup_data_processing_page(self, data_processing_page):
        layout = QVBoxLayout(data_processing_page)  # Use the data processing widget as the parent for the layout
        #layout.addStretch(1)
        button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        # Main output box
        self.output_text = QTextEdit()
        layout.addWidget(self.output_text)
        self.output_text.setStyleSheet("background: #b5b1ba; color: #222222;")

        # Create a QHBoxLayout to hold the buttons
        buttons_layout = QHBoxLayout()

        # Continue to charts button
        self.continue_charts_button = QPushButton("Continue to Charts →")
        self.continue_charts_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        # Back to main menu button
        self.start_over_button = QPushButton("← Start over")
        self.start_over_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        # Add button styles
        self.start_over_button.setStyleSheet(button_style)
        self.continue_charts_button.setStyleSheet(button_style)

        # Add the buttons to the buttons_layout
        buttons_layout.addWidget(self.start_over_button)
        buttons_layout.addWidget(self.continue_charts_button)

        # Add the buttons_layout to the main layout
        layout.addLayout(buttons_layout)

    def setup_charts_page(self, charts_page):
        layout = QVBoxLayout(charts_page)
        layout.addStretch(1)
        # Create the matplotlib figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Add navigation buttons to the navigation pane + style them
        button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        # Create a QHBoxLayout to hold the buttons
        buttons_layout = QHBoxLayout()

        # 4 Chart buttons
        self.dom_distribution_button = QPushButton("DOM Distribution")
        self.dom_distribution_button.clicked.connect(self.show_dom_distribution_chart)
        buttons_layout.addWidget(self.dom_distribution_button)

        self.solds_table_button = QPushButton("Solds Table")
        buttons_layout.addWidget(self.solds_table_button)

        self.sfr_snapshot_button = QPushButton("SFR Snapshot")
        buttons_layout.addWidget(self.sfr_snapshot_button)

        self.month_over_month_button = QPushButton("Month-over-Month")
        self.month_over_month_button.clicked.connect(self.show_month_over_month_medians_chart)
        buttons_layout.addWidget(self.month_over_month_button)

        # Add the buttons_layout to the main layout
        layout.addLayout(buttons_layout)

        # # Save as PNG button
        # self.save_as_png_button = QPushButton("Save as PNG")
        # self.save_as_png_button.clicked.connect(self.on_save_as_png_clicked)
        # layout.addWidget(self.save_as_png_button)

        # Back to main menu button
        self.start_over_button = QPushButton("← Start over")
        self.start_over_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        layout.addWidget(self.start_over_button)     

        # Add button styles
        self.dom_distribution_button.setStyleSheet(button_style)
        self.solds_table_button.setStyleSheet(button_style)
        self.sfr_snapshot_button.setStyleSheet(button_style)
        self.month_over_month_button.setStyleSheet(button_style)
        # self.save_as_png_button(button_style)
        self.start_over_button.setStyleSheet(button_style)

    def setup_export_from_MLS_page(self, export_from_MLS_page):
        layout = QVBoxLayout(export_from_MLS_page)
        layout.addStretch(1)

        # Add navigation buttons to the navigation pane + style them
        button_style = (
            """QPushButton { background-color: #382c47;
            color: #FFFFFF;
            border: none;
            border-radius: 15px;
            padding: 15px;
            }"""
            "QPushButton:hover { background-color: #534361; }"
        )

        self.launch_button = QPushButton("Open Bareis")

        layout.addWidget(self.launch_button)

        # Connect navigation buttons to their respective pages
        self.launch_button.clicked.connect(self.launch_browser)

        # Add button styles
        self.launch_button.setStyleSheet(button_style)

    def get_previous_month(self):
        today = QDate.currentDate()
        self.month = today.addMonths(-1)
        return self.month.toString("MMMM yyyy")

    def launch_browser(self):
        self.username = '******'
        self.credentials = '*****'

        # Initialize Chrome WebDriver
        driver = webdriver.Chrome()

        # Open the website
        url = "http://www.bareis.com"
        driver.get(url)

        # Wait for the member login element to be visible (adjust the timeout as needed)
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for the element to be clickable
        submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btnSubmit")))
        submit_button.click()
        time.sleep(3)

        # Get handles of all open tabs/windows
        all_tabs = driver.window_handles

        # Close the original tab (the first one in the list)
        driver.switch_to.window(all_tabs[0])
        driver.close()

        # Switch back to the new tab (the only one left in the list after closing the original tab)
        driver.switch_to.window(all_tabs[-1])

        # Wait for the page to load and find the username and password input fields
        wait = WebDriverWait(driver, 10)
        username_input = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))

        # Input your username and password
        username_input.send_keys(self.username)  # Replace with your username
        password_input.send_keys(self.credentials)  # Replace with your password

        # Find and click the login button
        login_button = wait.until(EC.visibility_of_element_located((By.ID, "loginbtn")))
        login_button.click()

        # Close the browser
        #driver.quit()
        # assert "Python" in driver.title
        # elem = driver.find_element(By.NAME, "q")
        # elem.clear()
        # elem.send_keys("pycon")
        # elem.send_keys(Keys.RETURN)
        # assert "No results found." not in driver.page_source
        # driver.close()

    # Allow user to search for an attach a csv from their filesystem
    def browse_csv_file(self):
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.csv_file_edit.setText(file_name)

    # Before going into data processing screen, try to read the csv file
    def validate_csv(self):
        csv_file = self.csv_file_edit.text()

        try:
            # Use pandas library to open csv as a dataframe, parse 'Selling Date' col as dates in the format 'MM/DD/YYYY'
            self.user_profile.data = pd.read_csv(csv_file, parse_dates=['Selling Date'], date_format='%m/%d/%Y')
            self.user_profile.data['Sell Price Stripped'] = self.user_profile.data['Sell Price Display'].str.replace(',', '').astype(float)

            self.csv_file_label = QLabel("We've got your data")
        except Exception as e:
            QMessageBox.critical(self, "Error", "Attach valid CSV file")
            return

        self.process_data()

    def filter_properties_by_city_and_date(self, city, start_date, end_date):
        # Filter the data for properties sold in the specified city
        city_data = self.user_profile.data[self.user_profile.data['City'].str.contains(city, case=False, na=False)]

        total = len(self.user_profile.data)
        print(f'Filtering data for {city} from {start_date} to {end_date} from total of {total} properties', flush=True)
        # Filter the data for properties sold within the specified date range
        filtered_data = city_data[
            (city_data['Selling Date'] >= start_date) &
            (city_data['Selling Date'] <= end_date)
        ]

        prop_count = len(filtered_data)
        print(f'Number of properties being returned: {prop_count}', flush=True)
        return filtered_data

    def price_format(self, x, pos):
        # Format the tick labels like prices (e.g. $720,000)
        return '${:,.0f}'.format(x)

    def get_last_month_start(self):
        today = datetime.today()
        start_of_month = today.replace(day=1)
        end_of_last_month = start_of_month - timedelta(days=1)
        start_of_last_month = end_of_last_month.replace(day=1)

        # Format the dates as string in the format 'MM/DD/YYYY'
        start_date = start_of_last_month.strftime('%m/%d/%Y')

        return start_date

    # need to refactor, see QDate functions in get_previous_month in MainMenu
    def get_last_month_end(self):
        today = datetime.today()
        start_of_month = today.replace(day=1)
        end_of_last_month = start_of_month - timedelta(days=1)
        start_of_last_month = end_of_last_month.replace(day=1)

        # Format the dates as string in the format 'MM/DD/YYYY'
        end_date = end_of_last_month.strftime('%m/%d/%Y')

        return end_date

    def show_month_over_month_medians_chart(self):
        self.figure.clear()

        # Convert 'Selling Date' to datetime
        self.user_profile.data['Selling Datetime'] = pd.to_datetime(self.user_profile.data['Selling Date'])

        # Extract the month and year from the 'Selling Date' column and create new columns
        self.user_profile.data['Month'] = self.user_profile.data['Selling Datetime'].dt.strftime('%b-%y')  # Format: 'Jun-23'
        self.user_profile.data['YearMonth'] = self.user_profile.data['Selling Datetime'].dt.to_period('M')  # For grouping

        # Group the data by 'YearMonth' and calculate the median sell price and median DOM for each group
        median_sell_prices = self.user_profile.data.groupby('YearMonth')['Sell Price Stripped'].median()
        median_dom = self.user_profile.data.groupby('YearMonth')['DOM'].median()

        data_for_plot = []
        for i, year_month in enumerate(median_sell_prices.index):
            year_month_str = year_month.strftime('%b-%y')
            data_for_plot.append([year_month_str, median_dom[i], median_sell_prices[i]])

        months = median_sell_prices.index.to_timestamp() #convert from PeriodIndex to DatetimeIndex

        doms = [item[1] for item in data_for_plot]
        prices = [item[2] for item in data_for_plot]

        # Set up the axes
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()
        ax2.set_ylim(4, 50)

        # Set color for y-axis ticks and grid lines
        ax1.tick_params(axis='x', length=0)
        ax1.tick_params(axis='y', colors='lightgray', length=0)
        ax1.yaxis.grid(color='#EEEEEE', linestyle='solid')

        ax2.plot(months, doms)    
        ax2.tick_params(axis='y', colors='lightgray', length=0)
        ax2.set_ylim(0, max(median_dom) + 5)  # Set the second y-axis range
        
        # Plot the bar chart for median sell price
        ax1.bar(months, prices, color='lightblue', width=15, zorder=2)  # Increase zorder to make sure bars are on top
        ax1.set_ylim(720000, 860000)  # Set the y-axis range
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(self.price_format))
        ax1.xaxis.set_major_locator(plt.MaxNLocator(13))  # Show 15 ticks at most
        plt.xticks(rotation=45, ha='right')  # Use 'ha' parameter for better label alignment
        plt.subplots_adjust(bottom=.9, top=1)  # Adjust bottom margin for the rotated labels
        ax1.set_xticklabels(median_sell_prices.index, rotation=45, color='lightgray')

        # Add a title
        ax1.set_title('County of Sonoma: Month-Over-Month Comparison', color='lightgray')

        # Set border color of the graph to 'none'
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        # Show the plot within the PyQt6 application
        self.canvas.draw()

        # Add padding to the bottom of the chart
        self.figure.tight_layout()

        # # Convert 'Selling Date' to datetime
        # self.user_profile.data['Selling Datetime'] = pd.to_datetime(self.user_profile.data['Selling Date'])

        # # Extract the month and year from the 'Selling Date' column and create new columns
        # self.user_profile.data['Month'] = self.user_profile.data['Selling Datetime'].dt.strftime('%b-%y')  # Format: 'Jun-23'
        # self.user_profile.data['YearMonth'] = self.user_profile.data['Selling Datetime'].dt.to_period('M')  # For grouping

        # # Group the data by 'YearMonth' and calculate the median sell price and median DOM for each group
        # median_sell_prices = self.user_profile.data.groupby('YearMonth')['Sell Price Stripped'].median()
        # median_dom = self.user_profile.data.groupby('YearMonth')['DOM'].median()

        # data_for_plot = []
        # for i, year_month in enumerate(median_sell_prices.index):
        #     year_month_str = year_month.strftime('%b-%y')
        #     data_for_plot.append([year_month_str, median_dom[i], median_sell_prices[i]])

        # months = median_sell_prices.index.to_timestamp() #convert from PeriodIndex to DatetimeIndex

        # doms = [item[1] for item in data_for_plot]
        # prices = [item[2] for item in data_for_plot]

        # # Set up the figure and axes
        # fig, ax1 = plt.subplots(figsize=(8, 4))
        # ax2 = ax1.twinx()
        # ax2.set_ylim(4,50)

        # # Set color for y-axis ticks and grid lines
        # ax1.tick_params(axis='x', length=0)
        # ax1.tick_params(axis='y', colors='lightgray', length=0)
        # ax1.yaxis.grid(color='#EEEEEE', linestyle='solid')

        # ax2.plot(months, doms)    
        # ax2.tick_params(axis='y', colors='lightgray', length=0)
        # ax2.set_ylim(0, max(median_dom) + 5)  # Set the second y-axis range
        
        # # Plot the bar chart for median sell price
        # ax1.bar(months, prices, color='lightblue', width=15, zorder=2)  # Increase zorder to make sure bars are on top
        # ax1.set_ylim(720000, 860000)  # Set the y-axis range
        # ax1.yaxis.set_major_formatter(ticker.FuncFormatter(self.price_format))
        # #ax1.set_xticks(months)
        # ax1.xaxis.set_major_locator(plt.MaxNLocator(13))  # Show 15 ticks at most
        # plt.xticks(rotation=45, ha='right')  # Use 'ha' parameter for better label alignment
        # plt.subplots_adjust(bottom=0.2)  # Adjust bottom margin for the rotated labels
        # ax1.set_xticklabels(median_sell_prices.index, rotation=45, color='lightgray')

        # #Check if first and last x-coordinates are in tick positions
        # # xticks_positions = ax1.get_xticks()
        # # if x_coords[0] not in xticks_positions:
        # #     xticks_positions = np.insert(xticks_positions, 0, x_coords[0])
        # # if x_coords[-1] not in xticks_positions:
        # #     xticks_positions = np.append(xticks_positions, x_coords[-1])
        # # ax1.set_xticks(xticks_positions)

        # # Add a title
        # ax1.set_title('County of Sonoma: Month-Over-Month Comparison', color='lightgray')

        # # Set border color of the graph to 'none'
        # ax1.spines['top'].set_visible(False)
        # ax1.spines['right'].set_visible(False)
        # ax1.spines['bottom'].set_visible(False)
        # ax1.spines['left'].set_visible(False)
        # ax2.spines['top'].set_visible(False)
        # ax2.spines['right'].set_visible(False)
        # ax2.spines['bottom'].set_visible(False)
        # ax2.spines['left'].set_visible(False)

        # # Adjust x-axis limits for breathing room at the edges
        # #ax1.set_xlim(months[0] - pd.Timedelta(days=width), months[-1] + pd.Timedelta(days=width))

        # # Show the plot
        # #plt.tight_layout()
        # #plt.show()
        # self.canvas.draw()

    def show_dom_distribution_chart(self):
        self.figure.clear()

        # Data for the pie chart
        labels = ['0-30 Days', '31-60 Days', '61-90 Days', '91-120 Days', '120+ Days']
        sizes = [self.count0to30, self.count31to60, self.count61to90, self.count91to120, self.count120plus]
        colors = ['#CFE6EB', '#A0B0BC', '#70798C', '#C9C5B1', '#C2A477']

        # Filter out categories with a count of 0
        labels_filtered = []
        sizes_filtered = []
        colors_filtered = []
        for label, size, color in zip(labels, sizes, colors):
            if size > 0:
                labels_filtered.append(label)
                sizes_filtered.append(size)
                colors_filtered.append(color)

        # Create a subplot and plot your data
        ax = self.figure.add_subplot(111)
        ax.pie(sizes_filtered, labels=labels_filtered, colors=colors_filtered, autopct='%1.1f%%', startangle=140)
        ax.set_title('DOM Distribution')
        ax.axis('equal') # Equal aspect ratio ensures that the pie chart is drawn as a circle.

        self.canvas.draw()

    # def on_save_as_png_clicked(self):
    #     # Call the save_chart_as_png method with the appropriate figure
    #     if self.figure != None:
    #         self.save_chart_as_png(self.figure)

    # def save_chart_as_png(self):
    #     # Show a file dialog to get the desired file path and name for the .png file
    #     file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart as PNG", "", "PNG Files (*.png)")

    #     if file_path:
    #         # Save the chart as a .png file
    #         self.figure.savefig(file_path, dpi=300)  # You can adjust the dpi as needed

    # Function to extract the first integer from a cell because the MLS is trassshhhhh
    def extract_first_integer(self, cell_data):
        # Use regex pattern to match either slash or hyphen
        pattern = r'(\d+)[\/-](\w+)'
        try:
            match = re.match(pattern, cell_data)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"Error occurred while processing cell data: {e}")
        return None

    def handle_go_button(self):
        self.stacked_widget.setCurrentIndex(2)
        self.validate_csv()

    def process_data(self):
        time_period = self.month
        dom_list = []
        output_lines = []
        dom_output_data = []
        output_text = ''
        total_property_count = len(self.user_profile.data)

        # Extract only days on market, not cumulative days on market
        self.user_profile.data['DOM/CDOM'] = self.user_profile.data['DOM/CDOM'].apply(self.extract_first_integer)
        self.user_profile.data.rename(columns={'DOM/CDOM': 'DOM'}, inplace=True)

        # Split the 'Street Full Address' into separate parts (address, city, state_zip)
        # Replaces prev version: data["Street Full Address"] = data["Street Full Address"].str.split(',').str.get(0)
        self.user_profile.data[['Address', 'City', 'State_Zip']] = self.user_profile.data['Street Full Address'].str.split(',', n=2, expand=True)

        # Extract the zip code (5-digit only) from the 'State_Zip' column
        self.user_profile.data['Zip Code'] = self.user_profile.data['State_Zip'].str.extract(r'(\d{5})')

        # Drop the 'State_Zip' column, as we have extracted the zip code
        self.user_profile.data.drop(columns=['State_Zip'], inplace=True)

        self.user_profile.save_user_data()
        self.csv_file_label = QLabel("We already have your data!")

        # SONOMA ONLY. Last Month's Solds: table, analysis, and exports
        sonoma_last_month_data = self.filter_properties_by_city_and_date('Sonoma', self.get_last_month_start(), self.get_last_month_end())

        sold_off_market_count = self.process_sonoma(sonoma_last_month_data, output_lines, dom_output_data, dom_list)

        # Calculate median DOM and close price
        median_dom = sonoma_last_month_data['DOM'].median()
        median_close_price = sonoma_last_month_data['Sell Price Stripped'].median()

        # Output 1: Write the processed data to the output file
        output_file = "sorted_data.txt"
        with open(output_file, 'w') as file:
            file.write('\n'.join(output_lines))
            data_excludes_line = f"\nData excludes {sold_off_market_count} properties sold off market"
            file.write(f'\n{data_excludes_line}')

        # Output 2: Dom data for Illustrator and MatPlotLib Pie Charts (Days on Market Distribution)
        with open('dom_data.txt', 'w') as file:
            file.write('\"0-30 Days\"\t\"31-60 Days\"\t\"61-90 Days\"\t\"91-120 Days\"\t\"120+ Days\"\n')

            for index, row in sonoma_last_month_data.iterrows():
                dom = row["DOM"]
                if dom > 120:
                    self.count120plus += 1
                elif dom > 91:
                    self.count91to120 += 1
                elif dom > 61:
                    self.count61to90 += 1
                elif dom > 31:
                    self.count31to60 += 1
                else:
                    self.count0to30 += 1

            dom_distribution_string = f'{self.count0to30}\t{self.count31to60}\t{self.count61to90}\t{self.count91to120}\t{self.count120plus}'
            file.write(dom_distribution_string)  # each cell's data must be separated by a tab for Illustrator charts

        # Display the count of properties sold off market and the total property count
        output_text += f'\n\tData excludes {sold_off_market_count} properties sold off market\n'
        output_text += f"\tTotal properties processed: {total_property_count}\n\n"
        output_text += f'\tIn Sonoma, {self.sonoma_property_count} homes sold (SFR and condos) during June 2023\n\n'
        output_text += f"\tMedian DOM: {median_dom}\n"
        output_text += f"\tMedian Close Price: ${median_close_price}\n"

        self.output_text.append(output_text)

    def process_sonoma(self, sonoma_data, output_lines, dom_output_data, dom_list):
        sonoma_output = ''
        sold_off_market_count = 0
        self.sonoma_property_count = len(sonoma_data)
        self.output_text.append(sonoma_output)
        QApplication.processEvents()

        # Go through each Sonoma entry and process
        for index, row in sonoma_data.iterrows():
            close_price_list = []
            processed_text = ''

            # Check if the property should be discarded (Sold Off MLS)
            if "Sold Off MLS" in row["Status Desc"]:
                sold_off_market_count += 1
                continue

            # Add DOM and close price to respective lists for median calculation and DOM pie chart export data
            dom_list.append(int(row["DOM"]))
            stripped_close_price = row["Sell Price Display"].replace(",", "")
            close_price_list.append(float(stripped_close_price))

            # # Append output line for Illustrator DOM Pie Chart data
            dom_output_data.append(str(row["DOM"]))  # each cell's data must be separated by a tab for Illustrator charts

            # Create and append the output line for Indesign Table data
            output_line = f'{row["Address"]};{row["Bedrooms"]};{row["Total Bathrooms"]};{row["DOM"]};$ {row["Sell Price Display"]}'
            output_lines.append(output_line)
            processed_text += f'Processed {row["Address"]} with {row["DOM"]} days on market.'

            self.output_text.append(processed_text)
            QApplication.processEvents()

        return sold_off_market_count

    # Somehow this is "eating"
    def mousePressEvent(self, event):
        # print("main menu mouse press", flush=True)
        if event.type() == QEvent.Type.MouseButtonPress:
            # Emit the custom signal when the title bar is clicked
            self.mainMenuClicked.emit(event)

    def load_last_user(self):
        try:
            with open("data/last_user.txt", "r") as f:
                last_user = f.read()
                self.user_profile.user = last_user.strip()
                return self.user_profile.user

        except FileNotFoundError:
            return None

    def save_last_user(self):
        with open("data/last_user.txt", "w") as f:
            last_user = self.user_profile.user
            f.write(last_user)