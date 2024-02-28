import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QStackedWidget, QLabel, QComboBox, QHBoxLayout, QGridLayout, QLineEdit, QMessageBox, QInputDialog, QTreeView, QProgressBar, QSlider
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QImage, QPixmap
from pyqtgraph import LegendItem
import os
import io
import time
import csv
import pyqtgraph as pg
import numpy as np
import pandas as pd
from datetime import date, datetime
from threading import Thread
import serial
from playsound import playsound
import cv2
from time import sleep

#===============================for google drive synchronisation of Athlete's profile==================================================================
from googleapiclient.http import MediaFileUpload    #to upload files
from googleapiclient.http import MediaIoBaseDownload    #to download files
from Google import Create_Service
#===============================for video player=================================================
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
#=====================================================================================

CLIENT_SECRET_FILE = 'credentials1.json' #authenticator
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
#=====================================================================================================================================================

#Initiatiation
data1 = np.array([])
data2 = np.array([])
time_interval = 1/200
iteration = -1
F1_resting_value = 0
F2_resting_value = 0
qt_image = None
frame = None

#Choose frank or rp acccount
frank_account = True
dummy_FP_data = True

#set variables
interval_ms = 15

if frank_account == True:
    audio_file_path = r"C:\Users\wongt\OneDrive - Nanyang Technological University\Academics\NTU\Y4S1\FYP\swimming-force-plate-prototype/Start.mp3"
    athletes_file_path = r"C:\Users\wongt\OneDrive - Nanyang Technological University\Academics\NTU\Y4S1\FYP\swimming-force-plate-prototype/Athlete's Profile"

else:
    audio_file_path = r"/home/ssisportstech/Desktop/swimming-force-plate-prototype/Start.mp3"
    athletes_file_path = r"/home/ssisportstech/Desktop/swimming-force-plate-prototype/Athlete's Profile"


def twos_complement_16bits(hexstr):
    return twos_complement(hexstr, 16)

def twos_complement(hexstr, bits):
    """Hex string to signed int conversion"""
    value = int(hexstr, 16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value

def return_calibrated_force_plate_values(FP1, FP2):
    return (FP1-29.926)/(0.3874), (FP2-33.926)/(0.3874)

def convert(x): #function to convert hex to int, base 16
    return int(x,16) #convert hex to int with argument x

#length of video frames sent for display
display_video_frame_length = 0

class VideoStreamWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
       # self.video_stream_url = 'udp://@0.0.0.0:8554?fifo_size=10000&overrun_nonfatal=1'  ## Adjust fifo_size and overrun_nonfatal options as needed'  # Modify this to your UDP video stream URL
        self.video_stream_url = 'udp://@0.0.0.0:8554'
        #self.cap = cv2.VideoCapture(self.video_stream_url)

        self.paused = True

        

        # Start the video streaming loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(interval_ms)  # Call update_frame based on variable interval milliseconds
    
    def read_cap(self):
        self.cap = cv2.VideoCapture(self.video_stream_url)
        cap_reading_start_time = datetime.now()
        seconds_past_for_video_buffer = 15
        while True:
            current_time = datetime.now()
            if (current_time - cap_reading_start_time).total_seconds() <= seconds_past_for_video_buffer:
                ret, frame = self.cap.read()
            else:
                break
            
        if not self.cap.isOpened():
            print("Error: Unable to open video stream.")
            return

    def update_frame(self):
        global qt_image, display_video_frame_length, frame
        if not self.paused:
            ret, frame = self.cap.read()
            if ret:
                display_video_frame_length += 1
                # Resize the frame to reduce resolution
                new_width = 200
                new_height = 125
                frame = cv2.resize(frame, (new_width, new_height)) ##Figure out new width and height
                frame = cv2.resize(frame, (800, 500))   #resize it again to lower quality image
                height, width, channel = frame.shape
                bytes_per_line = 3 * width  # Assuming 3 channels (RGB)
                qt_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                self.setPixmap(QPixmap.fromImage(qt_image))
            else:
                print("Error: Unable to read frame.")
    
    def toggle_pause(self):
        self.paused = True

    def toggle_play(self):
        self.paused = False
    
    def toggle_stop_cap(self):
        self.timer.stop()
        self.cap.release()
    

class Force_plate_calibration_page(QWidget):
    def __init__(self, force_plate_calibration_page):
        
        super().__init__()
        self.setWindowTitle("Force_plate_calibration")
        self.setGeometry(100, 100, 1600, 800)
        # Create a vertical layout manager for the main menu page
        self.force_plate_calibration_page = force_plate_calibration_page
        self.layout = QVBoxLayout(self)
        self.layout.layout().setAlignment(Qt.AlignCenter)
        self.to_tare_bool = False
        self.to_read_FP_data_bool = False
        self.FP1_resting_value_list = []
        self.FP2_resting_value_list = []
        self.tare_holding_data_quantity = 3
        self.ser = None

        # Create and insert Graphics Layout to layout
        self.canvas = pg.GraphicsLayoutWidget()   
        self.layout.layout().addWidget(self.canvas)
        
        #Create analogplots for force plate 1 and 2
        self.analogPlot1 = self.canvas.addPlot(title='Force Plate 1')
        self.analogPlot1.enableAutoRange(enable = True)
        self.analogPlot1.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase

        self.analogPlot2 = self.canvas.addPlot(title='Force Plate 2')
        self.analogPlot1.enableAutoRange(enable = True)
        self.analogPlot2.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase
        self.analogPlot2.enableAutoRange(enable = True)

        # Initialize sensor data variables
        self.numPoints = 2000
        self.fps = 0.0
        self.lastupdate = time.time()
        self.x = np.arange(self.numPoints)
        self.y1 = np.zeros(self.numPoints)
        self.y2 = np.zeros(self.numPoints)
        self.drawplot1 = self.analogPlot1.plot(pen='y')
        self.drawplot2 = self.analogPlot2.plot(pen='g')
        #Create  widgets
            #Read in FP1 and FP2 data
        self.read_FP_data_button = QPushButton('read FP data', self)
        self.read_FP_data_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.layout.addWidget(self.read_FP_data_button)
        self.read_FP_data_button.clicked.connect(self.to_read_FP_data)

            #tare values button
        self.tare_button = QPushButton('tare values', self)
        self.tare_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.layout.addWidget(self.tare_button)
        self.tare_button.clicked.connect(self.to_tare)

            #Create proceed button
        self.proceed_button = QPushButton("Proceed", self)
        self.proceed_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.layout.addWidget(self.proceed_button)
        self.proceed_button.clicked.connect(self.open_Calibration_page_for_sync_between_force_plates_and_camera_1)

            #Create progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.layout.addWidget(self.progress_bar)

            #Create label widgets
        self.FP1_plate_value_label = QLabel("NA Newton", self)
        self.layout.addWidget(self.FP1_plate_value_label) 
        self.FP2_plate_value_label = QLabel("NA Newton", self)
        self.layout.addWidget(self.FP2_plate_value_label)

        #Create a QTimer instance
        self.timer = QTimer()
        # Connect the timeout signal to the update_label function
        self.timer.timeout.connect(self._update)
        

    def to_tare(self):
        global F1_resting_value, F2_resting_value
        self.to_tare_bool = True
        F1_resting_value = 0
        F2_resting_value = 0

    def to_read_FP_data(self):
        global data1, data2
        data1 = np.array([])
        data2 = np.array([])
        self.timer.start(10)

        self.to_read_FP_data_bool = True

    def open_Calibration_page_for_sync_between_force_plates_and_camera_1(self):
        global data1, data2
        self.timer.stop()
        self.to_read_FP_data_bool = False
        try:
            self.ser.close()
        except:
            pass
        self.force_plate_calibration_page.show_Calibration_page_for_sync_between_force_plates_and_camera_1()

    def _update(self):
            global data1, data2
            global F1_resting_value, F2_resting_value
            global iteration
            iteration += 1
            time = iteration * time_interval #Calculate the time using the serial number
            time_string = "{:06.3f}".format(time)

            if self.to_read_FP_data_bool == True:
                if dummy_FP_data == False:
                    self.ser = serial.Serial('/dev/ttyUSB0', 115200, 8, 'N', 2, timeout=1) #open serial port
                    hex_list = []
                    output = self.ser.read_until(b'\r\n')
                    output_hex = output.hex() #convert serial to hex
                    if (len(output_hex)) == 42:
                        hex_list.extend([output_hex[6:10], output_hex[10:14], #[Iteration, F1, F2]
                        output_hex[14:18], output_hex[18:22], output_hex[22:26], #[X1, Y1, Z1]
                        output_hex[26:30], output_hex[30:34], output_hex[34:38]]) #[X2, Y2, Z2]
                        integer_list = []
                        integer_list = map(twos_complement_16bits, hex_list) #convert all hex elements into int 
                        integer_list = list(integer_list) #convert map type to list type
                        FP1, FP2 = return_calibrated_force_plate_values(integer_list[0], integer_list[1])
                        FP1 = round(FP1 - F1_resting_value)
                        FP2 = round(FP2 - F2_resting_value)
                        if self.to_tare_bool == True:
                            if len(self.FP1_resting_value_list) <= self.tare_holding_data_quantity: #10
                                self.FP1_resting_value_list.append(FP1)
                                self.FP2_resting_value_list.append(FP2)
                                value = self.progress_bar.value()
                                value += 100/self.tare_holding_data_quantity
                                self.progress_bar.setValue(int(value))

                            else:
                                self.to_tare_bool = False
                                F1_resting_value = sum(self.FP1_resting_value_list)/len(self.FP1_resting_value_list)
                                F2_resting_value = sum(self.FP2_resting_value_list)/len(self.FP2_resting_value_list)
                                self.FP1_resting_value_list = []
                                self.FP2_resting_value_list = []
                        else:
                            self.progress_bar.setValue(0)

                        if len(data1) < self.numPoints: 
                            data1 = np.append(data1, FP1)
                        else:
                            data1[:-1] = data1[1:]
                            data1[-1] = FP1

                        if len(data2) < self.numPoints:
                            data2 = np.append(data2, FP2)
                        else:
                            data2[:-1] = data2[1:]
                            data2[-1] = FP2

                        xAxis = np.arange(0, len(data1))
                        yAxis1 = data1
                        yAxis2 = data2

                        self.x = np.arange(len(data1))  # Update x-axis data
                        self.y1 = yAxis1  # Update y-axis data for plot 1
                        self.y2 = yAxis2  # Update y-axis data for plot 2
                        self.drawplot1.setData(self.x, self.y1)
                        self.drawplot2.setData(self.x, self.y2)
                        self.FP1_plate_value_label.setText("{}: {} Newton".format("FP1", str(FP1)))
                        self.FP2_plate_value_label.setText("{}: {} Newton".format("FP2", str(FP2)))
      
                else:
                    integer_list = [10 for _ in range(8)]
                    integer_list.insert(0,iteration)
                    integer_list.insert(0, time_string)
                    FP1, FP2 = integer_list[2], integer_list[3]
                    FP1 = round(FP1 - F1_resting_value)
                    FP2 = round(FP2 - F2_resting_value)
                    if self.to_tare_bool == True:
                        if len(self.FP1_resting_value_list) <= self.tare_holding_data_quantity: #10
                            self.FP1_resting_value_list.append(FP1)
                            self.FP2_resting_value_list.append(FP2)
                            value = self.progress_bar.value()
                            value += 100/self.tare_holding_data_quantity
                            self.progress_bar.setValue(int(value))

                        else:
                            self.to_tare_bool = False
                            F1_resting_value = sum(self.FP1_resting_value_list)/len(self.FP1_resting_value_list)
                            F2_resting_value = sum(self.FP2_resting_value_list)/len(self.FP2_resting_value_list)
                            self.FP1_resting_value_list = []
                            self.FP2_resting_value_list = []
                    else:
                        self.progress_bar.setValue(0)

                    if len(data1) < self.numPoints: 
                        data1 = np.append(data1, FP1)
                    else:
                        data1[:-1] = data1[1:]
                        data1[-1] = FP1

                    if len(data2) < self.numPoints:
                        data2 = np.append(data2, FP2)
                    else:
                        data2[:-1] = data2[1:]
                        data2[-1] = FP2

                    xAxis = np.arange(0, len(data1))
                    yAxis1 = data1
                    yAxis2 = data2

                    self.x = np.arange(len(data1))  # Update x-axis data
                    self.y1 = yAxis1  # Update y-axis data for plot 1
                    self.y2 = yAxis2  # Update y-axis data for plot 2
                    self.drawplot1.setData(self.x, self.y1)
                    self.drawplot2.setData(self.x, self.y2)
                    self.FP1_plate_value_label.setText("{}: {} kg".format("FP1", str(FP1)))
                    self.FP2_plate_value_label.setText("{}: {} kg".format("FP2", str(FP2)))
                    
                
class Calibration_page_for_sync_between_force_plates_and_camera_1(QWidget):
    def __init__(self, force_plate_calibration_page):
        super().__init__()
        self.setWindowTitle("Calibration_Page_for_sync_between_force_plates_and_camera_1")
        self.setGeometry(100, 100, 1600, 800)
        # Create a vertical layout manager for the main menu page
        self.force_plate_calibration_page = force_plate_calibration_page
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        #Text for title
        self.description_label_1 = QLabel("This process will involve the sync between the force plates and camera", self)
        self.description_label_1.setFont(QFont("Arial", 24))
        layout.addWidget(self.description_label_1)

        #Text for instructions
        self.description_label_2 = QLabel("Step 1:\nPress the start button to start the video recording and data collection, recommended\nto be 5 seconds before applying force on the plates\n\nStep 2:\nPress about 5 to 10 times\n\nStep 3:\nClick the stop button\n\nStep 4:\nVideo will be played, user can figured out the delay\n\nStep 5:\nChoose either the graph or video, and key in the delay in seconds\n\nStep 6:\nClick delay button", self)
        self.description_label_2.setFont(QFont("Arial", 15))
        self.description_label_2.move(0, 100)

        #Create Back to plate calibration button
        self.back_to_plate_calibration_button = QPushButton("Back to plate calibration", self)
        self.back_to_plate_calibration_button.clicked.connect(self.open_calibration_page_for_force_plates)
        self.back_to_plate_calibration_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.back_to_plate_calibration_button.move(0, 700)
        layout.addWidget(self.back_to_plate_calibration_button) 

        # Create proceed to sync button
        self.proceed_to_sync_button = QPushButton("proceed to sync", self)
        self.proceed_to_sync_button.clicked.connect(self.open_Calibration_page_for_sync_between_force_plates_and_camera_2)
        self.proceed_to_sync_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.proceed_to_sync_button.move(900, 700)
        layout.addWidget(self.proceed_to_sync_button) 
        
    def open_calibration_page_for_force_plates(self):
        self.force_plate_calibration_page.show_Force_plate_calibration_page()
    
    def open_Calibration_page_for_sync_between_force_plates_and_camera_2(self):
        self.force_plate_calibration_page.show_Calibration_page_for_sync_between_force_plates_and_camera_2()

#====================================================================================================================
class Calibration_page_for_sync_between_force_plates_and_camera_2(QWidget):
    def __init__(self, force_plate_calibration_page):
        super().__init__()
        self.setWindowTitle("Calibration_Page_for_sync_between_force_plates_and_camera_2")
        self.setGeometry(100, 100, 1600, 800)
        # Create a vertical layout manager for the main menu page
        self.force_plate_calibration_page = force_plate_calibration_page
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.to_read_live_data_bool = False

        #for video ouput
        self.video_recorded_frames =[]

        #for both video and forceplates ouput
        self.recording_length = 0
        self.recording_framecount = 0
    
        #widgets
            #Data output
                #video output
        self.w9_video_output = VideoStreamWidget()
        self.w9_video_output.setFixedSize(800, 500)
        self.layout.addWidget(self.w9_video_output, 0, 2, 2, 2)
        

                 # Create and insert Graphics Layout to layout
        self.canvas = pg.GraphicsLayoutWidget()
        self.canvas.setFixedSize(800, 500) 
        self.layout.layout().addWidget(self.canvas, 0, 0, 2, 2)

                    #Create analogplots for force plate 1 and 2
        self.analogPlot1 = self.canvas.addPlot(title='Force Plate 1',  row = 0, col = 0)
        self.analogPlot1.enableAutoRange(enable = True)
        self.analogPlot1.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase

        self.analogPlot2 = self.canvas.addPlot(title='Force Plate 2',  row = 1, col = 0)
        self.analogPlot2.enableAutoRange(enable = True)
        self.analogPlot2.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase
        self.analogPlot2.enableAutoRange(enable = True)
                        #Initiatlisation for FP output
        self.numPoints = 500
        self.fps = 0.0
        self.lastupdate = time.time()
        self.x = np.arange(self.numPoints)
        self.recorded_x =[]
        self.recorded_y1 = []
        self.recorded_y2 = []
        self.y1 = np.zeros(self.numPoints)
        self.y2 = np.zeros(self.numPoints)
        self.drawplot1 = self.analogPlot1.plot(pen='y')
        self.drawplot2 = self.analogPlot2.plot(pen='g')
        self.frames_graph_delay = 0

            #Slider
        self.w1_adjust_video_FP_slider = QSlider(Qt.Horizontal, self)
        self.w1_adjust_video_FP_slider.setFixedSize(800, 20)
        self.layout.addWidget(self.w1_adjust_video_FP_slider,2,0,1,2)

            #Buttons
        self.w2_display_live_output_button = QPushButton('display live output', self)
        self.w2_display_live_output_button.clicked.connect(self.w2_display_live_output_button_fn)
        self.w2_display_live_output_button.setFixedSize(400, 30)
        self.layout.addWidget(self.w2_display_live_output_button, 2, 2)

        self.w3_start_recording_output_button = QPushButton('start recording output', self)
        self.w3_start_recording_output_button.clicked.connect(self.w3_start_recording_output_button_fn)
        self.layout.addWidget(self.w3_start_recording_output_button, 2, 3)

        self.w4_replay_recorded_output_button = QPushButton('replay recorded output', self)
        self.w4_replay_recorded_output_button.clicked.connect(self.w4_replay_recorded_output_button_fn)
        self.layout.addWidget(self.w4_replay_recorded_output_button, 4, 0)

        self.w5_play_recorded_output_button = QPushButton('resume recorded output', self)
        self.layout.addWidget(self.w5_play_recorded_output_button, 4,1)
        self.w5_play_recorded_output_button.clicked.connect(self.w5_play_recorded_output_button_fn)

        self.w6_pause_recording_button = QPushButton('pause recording', self)
        self.w6_pause_recording_button.clicked.connect(self.w6_pause_recording_button_fn)
        self.layout.addWidget(self.w6_pause_recording_button,5, 1)

        self.w7_proceed_to_next_page_button = QPushButton('proceed to next page', self)
        self.w7_proceed_to_next_page_button.clicked.connect(self.w7_proceed_to_next_page_button_fn)
        self.layout.addWidget(self.w7_proceed_to_next_page_button, 6, 3)

        self.w8_clear_recording_button = QPushButton('clear recording', self)
        self.w8_clear_recording_button.clicked.connect(self.w8_clear_recording_button_fn)
        self.layout.addWidget(self.w8_clear_recording_button, 4, 3)

        self.w9_back_to_previous_page_button = QPushButton('back to previous page', self)
        self.w9_back_to_previous_page_button.clicked.connect(self.w9_back_to_previous_page_button_fn)
        self.layout.addWidget(self.w9_back_to_previous_page_button, 6,0)

        self.w10_confirm_delay_of_graph_output_button = QPushButton('confirm delay of graph output button', self)
        self.w10_confirm_delay_of_graph_output_button.setFixedSize(400, 30)
        self.w10_confirm_delay_of_graph_output_button.clicked.connect(self.w10_confirm_delay_of_graph_output_button_fn)
        self.layout.addWidget(self.w10_confirm_delay_of_graph_output_button, 4, 2)
        
        self.w11_title_for_delay_of_graph_output_label = QLabel("Key in Delay in frames: ", self)
        self.w11_title_for_delay_of_graph_output_label.setFixedSize(400, 30)
        self.layout.addWidget(self.w11_title_for_delay_of_graph_output_label, 3,2)

        #Delay textfield
        self.w12_delay_of_graph_output_textfield = QLineEdit(self)
        self.w12_delay_of_graph_output_textfield.setFixedSize(400, 30)
        self.layout.addWidget(self.w12_delay_of_graph_output_textfield, 3, 3)

        self.w14_current_frame_versus_total_frames_label = QLabel("NA frame: 200 total frames", self)
        self.layout.addWidget(self.w14_current_frame_versus_total_frames_label, 3, 0)

        #Initialise state after widgets have ran
        self.state = 1
        self._state_update()

        #Qtimer connection
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(interval_ms)

    #functions
    def w1_adjust_video_FP_slider_valueChanged_update_output_position_fn(self, slider_changed_value):    #change to the user shifted position
        self.recording_framecount = int(slider_changed_value / 100 * (self.recording_length - 1))   #reset frame count to changed slider value
        replaying_Qtimage = self.video_recorded_frames[self.recording_framecount]
        pixmap = QPixmap.fromImage(replaying_Qtimage)
        self.w9_video_output.setPixmap(pixmap)

        self.w14_current_frame_versus_total_frames_label.setText("{} frame: {} total frames".format(str(self.recording_framecount), str(self.recording_length)))

        self.drawplot1.setData(self.x[0:self.recording_framecount], self.y1[0:self.recording_framecount])
        self.drawplot2.setData(self.x[0:self.recording_framecount], self.y2[0:self.recording_framecount])
        # self.w1_adjust_video_FP_slider.setValue(int(self.recording_framecount / (self.recording_length - 1) * 100))

    def w2_display_live_output_button_fn(self):
        self.state = 2
        self.display_live_output_start_time = datetime.now()
        self._state_update()

    def w3_start_recording_output_button_fn(self):
        self.state = 3
        self.recording_start_time = datetime.now()
        self._state_update()

    def w4_replay_recorded_output_button_fn(self):
        self.state = 5
        self.recording_framecount = 0
        self.playback_start_time = datetime.now()
        self._state_update()

    def w5_play_recorded_output_button_fn(self): #Ensure it goes to s4 when done playing
        self.state = 5
        self._state_update()

    def w6_pause_recording_button_fn(self):
        self.state = 6
        self._state_update()

    def w7_proceed_to_next_page_button_fn(self):
        self.state = 1
        self.force_plate_calibration_page.show_Main_Menu_Page()
        self._state_update()

    def w8_clear_recording_button_fn(self):
        self.state = 1
        self.frames_graph_delay = 0
        self._state_update()
    
    def w9_back_to_previous_page_button_fn(self):
        self.state = 1
        self.force_plate_calibration_page.show_Calibration_page_for_sync_between_force_plates_and_camera_1()
        self._state_update()

    def w10_confirm_delay_of_graph_output_button_fn(self):
        self.frames_graph_delay = int(self.w12_delay_of_graph_output_textfield.text())

    def _update(self):
        if (self.state == 1) or (self.state == 4) or (self.state == 6) or (self.state == 7):
            self.timer.stop() #stop the Qtimer
            
        elif (self.state == 2) or (self.state == 3):            
            global data1, data2
            global iteration
            iteration += 1
            time = iteration * time_interval #Calculate the time using the serial number
            time_string = "{:06.3f}".format(time)
            #================================
            if self.to_read_live_data_bool == True:
                if dummy_FP_data == False:
                    self.ser = serial.Serial('/dev/ttyUSB0', 115200, 8, 'N', 2, timeout=1) #open serial port
                    hex_list = []
                    output = self.ser.read_until(b'\r\n')
                    output_hex = output.hex() #convert serial to hex
                    if (len(output_hex)) == 42:
                        hex_list.extend([output_hex[6:10], output_hex[10:14], #[Iteration, F1, F2]
                        output_hex[14:18], output_hex[18:22], output_hex[22:26], #[X1, Y1, Z1]
                        output_hex[26:30], output_hex[30:34], output_hex[34:38]]) #[X2, Y2, Z2]
                        integer_list = []
                        integer_list = map(twos_complement_16bits, hex_list) #convert all hex elements into int 
                        integer_list = list(integer_list) #convert map type to list type

                        FP1, FP2 = return_calibrated_force_plate_values(integer_list[2], integer_list[3])
                        FP1 = round(FP1 - F1_resting_value)
                        FP2 = round(FP2 - F2_resting_value)

                        self.video_frame_iterated += 1
                        if self.video_frame_iterated >= self.frames_graph_delay:
                            if len(data1) < self.numPoints: 
                                data1 = np.append(data1, FP1)

                            else:
                                data1[:-1] = data1[1:]
                                data1[-1] = FP1

                            if len(data2) < self.numPoints:
                                data2 = np.append(data2, FP2)
                            else:
                                data2[:-1] = data2[1:]
                                data2[-1] = FP2

                            yAxis1 = data1
                            yAxis2 = data2

                            self.x = np.arange(len(data1))  # Update x-axis data
                            self.y1 = yAxis1  # Update y-axis data for plot 1
                            self.y2 = yAxis2  # Update y-axis data for plot 2
                            self.drawplot1.setData(np.arange(len(self.y1[0:self.graph_plotting_backtrack])), self.y1[0:self.graph_plotting_backtrack])
                            self.drawplot2.setData(np.arange(len(self.y1[0:self.graph_plotting_backtrack])), self.y2[0:self.graph_plotting_backtrack])
                            self.graph_plotting_backtrack += 1

                        else:
                            data1 = np.append(data1, FP1)
                            data2 = np.append(data2, FP2)

                            
                        if self.state == 3:
                            #data recording of FP1 and FP2
                            self.recorded_x.append(len(data1))
                            self.recorded_y1.append(FP1)
                            self.recorded_y2.append(FP2)

                            #data collection of video frames
                            self.video_recorded_frames.append(qt_image)
                            
                            #counting the total frames for both video and graph
                            self.recording_length = len(self.recorded_x)
                            self.recorded_y1.append(FP1)
                            self.recorded_y2.append(FP2)
                            if self.recording_length >= 200:
                                self.state = 4  #recording completed state
                                recording_end_time = datetime.now()
                                recording_duration = recording_end_time - self.recording_start_time
                                self.recording_playback_interval_ms = recording_duration.total_seconds()/200
                                self._state_update()

                else:
                    #integer_list = [10 for _ in range(8)]
                    integer_list = [iteration, iteration] ##remove and unremove the above line
                    integer_list.insert(0,iteration)
                    integer_list.insert(0, time_string)

                    FP1, FP2 = integer_list[2], integer_list[3]
                    FP1 = round(FP1 - F1_resting_value)
                    FP2 = round(FP2 - F2_resting_value)

                    self.video_frame_iterated += 1
                    if self.video_frame_iterated >= self.frames_graph_delay:
                        if len(data1) < self.numPoints: 
                            data1 = np.append(data1, FP1)

                        else:
                            data1[:-1] = data1[1:]
                            data1[-1] = FP1

                        if len(data2) < self.numPoints:
                            data2 = np.append(data2, FP2)
                        else:
                            data2[:-1] = data2[1:]
                            data2[-1] = FP2

                        yAxis1 = data1
                        yAxis2 = data2

                        self.x = np.arange(len(data1))  # Update x-axis data
                        self.y1 = yAxis1  # Update y-axis data for plot 1
                        self.y2 = yAxis2  # Update y-axis data for plot 2
                        self.drawplot1.setData(np.arange(len(self.y1[0:self.graph_plotting_backtrack])), self.y1[0:self.graph_plotting_backtrack])
                        self.drawplot2.setData(np.arange(len(self.y1[0:self.graph_plotting_backtrack])), self.y2[0:self.graph_plotting_backtrack])
                        self.graph_plotting_backtrack += 1

                    else:
                        data1 = np.append(data1, FP1)
                        data2 = np.append(data2, FP2)

                    if self.state == 3:
                        #data recording of FP1 and FP2
                        self.recorded_x.append(len(data1))
                        self.recorded_y1.append(FP1)
                        self.recorded_y2.append(FP2)

                        #data collection of video frames
                        self.video_recorded_frames.append(qt_image)
                        
                        #counting the total frames for both video and graph
                        self.recording_length = len(self.recorded_x)
                        self.recorded_y1.append(FP1)
                        self.recorded_y2.append(FP2)
                        if self.recording_length >= 200:
                            self.state = 4  #recording completed state
                            recording_end_time = datetime.now()
                            recording_duration = recording_end_time - self.recording_start_time
                            self.recording_playback_interval_ms = recording_duration.total_seconds()/200
                            self._state_update()

        elif (self.state == 5):   #while replaying from clicking replay (start from time = 0) or play after pausing (starts after time = 0)
            if self.recording_framecount < len(self.video_recorded_frames):
                replaying_Qtimage = self.video_recorded_frames[self.recording_framecount]
                pixmap = QPixmap.fromImage(replaying_Qtimage)
                self.w9_video_output.setPixmap(pixmap)

                self.drawplot1.setData(self.x[0:self.recording_framecount], self.y1[0:self.recording_framecount])
                self.drawplot2.setData(self.x[0:self.recording_framecount], self.y2[0:self.recording_framecount])
                self.w1_adjust_video_FP_slider.setValue(int(self.recording_framecount / (self.recording_length - 1) * 100))
                self.recording_framecount += 1

            else:
                playback_endtime = datetime.now()
                
                self.state = 4  #replaying done or recording completed
                self._state_update()


    def _state_update(self):
        global data1, data2, iteration
        if self.state == 1:  #Initial Page
            self.w9_video_output.toggle_pause()
            #To save video ouput frames
            self.video_recorded_frames =[]

            #To empty out list FP1 and FP2
            iteration = 0
            data1 = np.array([])
            data2 = np.array([])
            self.x = []
            self.y1 = []
            self.y2 = []
            self.recorded_x = []
            self.recorded_y1 = []
            self.recorded_y2 = []
            self.drawplot1.setData([0],[0])
            self.drawplot2.setData([0],[0])
            #for both video and forceplates ouput
            self.recording_framecount = 0
            self.recording_length = len(self.video_recorded_frames)
            #for sync
            self.video_frame_iterated = 0
            self.graph_plotting_backtrack = 1


            self.w1_adjust_video_FP_slider.setEnabled(False)
            self.w3_start_recording_output_button.setEnabled(False)
            self.w4_replay_recorded_output_button.setEnabled(False)
            self.w5_play_recorded_output_button.setEnabled(False)
            self.w6_pause_recording_button.setEnabled(False)
            self.w8_clear_recording_button.setEnabled(False)

            self.w2_display_live_output_button.setEnabled(True)

        elif self.state == 2:   #Live Outputs are displaying
            self.w9_video_output.read_cap()
            self.w9_video_output.toggle_play()
            self.to_read_live_data_bool = True
            self.timer.start(interval_ms)   #start the timer for _update

            self.w1_adjust_video_FP_slider.setEnabled(False)
            self.w2_display_live_output_button.setEnabled(False)
            self.w4_replay_recorded_output_button.setEnabled(False)
            self.w5_play_recorded_output_button.setEnabled(False)
            self.w6_pause_recording_button.setEnabled(False)   
            self.w8_clear_recording_button.setEnabled(False)         
            self.w3_start_recording_output_button.setEnabled(True)
            self.w7_proceed_to_next_page_button.setEnabled(True)

        elif self.state == 3:    #Midst of recording
            self.w1_adjust_video_FP_slider.setEnabled(False)
            self.w2_display_live_output_button.setEnabled(False)
            self.w3_start_recording_output_button.setEnabled(False)
            self.w4_replay_recorded_output_button.setEnabled(False)
            self.w5_play_recorded_output_button.setEnabled(False)
            self.w6_pause_recording_button.setEnabled(False)   
            self.w7_proceed_to_next_page_button.setEnabled(False)
            self.w8_clear_recording_button.setEnabled(False)    

        elif self.state == 4:    #Recording completed or video finished playing
            self.w9_video_output.toggle_pause()
            self.recording_framecount = 0
            self.w1_adjust_video_FP_slider.valueChanged.connect(self.w1_adjust_video_FP_slider_valueChanged_update_output_position_fn)
            self.w9_video_output.toggle_stop_cap()

            self.w1_adjust_video_FP_slider.setEnabled(True)
            self.w2_display_live_output_button.setEnabled(False)
            self.w3_start_recording_output_button.setEnabled(False)
            self.w5_play_recorded_output_button.setEnabled(False)
            self.w6_pause_recording_button.setEnabled(False)
             
            self.w7_proceed_to_next_page_button.setEnabled(True)
            self.w4_replay_recorded_output_button.setEnabled(True)
            self.w8_clear_recording_button.setEnabled(True)  

        elif self.state == 5:    #While replaying
            self.timer.start(round(self.recording_playback_interval_ms*1000))
            self.w1_adjust_video_FP_slider.setValue(int(self.recording_framecount / (self.recording_length - 1) * 100))
            self.w1_adjust_video_FP_slider.valueChanged.disconnect(self.w1_adjust_video_FP_slider_valueChanged_update_output_position_fn)
            self.w14_current_frame_versus_total_frames_label.setText("{} frame: {} total frames".format(str(self.recording_framecount), str(self.recording_length)))
            self.w6_pause_recording_button.setEnabled(True)

            self.w1_adjust_video_FP_slider.setEnabled(False)
            self.w2_display_live_output_button.setEnabled(False)
            self.w3_start_recording_output_button.setEnabled(False)
            self.w4_replay_recorded_output_button.setEnabled(False)
            self.w5_play_recorded_output_button.setEnabled(False)
            self.w7_proceed_to_next_page_button.setEnabled(False)
            self.w8_clear_recording_button.setEnabled(False) 

        elif self.state == 6:    #Output is now Paused
            self.w1_adjust_video_FP_slider.valueChanged.connect(self.w1_adjust_video_FP_slider_valueChanged_update_output_position_fn)

            self.w1_adjust_video_FP_slider.setEnabled(True)
            self.w1_adjust_video_FP_slider.setEnabled(True)
            self.w8_clear_recording_button.setEnabled(True)
            self.w5_play_recorded_output_button.setEnabled(True)
            self.w4_replay_recorded_output_button.setEnabled(True)
            
            self.w3_start_recording_output_button.setEnabled(False)
            self.w6_pause_recording_button.setEnabled(False)   
            self.w7_proceed_to_next_page_button.setEnabled(False)
            self.w8_clear_recording_button.setEnabled(False)
        

        else: #state 7: Adjusted outputs positions
            self.w1_adjust_video_FP_slider.setEnabled(True)
            self.w1_adjust_video_FP_slider.setEnabled(True)
            self.w5_play_recorded_output_button.setEnabled(True)
            self.w8_clear_recording_button.setEnabled(True)
        
            self.w3_start_recording_output_button.setEnabled(False)
            self.w4_replay_recorded_output_button.setEnabled(False)
            self.w6_pause_recording_button.setEnabled(False)   
            self.w7_proceed_to_next_page_button.setEnabled(False)
            self.w8_clear_recording_button.setEnabled(False)

#====================================================================================================================
 
class MainMenu(QWidget):
    def __init__(self, force_plate_calibration_page):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 1600, 800)
        # Create a vertical layout manager for the main menu page
        self.force_plate_calibration_page = force_plate_calibration_page
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Create Analysis button
        self.analysis_button = QPushButton("Analysis", self)
        self.analysis_button.clicked.connect(self.open_analysis)
        self.analysis_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.analysis_button.move(500, 400)
        layout.addWidget(self.analysis_button)

        # Create Data Collection button
        self.data_collection_button = QPushButton("Data Collection", self)
        self.data_collection_button.clicked.connect(self.open_data_collection)
        self.data_collection_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.data_collection_button.move(900, 400)
        layout.addWidget(self.data_collection_button)

        #Create back to sync page
        self.back_button = QPushButton("Back", self)
        self.back_button.clicked.connect(self.open_Calibration_page_for_sync_between_force_plates_and_camera_2)
        self.back_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.back_button.move(1300, 400)
        layout.addWidget(self.back_button)

    def open_analysis(self):
        print("Analysis button clicked")
        # Add your code here to open the analysis window or perform any actions related to analysis
        self.force_plate_calibration_page.show_Analysis_Selection_Page()

    def open_data_collection(self):
        print("Data Collection button clicked")
        self.force_plate_calibration_page.show_Training_page()

    def open_Calibration_page_for_sync_between_force_plates_and_camera_2(self):
        self.force_plate_calibration_page.show_Calibration_page_for_sync_between_force_plates_and_camera_2()


class Analysis_Selection_Page(QWidget):
    def __init__(self, force_plate_calibration_page):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 1600, 800)
        # Create a vertical layout manager for the main menu page
        self.force_plate_calibration_page = force_plate_calibration_page
        self.mainbox = QVBoxLayout()
        self.mainbox.setAlignment(Qt.AlignCenter)

        # Create Analysis button
        self.comparison_analysis_button = QPushButton("Comparison Analysis", self)
        self.comparison_analysis_button.clicked.connect(self.comparison_analysis)
        self.comparison_analysis_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.comparison_analysis_button.move(500, 400)
        self.mainbox.addWidget(self.comparison_analysis_button)

        # Create Data Collection button
        self.individual_analysis_button = QPushButton("Individual Analysis", self)
        self.individual_analysis_button.clicked.connect(self.individual_analysis)
        self.individual_analysis_button.setFixedSize(200, 50)  # Set the fixed size of the button
        self.individual_analysis_button.move(900, 400)
        self.mainbox.addWidget(self.individual_analysis_button)

        # Create Back button
        self.back_button = QPushButton("Back", self)
        self.back_button.clicked.connect(self.back_button_clicked)
        self.back_button.setFixedSize(200, 50)
        self.back_button.move(700, 600)
        self.mainbox.addWidget(self.back_button)



    def comparison_analysis(self):
        print("Comparison Analysis Button Clicked")
        #Navigate to comparison analysis data selection page
        self.force_plate_calibration_page.show_Comparison_Analysis_Selection_Page()

    def individual_analysis(self):
        print("Individual Analysis Button Clicked")
        #Navigate to individual analysis profile selection page
        self.force_plate_calibration_page.show_Analysis_Profile_Selection_Page()

    def back_button_clicked(self):
        self.force_plate_calibration_page.show_Main_Menu_Page()


class Comparison_Analysis_Selection_Page(QWidget):
    def __init__(self, force_plate_calibration_page, parent=None):  # Add a second argument for the parent
        super().__init__(parent)
        self.force_plate_calibration_page = force_plate_calibration_page
        self.setWindowTitle("File Selection GUI")
        self.setGeometry(100, 100, 1600, 800)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.file_model = QStandardItemModel()
        self.tree_view = FileTreeView(self.file_model)
        layout.addWidget(self.tree_view)

        # Set the root path
        self.root_path = athletes_file_path
        self.populate_tree(self.root_path, self.file_model, self.root_path)

        select_button = QPushButton("Select Files")
        select_button.clicked.connect(self.get_selected_files)
        layout.addWidget(select_button)

        # Create the Back Button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_button_clicked)  # Add a function to handle the button click
        layout.addWidget(back_button)


        self.setLayout(layout)

    def populate_tree(self, directory_path, parent_item, full_directory_path):
        items = os.listdir(directory_path)
        items.sort()
        for item_name in items:
            item_path = os.path.join(directory_path, item_name)
            item = QStandardItem(item_name)
            if os.path.isdir(item_path):
                item.setCheckable(False)  # Folders should not have checkboxes
                self.populate_tree(item_path, item, os.path.join(full_directory_path, item_name))
            else:
                item.setCheckable(True)  # Files should have checkboxes
            parent_item.appendRow(item)

    def get_selected_files(self):
        selected_files = self.get_checked_files(self.file_model.invisibleRootItem(), '')
        print("Selected Files:")
        self.file_directory_list = []
        self.file_name_list = []
        for file in selected_files:
            file_directory = os.path.join(self.root_path, file)
            self.file_directory_list.append(file_directory)
            self.file_name_list.append(file)
            # print(file)
        self.force_plate_calibration_page.show_Comparison_Analysis_Page(self.file_directory_list, self.file_name_list)

    def get_checked_files(self, item, directory_path):
        selected_files = []
        for row in range(item.rowCount()):
            child_item = item.child(row)
            if child_item.isCheckable() and child_item.checkState() == Qt.Checked:
                file_name = child_item.text()
                selected_files.append(os.path.join(directory_path, file_name))
            if child_item.hasChildren():
                selected_files.extend(self.get_checked_files(child_item, os.path.join(directory_path, child_item.text())))
        return selected_files
    
    def back_button_clicked(self):
        self.force_plate_calibration_page.show_Analysis_Selection_Page()

    
class FileTreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setHeaderHidden(True)  # Hide the header (top-level directory name)

class Comparison_Analysis_Page(QWidget):
    def __init__(self, force_plate_calibration_page, file_directory_list, file_name_list, parent=None):
        super(Comparison_Analysis_Page, self).__init__(parent)
        self.force_plate_calibration_page = force_plate_calibration_page
        self.file_directory_list = file_directory_list
        self.file_name_list = file_name_list
        self.COT_Graph = False
        self.max_forces_FP1 = []
        self.max_forces_FP2 = []
        self.Time_Taken_to_Max_FP1 = []
        self.Time_Taken_to_Max_FP2 = []
        self.COT_Time = []

        for dir in self.file_directory_list:
            df = pd.read_csv(dir)
            force_plate_1 = df['Force plate 1'].tolist()
            force_plate_2 = df['Force plate 2'].tolist()
            Time = df['Time'].tolist()
            self.max_forces_FP1.append(max(force_plate_1))
            self.max_forces_FP2.append(max(force_plate_2))
            self.Time_Taken_to_Max_FP1.append(Time[force_plate_1.index(max(force_plate_1))])
            self.Time_Taken_to_Max_FP2.append(Time[force_plate_2.index(max(force_plate_2))])
            cot_time_list = df['COT'].tolist()
            if max(cot_time_list) == -1:
                self.COT_Time.append(0)
            else:    
                self.COT_Time.append(max(cot_time_list))            

        self.setup_ui()

    def setup_ui(self):
        self.mainbox = QVBoxLayout(self)
        self.mainbox.setAlignment(Qt.AlignCenter)

        # Create the button and set its text and size
        button = QPushButton("Back")
        button.setFixedSize(150, 50)
        button.clicked.connect(self.back_button_clicked)

        self.COT_Comparison_button = QPushButton("COT Comparison")
        self.COT_Comparison_button.setFixedSize(200, 50)
        self.COT_Comparison_button.clicked.connect(self.COT_Comparison)

        self.Force_Comparison_button = QPushButton("Force Comparison")
        self.Force_Comparison_button.setFixedSize(200, 50)
        self.Force_Comparison_button.clicked.connect(self.Force_Comparison)

        # Add the button to the layout in the top right position
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.addWidget(button, alignment=Qt.AlignRight)
        button_layout.addWidget(self.COT_Comparison_button, alignment=Qt.AlignRight)
        button_layout.addWidget(self.Force_Comparison_button, alignment=Qt.AlignRight)

        self.Force_Comparison_button.setVisible(False)

        # Add the button widget to the main layout
        self.mainbox.addWidget(button_widget)

        #Setting up Top two Bargraph
        self.top_bargraph_widget = QWidget()
        self.top_bargraph_layout = QHBoxLayout(self.top_bargraph_widget)
        self.canvas = pg.GraphicsLayoutWidget()
        self.top_bargraph_layout.addWidget(self.canvas)
        self.create_bar_graph(self.max_forces_FP1, 'Max Forces FP1', self.file_name_list, self.canvas)

        self.canvas2 = pg.GraphicsLayoutWidget()
        self.top_bargraph_layout.addWidget(self.canvas2)
        self.create_bar_graph(self.max_forces_FP2, 'Max Forces FP2', self.file_name_list, self.canvas2)

        self.mainbox.addWidget(self.top_bargraph_widget)
        self.mainbox.addLayout(self.top_bargraph_layout)

        #Setting up Bottom two bargraph
        self.bottom_bargraph_widget = QWidget()
        self.bottom_bargraph_layout = QHBoxLayout(self.bottom_bargraph_widget)
        self.canvas3 = pg.GraphicsLayoutWidget()
        self.bottom_bargraph_layout.addWidget(self.canvas3)
        self.create_bar_graph(self.Time_Taken_to_Max_FP1, 'Time Taken to Max FP1', self.file_name_list, self.canvas3)

        self.canvas4 = pg.GraphicsLayoutWidget()
        self.bottom_bargraph_layout.addWidget(self.canvas4)       
        self.create_bar_graph(self.Time_Taken_to_Max_FP2, 'Time Taken to Max FP2', self.file_name_list, self.canvas4)

        self.mainbox.addWidget(self.bottom_bargraph_widget)
        self.mainbox.addLayout(self.bottom_bargraph_layout)
 
        self.setLayout(self.mainbox)

    def create_bar_graph(self, values, title, file_names, canvas):
        legend = pg.LegendItem(offset=(90,10))
        plot_item = canvas.addPlot(title=title)
        file_name = file_names
        x = np.arange(len(self.file_name_list)) + 1
        if len(values) == 1:
            # Handle the case when there's only one value
            y = np.array([values[0]])
        else:
            # When there are multiple values
            y = np.array(values)

        colors = ['g', 'y', 'c', 'r', 'b', 'm', 'k']

        for xi, yi, col, namesi in zip(x, y, colors, file_name):
            bg = pg.BarGraphItem(x=[xi], height=[yi], width=0.5, brush=col)
            plot_item.addItem(bg)
            #Add text label to the middle of the bars
            label = pg.TextItem(text=f'{yi:.2f}', color=(0, 0, 0))
            label.setPos((xi - 0.25), yi)
            plot_item.addItem(label)
            #Setting the legends
            legend.addItem(bg, name=namesi)
        #Adding Legends to the plot    
        canvas.addItem(legend)

        plot_item.getAxis('bottom').setTicks([(i + 0.5, name) for i, name in enumerate(self.file_name_list)])

    def back_button_clicked(self):
        self.force_plate_calibration_page.show_Comparison_Analysis_Selection_Page()

    def COT_Comparison(self):
        # Toggle the visibility of the bar graphs by hiding/showing the corresponding widgets
        self.canvas.setVisible(not self.canvas.isVisible())
        self.canvas2.setVisible(not self.canvas2.isVisible())
        self.canvas3.setVisible(not self.canvas3.isVisible())
        self.canvas4.setVisible(not self.canvas4.isVisible())

        if self.COT_Graph == False:
            self.top_bargraph_widget = QWidget()
            self.top_bargraph_layout = QHBoxLayout(self.top_bargraph_widget)
            self.canvas5 = pg.GraphicsLayoutWidget()
            self.top_bargraph_layout.addWidget(self.canvas5)
            self.create_bar_graph(self.COT_Time, 'COT', self.file_name_list, self.canvas5)

            self.mainbox.addWidget(self.top_bargraph_widget)
            self.mainbox.addLayout(self.top_bargraph_layout)

            self.setLayout(self.mainbox)
            self.COT_Graph = True
        
        if self.COT_Graph == True:
            self.canvas5.setVisible(not self.canvas5.isVisible())
        
        self.COT_Comparison_button.setVisible(False)
        self.Force_Comparison_button.setVisible(True)

    def Force_Comparison(self):
        # Toggle the visibility of the bar graphs by hiding/showing the corresponding widgets
        self.canvas.setVisible(not self.canvas.isVisible())
        self.canvas2.setVisible(not self.canvas2.isVisible())
        self.canvas3.setVisible(not self.canvas3.isVisible())
        self.canvas4.setVisible(not self.canvas4.isVisible())
        self.canvas5.setVisible(not self.canvas5.isVisible())
        self.COT_Comparison_button.setVisible(True)
        self.Force_Comparison_button.setVisible(False)     

        

class Analysis_Profile_Selection_Page(QWidget):
    def __init__(self, force_plate_calibration_page):
        super().__init__()
        self.force_plate_calibration_page = force_plate_calibration_page
        # Form.setObjectName("Form")
        # Form.resize(1124, 868)

        self.base_directory =athletes_file_path  # Specify the base directory for profiles

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Create a QGridLayout for the entire page
        self.label = QLabel("Profile Selection:")
        self.Profile_comboBox = QComboBox()
        self.Profile_comboBox.setEditable(True)
        self.Profile_comboBox.currentTextChanged.connect(self.profile_changed)

        self.label_2 = QLabel("Training Type:")
        self.Training_comboBox = QComboBox()
        self.Training_comboBox.setEditable(True)
        self.Training_comboBox.currentTextChanged.connect(self.training_changed)

        self.label_3 = QLabel("Date:")
        self.Date_comboBox = QComboBox()
        self.Date_comboBox.setEditable(True)
        self.Date_comboBox.currentTextChanged.connect(self.date_changed)

        self.label_4 = QLabel("Training Data:")
        self.Data_comboBox = QComboBox()
        self.Data_comboBox.setEditable(True)
        self.Data_comboBox.currentTextChanged.connect(self.data_changed)

        self.pushButton = QPushButton("Next", self)
        self.pushButton.clicked.connect(self.Data_Analysis_Page_Change)

        self.backbutton = QPushButton("Back", self)
        self.backbutton.clicked.connect(self.Analysis_Selection_Page_Change)

        # Add labels and combo boxes to the layout
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.Profile_comboBox, 0, 1)
        layout.addWidget(self.label_2, 1, 0)
        layout.addWidget(self.Training_comboBox, 1, 1)
        layout.addWidget(self.label_3, 2, 0)
        layout.addWidget(self.Date_comboBox, 2, 1)
        layout.addWidget(self.label_4, 3, 0)
        layout.addWidget(self.Data_comboBox, 3, 1)
        layout.addWidget(self.pushButton, 4, 0)
        layout.addWidget(self.backbutton, 5, 0)

        # Add a horizontal spacer to push widgets to the left
        layout.setColumnStretch(2, 1)

        self.setLayout(layout)

        self.load_existing_profiles()

    def load_existing_profiles(self):
        existing_profiles = [f for f in os.listdir(self.base_directory) if os.path.isdir(os.path.join(self.base_directory, f))]
        self.Profile_comboBox.clear()
        # self.Profile_comboBox.addItem("Select Profile")
        self.Profile_comboBox.addItems(existing_profiles)

    def profile_changed(self, text):
        self.profile_directory = os.path.join(self.base_directory, text)
        training_type = [f for f in os.listdir(self.profile_directory) if os.path.isdir(os.path.join(self.profile_directory, f))]
        self.Training_comboBox.clear()
        self.Training_comboBox.addItems(training_type)
        # self.directory_textbox.setText(profile_directory)
        # self.directory_textbox.setReadOnly(True)
        # self.next_button.setText("Next")
        # self.next_button.clicked.disconnect()  # Disconnect previous signal-slot connection
        # self.next_button.clicked.connect(self.save_data) 

    def training_changed(self, text):
        self.training_directory = os.path.join(self.profile_directory, text)
        Date_folder = [f for f in os.listdir(self.training_directory) if os.path.isdir(os.path.join(self.training_directory, f))]
        self.Date_comboBox.clear()
        self.Date_comboBox.addItems(Date_folder)

    def date_changed(self, text):
        self.date_directory = os.path.join(self.training_directory, text)
        data_type = [f for f in os.listdir(self.date_directory) if f.endswith('.csv')]
        self.Data_comboBox.clear()
        self.Data_comboBox.addItems(data_type)

    def data_changed(self, text):
        self.csv_data_directory = os.path.join(self.date_directory, text)

    def Data_Analysis_Page_Change(self):
        data_directory = self.csv_data_directory
        self.force_plate_calibration_page.show_Data_Analysis_Page(data_directory)

    def Analysis_Selection_Page_Change(self):
        self.force_plate_calibration_page.show_Analysis_Selection_Page()

        # if hasattr(self, 'data_analysis_page'):
        #     # The data_analysis_page already exists, set it as the current widget
        #     self.stacked_widget.setCurrentWidget(self.data_analysis_page)
        # else:
        #     # Create a new instance of Data_Analysis_Page and add it to the stacked widget
        #     self.data_analysis_page = Data_Analysis_Page(self, self.data_directory)
        #     self.stacked_widget.addWidget(self.data_analysis_page)
        #     self.stacked_widget.setCurrentWidget(self.data_analysis_page)

class Data_Analysis_Page(QWidget):
    def __init__(self, force_plate_calibration_page, data_directory, parent=None):
        super(Data_Analysis_Page, self).__init__(parent)
        self.force_plate_calibration_page = force_plate_calibration_page
        self.csv_data_directory = data_directory
        self.video_data_directory =  self.csv_data_directory.replace("FP output", "video output")
        self.video_data_directory =  self.video_data_directory.replace(".csv", ".mp4")
        print(self.csv_data_directory)
        print(self.video_data_directory)
        df = pd.read_csv(self.csv_data_directory)

        self.Force_Plate_1 = df['Force plate 1'].tolist()
        self.Force_Plate_2 = df['Force plate 2'].tolist()
        self.max_Forces = []
        self.max_Forces.append(max(self.Force_Plate_1))
        self.max_Forces.append(max(self.Force_Plate_2))
        
        self.Time = df['Time'].tolist()
        self.Time_Take_to_Max = []
        self.Time_Take_to_Max.append(self.Time[self.Force_Plate_1.index(max(self.Force_Plate_1))])
        self.Time_Take_to_Max.append(self.Time[self.Force_Plate_2.index(max(self.Force_Plate_2))])

                #for both video and forceplates ouput
     

        self.x1 = np.array([1])
        self.x2 = np.array([2])    

        self.setup_ui()
        self.setup_top_right_button()

    def setup_ui(self):
        self.mainbox = QGridLayout(self)
        self.mainbox.setAlignment(Qt.AlignCenter)
        
        #Setting Up 1st Bar graph
        bargraph_widget = QWidget()
        bargraph_layout = QHBoxLayout(bargraph_widget)
        self.canvas = pg.GraphicsLayoutWidget()
        bargraph_layout.addWidget(self.canvas)

        self.Bar_Plot_1 = self.canvas.addPlot(title='Max Force')
        bargraph1 = pg.BarGraphItem(x=self.x1, height=self.max_Forces[0], width=0.2, brush='g', name='FP1')
        bargraph2 = pg.BarGraphItem(x=self.x2, height=self.max_Forces[1], width=0.2, brush='y', name='FP2')
        self.Bar_Plot_1.addItem(bargraph1)
        self.Bar_Plot_1.addItem(bargraph2)

        # Add text labels to the middle of the bars
        label1 = pg.TextItem(text=str(self.max_Forces[0]), color=(0, 0, 0))
        label1.setPos(0.925, self.max_Forces[0] / 2)
        self.Bar_Plot_1.addItem(label1)

        label2 = pg.TextItem(text=str(self.max_Forces[1]), color=(0, 0, 0))
        label2.setPos(1.925, self.max_Forces[1] / 2)
        self.Bar_Plot_1.addItem(label2)

        self.Bar_Plot_1.getAxis('bottom').setTicks([[(1, 'FP1'), (2, 'FP2')]])
        legend = pg.LegendItem(offset=(70, 30))
        legend.addItem(bargraph1, 'FP1')
        legend.addItem(bargraph2, 'FP2')
        self.canvas.addItem(legend)

        #Setting up 2nd Bar Graph
        self.canvas2 = pg.GraphicsLayoutWidget()
        bargraph_layout.addWidget(self.canvas2)

        self.Bar_Plot_2 = self.canvas2.addPlot(title='Time Taken to Max Force')
        bargraph3 = pg.BarGraphItem(x=self.x1, height=self.Time_Take_to_Max[0], width=0.2, brush='g', name='FP1')
        bargraph4 = pg.BarGraphItem(x=self.x2, height=self.Time_Take_to_Max[1], width=0.2, brush='y', name='FP2')
        self.Bar_Plot_2.addItem(bargraph3)
        self.Bar_Plot_2.addItem(bargraph4)

        # Add text labels to the middle of the bars
        label3 = pg.TextItem(text=f'{self.Time_Take_to_Max[0]:.2f}s', color=(0, 0, 0))
        label3.setPos(0.925, self.Time_Take_to_Max[0] / 2)
        self.Bar_Plot_2.addItem(label3)

        label4 = pg.TextItem(text=f'{self.Time_Take_to_Max[1]:.2f}s', color=(0, 0, 0))
        label4.setPos(1.925, self.Time_Take_to_Max[1] / 2)
        self.Bar_Plot_2.addItem(label4)

#========================things related to video output=========================================================================
        #create videowidget object
        self.cap = cv2.VideoCapture(self.video_data_directory)  # Path to your MP4 file

        self.video_duration_seconds = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        self.recording_length = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        print(self.video_duration_seconds, self.recording_length)
        self.recording_framecount = 0
        print("video duration and number of frames")
        print(self.video_duration_seconds, self.recording_length)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)

        
        #create media player object
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(800, 400)
        self.mainbox.addWidget(self.video_label, 1, 1, 1, 1)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.set_position)  # Connect slider movement to set_position method, so that when u shift slider manually, it updates the data
        self.mainbox.addWidget(self.slider, 2, 1, 1, 2)

        self.setLayout(self.mainbox)
#============================================================================================================================

        self.current_frame_versus_total_frames_label = QLabel(f"NA frame: {self.recording_length} total frames", self)
        self.mainbox.addWidget(self.current_frame_versus_total_frames_label, 3, 0)

        # Add the bar graphs widget to the main layout
        self.mainbox.addWidget(bargraph_widget, 0,0, 1, 2)

        self.Bar_Plot_2.getAxis('bottom').setTicks([[(1, 'FP1'), (2, 'FP2')]])
        legend2 = pg.LegendItem(offset=(70, 30))         
        legend2.addItem(bargraph3, 'FP1')
        legend2.addItem(bargraph4, 'FP2')
        self.canvas2.addItem(legend2)

        # Add the horizontal bar graph layout to the main grid layout
        self.mainbox.addLayout(bargraph_layout, 2,0, 1, 2)   
#===============================line graph plotting============================================================
        # Create and insert Graphics Layout to layout
        self.canvas = pg.GraphicsLayoutWidget()   
        self.mainbox.layout().addWidget(self.canvas, 1, 0, 1, 1) 

        # Set up plots
        self.analogPlot1 = self.canvas.addPlot(title='Force Plate 1', row = 0, col = 0)
        self.analogPlot1.enableAutoRange(enable = True)
        self.analogPlot1.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase

        self.analogPlot2 = self.canvas.addPlot(title='Force Plate 2', row = 1, col = 0)
        self.analogPlot2.enableAutoRange(enable = True)
        self.analogPlot2.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase

        # Initialize sensor data variables
        self.drawplot1 = self.analogPlot1.plot(pen='y')
        self.drawplot2 = self.analogPlot2.plot(pen='g')
#============================================================================================================================
    def set_position(self, position):
        self.recording_framecount = int((position / 100) * self.recording_length)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.recording_framecount)
        self._update()

    def _update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_qt_format)
            self.video_label.setPixmap(pixmap.scaled(self.video_label.size()))

#===============================line graph live update===============================#===============================#===============================
        self.drawplot1.setData(self.Time[0:self.recording_framecount], self.Force_Plate_1[0:self.recording_framecount])
        self.drawplot2.setData(self.Time[0:self.recording_framecount], self.Force_Plate_2[0:self.recording_framecount])
        self.current_frame_versus_total_frames_label.setText("{} frame: {} total frames".format(str(self.recording_framecount), str(self.recording_length)))
        print(self.recording_framecount, self.Force_Plate_1[self.recording_framecount])
        if self.recording_framecount != self.recording_length - 1:
            self.recording_framecount += 1
        else:
            self.timer.stop()

        if self.recording_length > 0:
            self.slider.setValue(int((int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) / self.recording_length) * 100))

#===============================#===============================#===============================#===============================#===============================
    def setup_top_right_button(self):
        
        # Create a button and set its text and size
        back_button = QPushButton("Back", self)
        back_button.setFixedSize(150, 50)
        back_button.clicked.connect(self.back_button_clicked)

        # Add the button to a widget to manage its position
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.addWidget(back_button, alignment=Qt.AlignRight)

        self.play_button = QPushButton('Play')
        self.play_button.setFixedSize(150, 50)
        self.play_button.clicked.connect(self.play_video)
        button_layout.addWidget(self.play_button, alignment=Qt.AlignRight)

        self.pause_button = QPushButton('Pause')
        self.pause_button.setFixedSize(150, 50)
        self.pause_button.clicked.connect(self.pause_video)
        button_layout.addWidget(self.pause_button, alignment=Qt.AlignRight)

        # Add the button widget to the main layout
        self.mainbox.addWidget(button_widget)

    def play_video(self):
        self.timer.start(30)

    def pause_video(self):
        self.timer.stop()

    def back_button_clicked(self):
        self.force_plate_calibration_page.show_Analysis_Profile_Selection_Page()


class Training_Page(QWidget):
    def __init__(self, force_plate_calibration_page):
        super().__init__()
        self.force_plate_calibration_page = force_plate_calibration_page
        layout = QVBoxLayout()

        self.base_directory = athletes_file_path  # Specify the base directory for profiles

        self.profile_label = QLabel("Selected Profile: ", self)
        self.profile_label.move(50,50)

        self.profile_combobox = QComboBox(self)
        self.profile_combobox.setGeometry(50, 50, 100, 25)
        self.profile_combobox.move(150, 50)
        self.profile_combobox.setEditable(True)
        self.profile_combobox.addItem("Create")
        self.profile_combobox.currentTextChanged.connect(self.profile_changed)

        self.directory_label = QLabel("Directory:", self)
        self.directory_label.move(50, 100)

        self.directory_textbox = QLineEdit(self)
        self.directory_textbox.move(150, 100)
        self.directory_textbox.setReadOnly(True)

        self.training_label = QLabel("Training Type:", self)
        self.training_label.move(50, 150)
        self.training_dropdown = QComboBox(self)
        self.training_dropdown.setGeometry(50, 50, 100, 25)
        self.training_dropdown.move(150, 150)
        self.training_dropdown.addItem("Backstroke Start")
        self.training_dropdown.addItem("Single Lap")
        self.training_dropdown.addItem("Multiple Laps")
        self.training_dropdown.addItem("Relay")            

        self.next_button = QPushButton("Next", self)
        self.next_button.move(150, 200)
        self.next_button.clicked.connect(self.go_to_Graph_page)

        self.back_button =QPushButton("back", self)
        self.back_button.move(300, 200)
        self.back_button.clicked.connect(self.back_to_mainmenu)
        layout.addWidget(self.back_button)

        self.load_existing_profiles()

    def load_existing_profiles(self):
        existing_profiles = [f for f in os.listdir(self.base_directory) if os.path.isdir(os.path.join(self.base_directory, f))]
        self.profile_combobox.clear()
        self.profile_combobox.addItem("Select Profile")
        self.profile_combobox.addItems(existing_profiles)
        self.profile_combobox.addItem("Create")


    def profile_changed(self, text):
        if text == "Create":
            self.directory_textbox.clear()
            self.directory_textbox.setReadOnly(False)
            self.next_button.setText("Create Profile")
            self.next_button.clicked.disconnect()  # Disconnect previous signal-slot connection
            self.next_button.clicked.connect(self.create_profile)
        else:
            profile_directory = os.path.join(self.base_directory, text)
            self.directory_textbox.setText(profile_directory)
            self.directory_textbox.setReadOnly(True)
            self.next_button.setText("Next")
            self.next_button.clicked.disconnect()  # Disconnect previous signal-slot connection
            self.next_button.clicked.connect(self.save_data)
    
    def create_profile(self):
        folder_name, ok_pressed = QInputDialog.getText(self, "Create New Profile", "Enter the profile name:")
        if ok_pressed and folder_name:
            new_profile_directory = os.path.join(self.base_directory, folder_name)
            if os.path.exists(new_profile_directory):
                QMessageBox.warning(self, "Warning", "Profile already exists. Please enter a different profile name.")
                self.profile_combobox.setCurrentIndex(0)
            else:
                os.makedirs(new_profile_directory)
                self.profile_combobox.addItem(folder_name)
                self.profile_combobox.setCurrentText(folder_name)
                self.directory_textbox.setText(new_profile_directory)

    def save_data(self):
        profile_name = self.profile_combobox.currentText()
        training_type = self.training_dropdown.currentText()
        current_date = date.today()
        str_current_date = current_date.strftime("%Y-%m-%d")
        directory = self.directory_textbox.text()
        self.saved_csv_file_name = str_current_date + " FP output " + profile_name
        self.saved_video_file_name = str_current_date + " Video output " + profile_name
        self.final_directory = os.path.join(directory,training_type,str_current_date)

        if not os.path.exists(self.final_directory):
            os.makedirs(self.final_directory)
        
        if profile_name == "Create":
            # Handle profile creation
            if directory == "":
                QMessageBox.warning(self, "Warning", "Please enter a profile name.")
                return

            new_profile_directory = os.path.join(self.base_directory, directory)
            if os.path.exists(new_profile_directory):
                QMessageBox.warning(self, "Warning", "Profile already exists. Please enter a different profile name.")
                return

            os.makedirs(new_profile_directory)
            print("New profile created:", directory)
            self.profile_combobox.addItem(directory)
            self.profile_combobox.setCurrentText(directory)
        else:
            # Handle existing profile
            print("Data saved with profile:", profile_name)
            print("Directory:", directory)
            print("Saved File Name:", self.saved_csv_file_name)

            while True:
                # Check if the file already exists
                file_path = os.path.join(directory, self.saved_csv_file_name + '.csv')
                if os.path.exists(file_path):
                    # Prompt the user for a different filename
                    new_file_name, ok = QInputDialog.getText(self, "File Already Exists", "A file with the same name already exists. Please enter a different file name:")
                    if ok:
                        # Update the saved_csv_file_name with the new input
                        self.saved_csv_file_name = new_file_name.strip()
                    else:
                        # User canceled, return without saving
                        return
                else:
                    break
            # Save the data in the CSV File

            print("Data saved with profile:", profile_name)
            print("Directory:", self.final_directory)
            print("Saved File Name:", self.saved_csv_file_name)

            self.go_to_Graph_page()

    def go_to_Graph_page(self):
        graph_page = Graph_Page(self.force_plate_calibration_page, self.final_directory, self.saved_csv_file_name, self.saved_video_file_name)
        final_directory = self.final_directory
        saved_csv_file_name = self.saved_csv_file_name
        saved_video_data_directory =  saved_csv_file_name.replace("FP output", "video output")
        saved_video_data_directory =  saved_video_data_directory.replace(".csv", ".mp4")
        self.force_plate_calibration_page.show_Graph_page(final_directory, saved_csv_file_name, saved_video_data_directory)


    def back_to_mainmenu(self):
        self.force_plate_calibration_page.show_Main_Menu_Page()
class Graph_Page(QWidget):
    def __init__(self, force_plate_calibration_page, final_directory, saved_csv_file_name, saved_video_file_name, parent=None):
        super(Graph_Page, self).__init__(parent)
        self.force_plate_calibration_page = force_plate_calibration_page
        # layout = QVBoxLayout()
        self.mainbox = QGridLayout(self)
        # self.label = QLabel("This is Page 2")
        # layout.addWidget(self.label)
        # self.setLayout(layout)

        self.canvas = pg.GraphicsLayoutWidget()   # Create Graphics Layout
        self.mainbox.layout().addWidget(self.canvas, 0,0, 2, 2)
        
        self.label = QLabel()               # Placeholder QLabel
        self.mainbox.layout().addWidget(self.label, 2, 0, 1, 4)

        # Add start, back, stop and upload to drive buttons
        self.startButton = QPushButton('Start')
        self.startButton.clicked.connect(self.start)
        self.mainbox.layout().addWidget(self.startButton, 3, 0, 1, 4)

        self.stopButton = QPushButton('Stop')
        self.stopButton.clicked.connect(self.stop)
        self.mainbox.layout().addWidget(self.stopButton, 4, 0, 1, 4)

        self.upload_to_Gdrive_button = QPushButton('upload to Gdrive')
        self.upload_to_Gdrive_button.clicked.connect(upload_to_Gdrive_button_fn)
        self.mainbox.layout().addWidget(self.upload_to_Gdrive_button, 5, 0, 1, 4)

        self.backButton = QPushButton('Back')
        self.backButton.clicked.connect(self.back)
        self.mainbox.layout().addWidget(self.backButton, 6, 0, 1, 4)


        # Set up plots
        self.analogPlot1 = self.canvas.addPlot(title='Force Plate 1', row = 0, col = 0)
        self.analogPlot1.setYRange(-0.5, 600)
        self.analogPlot1.setXRange(0, 2000)
        self.analogPlot1.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase

        self.analogPlot2 = self.canvas.addPlot(title='Force Plate 2', row = 1, col = 0)
        self.analogPlot2.setYRange(-0.5, 600)
        self.analogPlot2.setXRange(0, 2000)
        self.analogPlot2.showGrid(x=True, y=True, alpha=0.5)  # 'X' should be lowercase

        #for video ouput
        self.video_recorded_frames =[]

        #for both video and forceplates ouput
        self.recording_length = 0
        self.recording_framecount = 0
    
        #widgets
            #Data output
                #video output
        self.video_output = VideoStreamWidget()
        self.video_output.setFixedSize(800, 500)
        self.mainbox.addWidget(self.video_output, 0, 2, 2, 2)
        
        # Initialize sensor data variables
        self.numPoints = 2000
        self.fps = 0.0
        self.lastupdate = time.time()
        self.x = np.arange(self.numPoints)
        self.y1 = np.zeros(self.numPoints)
        self.y2 = np.zeros(self.numPoints)
        self.drawplot1 = self.analogPlot1.plot(pen='y')
        self.drawplot2 = self.analogPlot2.plot(pen='g')

        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.isGenerating = False

        self.csvFile = None
        self.csvWriter = None
        self.headingWritten = False      

        self.directory = final_directory
        self.saved_csv_file_name = saved_csv_file_name  
        self.saved_video_file_name = saved_video_file_name

        #Audio File Path
        self.audio_file = r"C:\Users\wongt\OneDrive - Nanyang Technological University\Academics\NTU\Y4S1\FYP\swimming-force-plate-prototype\Start.mp3"

    def start(self):
        if not self.isGenerating:
            self.video_output.read_cap()
            self.video_output.toggle_play()
            self.timer.start(interval_ms)  # Start timer with a interval_ms interval
            self.video_starttime = datetime.now()
            self.isGenerating = True
            # Open CSV file for writing if heading is not written
            print("File Name :" + self.saved_csv_file_name)
        
            if not self.headingWritten:
                print(self.saved_csv_file_name)
                file_path = os.path.join(self.directory, (self.saved_csv_file_name + ".csv"))
                self.csvFile = open(file_path, 'w', newline='')
                print('csv file opened')
                self.csvWriter = csv.writer(self.csvFile)
                self.csvWriter.writerow(['Time','Serial Number','Force plate 1','Force plate 2',
               'Tri1-X','Tri1-Y','Tri1-Z',
               'Tri2-X','Tri2-Y','Tri2-Z','COT'])
                self.headingWritten = True

            #Play the audio file
            ##audio_thread = Thread(target=playsound, args=(self.audio_file,))
            #audio_thread.start()

            
    def stop(self):
        if self.isGenerating:
            self.timer.stop()
            self.video_output.toggle_stop_cap()
            self.isGenerating = False
            output_file = os.path.join(self.directory, (self.saved_video_file_name + ".mp4"))
            self.video_endtime = datetime.now()
            duration_seconds_of_recording = (self.video_endtime - self.video_starttime).total_seconds()
            fps = int(round(len(self.video_recorded_frames)/duration_seconds_of_recording))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_file, fourcc, fps, (800, 500))

            for single_frame in self.video_recorded_frames:
                out.write(single_frame)

            out.release()
            # Close CSV file
            if self.csvFile is not None:
                self.csvFile.close()

    def back(self):
        self.force_plate_calibration_page.show_Training_page()

    def _update(self):
        global data1, data2
        global iteration
        hex_list = []
        if dummy_FP_data == False:
            self.ser = serial.Serial('/dev/ttyUSB0', 115200, 8, 'N', 2, timeout=1) #open serial port
            output = self.ser.read_until(b'\r\n')
            output_hex = output.hex()
            iteration += 1
            if (len(output_hex)) == 42: #only collects data if it have 42 char, fixes signal correction problem
                
                time = iteration * time_interval #Calculate the time using the serial number
                time_string = "{:06.3f}".format(time)
                
                hex_list.extend([output_hex[6:10], output_hex[10:14], #[Iteration, F1, F2]
                output_hex[14:18], output_hex[18:22], output_hex[22:26], #[X1, Y1, Z1]
                output_hex[26:30], output_hex[30:34], output_hex[34:38]]) #[X2, Y2, Z2]
                    
                integer_list = []
                integer_list = map(twos_complement_16bits, hex_list) #convert all hex elements into int 
                integer_list = list(integer_list) #convert map type to list type
                iteration += 1

                integer_list.insert(0,iteration)
                integer_list.insert(0, time_string)

                
                d = open(self.directory + "/" + self.saved_csv_file_name,"a")
                writer = csv.writer(d)
                writer.writerow(integer_list)
                d.close()
                
            else:
                print(f"missing at {iteration}" )
                print(output_hex)
                print(f"len: {len(output_hex)}")
                pass

        else:   #dummy data
            integer_list = [10, 2] ##remove and unremove the above line
            iteration += 1
            time = iteration * time_interval #Calculate the time using the serial number
            time_string = "{:06.3f}".format(time)
            integer_list.insert(0,iteration)
            integer_list.insert(0, time_string)


            
        FP1, FP2 = integer_list[2], integer_list[3]
        FP1 = round(FP1 - F1_resting_value)
        FP2 = round(FP2 - F2_resting_value)

        if self.csvWriter is not None:
            self.video_recorded_frames.append(frame)
            self.csvWriter.writerow(integer_list)

        if len(data1) < self.numPoints: 
            data1 = np.append(data1, FP1)
        else:
            data1[:-1] = data1[1:]
            data1[-1] = FP1

        if len(data2) < self.numPoints:
            data2 = np.append(data2, FP2)
        else:
            data2[:-1] = data2[1:]
            data2[-1] = FP2

        xAxis = np.arange(0, len(data1))
        yAxis1 = data1
        yAxis2 = data2

        self.x = np.arange(len(data1))  # Update x-axis data
        self.y1 = yAxis1  # Update y-axis data for plot 1
        self.y2 = yAxis2  # Update y-axis data for plot 2

        self.drawplot1.setData(self.x, self.y1)
        self.drawplot2.setData(self.x, self.y2)

        self._framerate()

    def _framerate(self):
        now = time.time()
        dt = now - self.lastupdate
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = f'Mean Frame Rate: {self.fps:.3f} FPS'
        self.label.setText(tx)

#==============================Functions for Gdrive=============================================    
#This is to upload entire files onto google drive
def upload_file(service, local_file_path, parent_folder_id=None):
    """
    Uploads a file to Google Drive.
    """
    file_metadata = {'name': os.path.basename(local_file_path)}
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    media = MediaFileUpload(local_file_path)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

def upload_directory(service, local_directory_path, parent_folder_id=None):
    """
    Recursively uploads all files in a directory to Google Drive.
    """
    for item in os.listdir(local_directory_path):
        item_path = os.path.join(local_directory_path, item)
        if os.path.isfile(item_path):
            upload_file(service, item_path, parent_folder_id)
        elif os.path.isdir(item_path):
            folder_metadata = {
                'name': item,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            upload_directory(service, item_path, folder.get('id'))

def upload_to_Gdrive_button_fn(self):
    # # Specify the local directory to upload
    local_directory_path = "./Athlete's Profile"

    # Specify the parent folder ID in Google Drive (optional)
    parent_folder_id = '1edIKtXY9GDcA_4MTij1bZ4kVn9LCs2ny'
    # Upload files recursively from the local directory to Google Drive
    upload_directory(service, local_directory_path, parent_folder_id)

#========================================================================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1600, 800)
        # Create the stacked widget and add pages
        self.stacked_widget = QStackedWidget()
        self.force_plate_calibration_page = Force_plate_calibration_page(self)
        
        self.stacked_widget.addWidget(self.force_plate_calibration_page)       
        

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
    
        self.setCentralWidget(central_widget)

    def show_Force_plate_calibration_page(self):
        self.force_plate_calibration_page = Force_plate_calibration_page(self)
        self.stacked_widget.addWidget(self.force_plate_calibration_page)
        self.stacked_widget.setCurrentWidget(self.force_plate_calibration_page)
    
    def show_Calibration_page_for_sync_between_force_plates_and_camera_1(self):
        self.calibration_page_for_sync_between_force_plates_and_camera_1 = Calibration_page_for_sync_between_force_plates_and_camera_1(self)
        self.stacked_widget.addWidget(self.calibration_page_for_sync_between_force_plates_and_camera_1)
        self.stacked_widget.setCurrentWidget(self.calibration_page_for_sync_between_force_plates_and_camera_1)

    def show_Calibration_page_for_sync_between_force_plates_and_camera_2(self):
        self.calibration_page_for_sync_between_force_plates_and_camera_2 = Calibration_page_for_sync_between_force_plates_and_camera_2(self)
        self.stacked_widget.addWidget(self.calibration_page_for_sync_between_force_plates_and_camera_2)
        self.stacked_widget.setCurrentWidget(self.calibration_page_for_sync_between_force_plates_and_camera_2)
    
    def show_Main_Menu_Page(self):
        self.main_menu = MainMenu(self)
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def show_Analysis_Selection_Page(self):
        self.analysis_selection_page = Analysis_Selection_Page(self)
        self.stacked_widget.addWidget(self.analysis_selection_page)
        self.stacked_widget.setCurrentWidget(self.analysis_selection_page)

    def show_Comparison_Analysis_Selection_Page(self):
        self.comparison_analysis_selection_page = Comparison_Analysis_Selection_Page(self, self)
        self.stacked_widget.addWidget(self.comparison_analysis_selection_page)
        self.stacked_widget.setCurrentWidget(self.comparison_analysis_selection_page)


    def show_Analysis_Profile_Selection_Page(self):
        self.analysis_profile_selection_page = Analysis_Profile_Selection_Page(self)
        self.stacked_widget.addWidget(self.analysis_profile_selection_page)
        self.stacked_widget.setCurrentWidget(self.analysis_profile_selection_page)

    def show_Data_Analysis_Page(self, data_directory):
        self.csv_data_directory = data_directory
        self.data_analysis_page = Data_Analysis_Page(self, self.csv_data_directory)
        self.stacked_widget.addWidget(self.data_analysis_page)
        self.stacked_widget.setCurrentWidget(self.data_analysis_page)

    def show_Comparison_Analysis_Page(self, file_directory_list, file_name_list):
        self.file_directory_list = file_directory_list
        self.file_name_list = file_name_list
        self.comparison_analysis_page = Comparison_Analysis_Page(self, self.file_directory_list, self.file_name_list)
        self.stacked_widget.addWidget(self.comparison_analysis_page)
        self.stacked_widget.setCurrentWidget(self.comparison_analysis_page)

    def show_Training_page(self):
        self.training_page = Training_Page(self)  # Changed variable name here to "training_page"
        self.stacked_widget.addWidget(self.training_page)  # Updated variable name here
        self.stacked_widget.setCurrentWidget(self.training_page)  # Updated variable name here

    def show_Graph_page(self, final_directory, saved_csv_file_name, saved_video_file_name):
        self.final_directory = final_directory
        self.saved_csv_file_name = saved_csv_file_name
        self.graph_page = Graph_Page(self, final_directory, saved_csv_file_name, saved_video_file_name)
        self.stacked_widget.addWidget(self.graph_page)
        self.stacked_widget.setCurrentWidget(self.graph_page)  # Updated variable name here


if __name__ == "__main__":
    print("application started")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
