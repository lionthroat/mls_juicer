import statistics  # For calculating median prices, days on market, etc.
import re
import statistics
import time
from datetime import datetime, timedelta  # For finding last month's solds
import sys
import PyQt6
import matplotlib.dates as mdates
import matplotlib.pyplot as plt  # For making simple charts (not print quality)
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd  # For reading in and manipulating CSV data from MLS exports
from PyQt6.QtCore import (QDate, QObject, Qt, QTimer,  # Qt is for alignment
                          pyqtSignal)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (QApplication, QComboBox, QFileDialog, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSplashScreen,
                             QStackedWidget, QTextEdit, QVBoxLayout, QWidget)

# Define a utility function to set white background color for widgets
def set_inputstyle(widget):
    widget.setStyleSheet("background-color: white; color: #111111;")

class MLSDataProcessor(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.init_ui()
        # Initialize DOM distribution count variables as instance variables
        self.count0to30 = 0
        self.count31to60 = 0
        self.count61to90 = 0
        self.count91to120 = 0
        self.count120plus = 0

        self.month = ''
        self.sonoma_property_count = 0

        # instance variable for master dataframe with all properties
        self.data = data

    # Creates data processing hub
    def init_ui(self):
        self.setWindowTitle("MLS Data Sorter")
        # Set the size and position of the splash screen, height x width
        self.setFixedSize(750, 650)

        # Center the splash screen on the user's monitor
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.move((screen_geometry.width() - self.width()) // 2, (screen_geometry.height() - self.height()) // 2)

        self.setStyleSheet(f"background-color: #A0B0BC; color: #FFFFFF")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Main output box
        self.output_text = QTextEdit()
        self.layout.addWidget(self.output_text)
        set_inputstyle(self.output_text)

        # 4 Chart buttons
        self.dom_distribution_button = QPushButton("DOM Distribution")
        self.dom_distribution_button.clicked.connect(self.show_dom_distribution_chart)
        self.layout.addWidget(self.dom_distribution_button)

        self.solds_table_button = QPushButton("Solds Table")
        self.layout.addWidget(self.solds_table_button)

        self.sfr_snapshot_button = QPushButton("SFR Snapshot")
        self.layout.addWidget(self.sfr_snapshot_button)

        self.month_over_month_button = QPushButton("Month-over-Month")
        self.month_over_month_button.clicked.connect(self.show_month_over_month_medians_chart)
        self.layout.addWidget(self.month_over_month_button)

        # Back to main menu button
        #self.start_over_button = QPushButton("Start over")
        #self.start_over_button.clicked.connect(self.hide_data_screen)
        #self.layout.addWidget(self.start_over_button)

        # Set the window flag to stay on top of other windows
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.show()
        # Set the main menu as the active screen
        self.show_data_screen()

    def filter_properties_by_city_and_date(self, city, start_date, end_date):
        # Filter the data for properties sold in the specified city
        city_data = self.data[self.data['City'].str.contains(city, case=False, na=False)]

        total = len(self.data)
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
        # Convert 'Selling Date' to datetime
        self.data['Selling Datetime'] = pd.to_datetime(self.data['Selling Date'])

        # Extract the month and year from the 'Selling Date' column and create new columns
        self.data['Month'] = self.data['Selling Datetime'].dt.strftime('%b-%y')  # Format: 'Jun-23'
        self.data['YearMonth'] = self.data['Selling Datetime'].dt.to_period('M')  # For grouping

        # Group the data by 'YearMonth' and calculate the median sell price and median DOM for each group
        median_sell_prices = self.data.groupby('YearMonth')['Sell Price Stripped'].median()
        median_dom = self.data.groupby('YearMonth')['DOM'].median()

        data_for_plot = []
        for i, year_month in enumerate(median_sell_prices.index):
            year_month_str = year_month.strftime('%b-%y')
            data_for_plot.append([year_month_str, median_dom[i], median_sell_prices[i]])

        months = median_sell_prices.index.to_timestamp() #convert from PeriodIndex to DatetimeIndex

        doms = [item[1] for item in data_for_plot]
        prices = [item[2] for item in data_for_plot]

        # Set up the figure and axes
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax2 = ax1.twinx()
        ax2.set_ylim(4,50)

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
        #ax1.set_xticks(months)
        ax1.xaxis.set_major_locator(plt.MaxNLocator(13))  # Show 15 ticks at most
        plt.xticks(rotation=45, ha='right')  # Use 'ha' parameter for better label alignment
        plt.subplots_adjust(bottom=0.2)  # Adjust bottom margin for the rotated labels
        ax1.set_xticklabels(median_sell_prices.index, rotation=45, color='lightgray')

        #Check if first and last x-coordinates are in tick positions
        # xticks_positions = ax1.get_xticks()
        # if x_coords[0] not in xticks_positions:
        #     xticks_positions = np.insert(xticks_positions, 0, x_coords[0])
        # if x_coords[-1] not in xticks_positions:
        #     xticks_positions = np.append(xticks_positions, x_coords[-1])
        # ax1.set_xticks(xticks_positions)

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

        # Adjust x-axis limits for breathing room at the edges
        #ax1.set_xlim(months[0] - pd.Timedelta(days=width), months[-1] + pd.Timedelta(days=width))

        # Show the plot
        plt.tight_layout()
        plt.show()

    def show_dom_distribution_chart(self):
        # Data for the pie chart
        labels = ['0-30 Days', '31-60 Days', '61-90 Days', '91-120 Days', '120+ Days']
        sizes = [self.count0to30, self.count31to60, self.count61to90, self.count91to120, self.count120plus]
        colors = ['#CFE6EB', '#A0B0BC', '#70798C', '#C9C5B1', '#C2A477']

        # Create a pie chart using matplotlib
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.title('DOM Distribution')
        plt.axis('equal')  # Equal aspect ratio ensures that the pie chart is drawn as a circle.

        # Display the chart within the PyQt6 application
        plt.show()

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

    # Show data processing screen widgets
    def show_data_screen(self):
        self.output_text.show()
        self.dom_distribution_button.show()
        self.solds_table_button.show()
        self.sfr_snapshot_button.show()
        self.month_over_month_button.show()
        #self.start_over_button.show()

    def process_data(self):
        self.show_data_screen()

        time_period = self.month
        dom_list = []
        output_lines = []
        dom_output_data = []
        output_text = ''
        total_property_count = len(self.data)

        # Extract only days on market, not cumulative days on market
        self.data['DOM/CDOM'] = self.data['DOM/CDOM'].apply(self.extract_first_integer)
        self.data.rename(columns={'DOM/CDOM': 'DOM'}, inplace=True)

        # Split the 'Street Full Address' into separate parts (address, city, state_zip)
        # Replaces prev version: data["Street Full Address"] = data["Street Full Address"].str.split(',').str.get(0)
        self.data[['Address', 'City', 'State_Zip']] = self.data['Street Full Address'].str.split(',', n=2, expand=True)

        # Extract the zip code (5-digit only) from the 'State_Zip' column
        self.data['Zip Code'] = self.data['State_Zip'].str.extract(r'(\d{5})')

        # Drop the 'State_Zip' column, as we have extracted the zip code
        self.data.drop(columns=['State_Zip'], inplace=True)

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
        output_text += f'\tIn Sonoma, {self.sonoma_property_count} homes sold (SFR and condos) during {time_period}\n\n'
        output_text += f"\tMedian DOM: {median_dom}\n"
        output_text += f"\tMedian Close Price: ${median_close_price}\n"

        self.output_text.append(output_text)

    def process_sonoma(self, sonoma_data, output_lines, dom_output_data, dom_list):
        sonoma_output = ''
        sold_off_market_count = 0
        self.sonoma_property_count = len(sonoma_data)
        sonoma_output += f'Sonoma properties: {self.sonoma_property_count}\n'
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

    def hide_data_screen(self):
        # Hide data processing screen widgets
        self.output_text.hide()
        self.dom_distribution_button.hide()
        self.solds_table_button.hide()
        self.sfr_snapshot_button.hide()
        self.month_over_month_button.hide()
        self.start_over_button.hide()
        self.launch_button.hide()
