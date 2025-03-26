import sys
import random
import math
import csv
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QGroupBox, QPushButton, QFileDialog)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import smtplib
from email.mime.text import MIMEText
import pandas as pd
from  Arrythmia_Detector import ArrythmiaDetector

class PatientMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iMonitor")
        self.setGeometry(100, 100, 1920, 1080)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title header
        title_label = QLabel("iMonitor")
        title_label.setFont(QFont("Arial", 28))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("background-color: #3c3c3c; color: white; padding: 15px;")
        main_layout.addWidget(title_label)

        # Content layout (ECG + right panel)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)
        main_layout.addLayout(content_layout, stretch=1)

        # ECG display
        self.ecg_widget = pg.PlotWidget()
        self.ecg_widget.setMinimumSize(800, 400)
        self.ecg_widget.setBackground('k')
        self.ecg_plot = self.ecg_widget.plot(pen='g')
        self.ecg_widget.setXRange(0, 10)  # Initial range, will adjust dynamically
        self.ecg_widget.setYRange(-2, 2)
        self.ecg_widget.setLabel('bottom', 'Time', 's')
        self.ecg_widget.setLabel('left', 'ECG', 'mV')
        self.ecg_widget.showGrid(x=True, y=True, alpha=0.3)
        content_layout.addWidget(self.ecg_widget, stretch=4)

        # Right panel
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        self.right_layout.setSpacing(40)
        content_layout.addWidget(right_panel, stretch=1)

        # Vital signs
        for vital, value in [("Blood Pressure", "BP: --/-- mmHg"), ("SpO2", "SpO2: --%"), ("Temperature", "Temp: --°C")]:
            group = QGroupBox(vital)
            layout = QVBoxLayout()
            label = QLabel(value)
            self.__setattr__(f"{vital.lower().replace(' ', '_')}_label", label)
            label.setFont(QFont("Arial", 24, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedHeight(60)
            label.setStyleSheet("background-color: gray; color: white; padding: 15px;")
            layout.addWidget(label)
            group.setLayout(layout)
            group.setStyleSheet("QGroupBox { font-size: 20px; color: white; border: 1px solid #555555; margin-top: 25px; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }")
            self.right_layout.addWidget(group)

        # Alarms section
        self.alarms = {'Tachycardia': False, 'Flutter': False, 'Couplets': False}
        self.alarm_labels = {}
        alarms_group = QGroupBox("Alarms")
        self.alarm_layout = QHBoxLayout()
        self.alarm_layout.setSpacing(20)
        for alarm in self.alarms:
            label = QLabel(alarm)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(150, 60)
            label.setFont(QFont("Arial", 16))
            label.setStyleSheet("background-color: green; color: white; border-radius: 5px; padding: 5px;")
            self.alarm_labels[alarm] = label
            self.alarm_layout.addWidget(label)
        alarms_group.setLayout(self.alarm_layout)
        alarms_group.setStyleSheet("QGroupBox { font-size: 20px; color: white; border: 1px solid #555555; margin-top: 25px; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }")
        self.right_layout.addWidget(alarms_group)

        # Browse signal button
        self.browse_btn = QPushButton("Browse Signal")
        self.browse_btn.setStyleSheet("background-color: #3c3c3c; color: white; padding: 8px; font-size: 20px;")
        self.browse_btn.setIcon(QIcon("icons/browse_icon.png"))
        self.browse_btn.setIconSize(QSize(32, 32))
        self.browse_btn.setToolTip("Browse Signal")
        self.browse_btn.clicked.connect(self.browse_signal)
        self.right_layout.addWidget(self.browse_btn)

        # Signal control buttons
        control_group = QGroupBox("Signal Controls")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)

        self.increase_speed_btn = QPushButton("Speed Up")
        self.increase_speed_btn.setIcon(QIcon("icons/increase_speed_icon.png"))
        self.increase_speed_btn.setIconSize(QSize(32, 32))
        self.increase_speed_btn.setToolTip("Increase Speed")

        self.decrease_speed_btn = QPushButton("Slow Down")
        self.decrease_speed_btn.setIcon(QIcon("icons/decrease_speed_icon.png"))
        self.decrease_speed_btn.setIconSize(QSize(32, 32))
        self.decrease_speed_btn.setToolTip("Decrease Speed")

        self.pause_play_btn = QPushButton("Pause")
        self.pause_play_btn.setIcon(QIcon("icons/pause_icon.png"))
        self.pause_play_btn.setIconSize(QSize(32, 32))
        self.pause_play_btn.setToolTip("Pause")

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setIcon(QIcon("icons/reset_icon.png"))
        self.reset_btn.setIconSize(QSize(32, 32))
        self.reset_btn.setToolTip("Reset")

        for btn in [self.increase_speed_btn, self.decrease_speed_btn, self.pause_play_btn, self.reset_btn]:
            btn.setStyleSheet("background-color: #3c3c3c; color: white; padding: 8px; font-size: 16px;")
            btn.setFixedHeight(50)
            control_layout.addWidget(btn)

        control_group.setLayout(control_layout)
        control_group.setStyleSheet("QGroupBox { font-size: 20px; color: white; border: 1px solid #555555; margin-top: 25px; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }")
        self.right_layout.addWidget(control_group)
        self.right_layout.addStretch()

        # Signal control variables
        self.base_update_interval = 50
        self.speed_factor = 1.0
        self.is_playing = True
        self.max_window_size = 1000  # Maximum number of points to display

        # Signal data
        self.x = []  # Full time data
        self.full_signal = []  # Full ECG signal
        self.x_display = []  # Rolling time window (starts empty)
        self.display_signal = []  # Rolling signal window (starts empty)
        self.current_index = 0

        # Connect buttons
        self.increase_speed_btn.clicked.connect(self.increase_speed)
        self.decrease_speed_btn.clicked.connect(self.decrease_speed)
        self.pause_play_btn.clicked.connect(self.toggle_pause_play)
        self.reset_btn.clicked.connect(self.reset_signal)

        # Timers
        self.ecg_timer = QTimer()
        self.ecg_timer.timeout.connect(self.update_ecg)

        self.vitals_timer = QTimer()
        self.vitals_timer.timeout.connect(self.update_vitals)

        self.blink_state = 0
        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.update_alarms)

        # Start timers
        self.ecg_timer.start(int(self.base_update_interval * self.speed_factor))
        self.vitals_timer.start(5000)

        # Initialize the arrythmia detector class
        self.detector = ArrythmiaDetector()

        # Adjust alarm timer to 1 second (1000 ms)
        self.alarm_timer.start(1000)  # Start with 1-second interval
        
        # Initial updates
        self.update_vitals()

    def browse_signal(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select ECG Signal File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                df = pd.read_csv(file_name, header=None)
                self.x = df.iloc[:, 0].dropna().astype(float).tolist()
                self.full_signal = df.iloc[:, 1].dropna().astype(float).tolist()

                # Reset display data
                self.current_index = 0
                self.x_display = []
                self.display_signal = []

            except Exception as e:
                print(f"Error loading signal: {e}")

    def set_initial_signal(self, file_name):
        if file_name:
            try:
                df = pd.read_csv(file_name, header=None)
                self.x = df.iloc[:, 0].dropna().astype(float).tolist()
                self.full_signal = df.iloc[:, 1].dropna().astype(float).tolist()

                # Reset display data
                self.current_index = 0
                self.x_display = []
                self.display_signal = []
            except Exception as e:
                print(f"Error loading signal: {e}")

    def increase_speed(self):
        self.speed_factor *= 0.5
        if self.speed_factor < 0.1:
            self.speed_factor = 0.1
        if self.is_playing:
            self.ecg_timer.start(int(self.base_update_interval * self.speed_factor))

    def decrease_speed(self):
        self.speed_factor *= 2.0
        if self.speed_factor > 10.0:
            self.speed_factor = 10.0
        if self.is_playing:
            self.ecg_timer.start(int(self.base_update_interval * self.speed_factor))

    def toggle_pause_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.ecg_timer.start(int(self.base_update_interval * self.speed_factor))
            self.pause_play_btn.setIcon(QIcon("icons/pause_icon.png"))
            self.pause_play_btn.setText("Pause")
            self.pause_play_btn.setToolTip("Pause")
        else:
            self.ecg_timer.stop()
            self.pause_play_btn.setIcon(QIcon("icons/play_icon.png"))
            self.pause_play_btn.setText("Play")
            self.pause_play_btn.setToolTip("Play")

    def reset_signal(self):
        self.current_index = 0
        self.x_display = []
        self.display_signal = []
        self.ecg_plot.setData(self.x_display, self.display_signal)

    def update_ecg(self):
        if not self.is_playing or not self.full_signal:
            return

        # Add the next point to the display
        self.x_display.append(self.x[self.current_index])
        self.display_signal.append(self.full_signal[self.current_index])

        # If the window exceeds max_window_size, start shifting
        if len(self.x_display) > self.max_window_size:
            self.x_display.pop(0)
            self.display_signal.pop(0)

        # Update the x-axis range dynamically
        if self.x_display:
            min_x = min(self.x_display)
            max_x = max(self.x_display)
            self.ecg_widget.setXRange(min_x, max_x)

        # Update the plot
        self.ecg_plot.setData(self.x_display, self.display_signal)
        self.ecg_widget.autoRange()

        # Increment index
        self.current_index = (self.current_index + 1) % len(self.full_signal)

    def update_vitals(self):
        bp_sys = random.randint(80, 140)
        bp_dia = random.randint(50, 90)
        bp_color = 'green' if (100 <= bp_sys <= 130 and 70 <= bp_dia <= 85) else 'yellow' if (90 <= bp_sys <= 140 and 60 <= bp_dia <= 90) else 'red'
        bp_text_color = 'black' if bp_color == 'yellow' else 'white'
        self.blood_pressure_label.setText(f"BP: {bp_sys}/{bp_dia} mmHg")
        self.blood_pressure_label.setStyleSheet(f"background-color: {bp_color}; color: {bp_text_color}; padding: 15px;")

        spo2 = random.randint(85, 100)
        spo2_color = 'green' if spo2 >= 95 else 'yellow' if spo2 >= 90 else 'red'
        spo2_text_color = 'black' if spo2_color == 'yellow' else 'white'
        self.spo2_label.setText(f"SpO2: {spo2}%")
        self.spo2_label.setStyleSheet(f"background-color: {spo2_color}; color: {spo2_text_color}; padding: 15px;")

        temp = round(random.uniform(35.0, 39.0), 1)
        temp_color = 'green' if 36.1 <= temp <= 37.2 else 'yellow' if 35.5 <= temp <= 38.5 else 'red'
        temp_text_color = 'black' if temp_color == 'yellow' else 'white'
        self.temperature_label.setText(f"Temp: {temp}°C")
        self.temperature_label.setStyleSheet(f"background-color: {temp_color}; color: {temp_text_color}; padding: 15px;")

    def update_alarms(self):
        self.blink_state = 1 - self.blink_state
        
        # Only proceed if we have ECG data
        if not self.full_signal or not self.x:
            for alarm, label in self.alarm_labels.items():
                label.setStyleSheet("background-color: green; color: white; border-radius: 5px; padding: 5px;")
            return

        # Analyze the full signal for arrhythmias
        flutter_detected = self.detector.detect_flutter(self.x, self.full_signal)
        vtach_detected = self.detector.detect_ventricular_tachycardia(self.full_signal)
        couplets_detected = self.detector.detect_couplets(self.x, self.full_signal)

        # Update alarm states based on detection results
        self.alarms['Tachycardia'] = vtach_detected  # Ventricular tachycardia
        self.alarms['Flutter'] = flutter_detected    # Atrial flutter
        self.alarms['Couplets'] = couplets_detected  # Couplets

        # Update alarm labels with blinking effect
        for alarm, label in self.alarm_labels.items():
            if self.alarms[alarm]:
                color = 'red' if self.blink_state == 0 else 'yellow'
                text_color = 'black' if color == 'yellow' else 'white'
                label.setStyleSheet(f"background-color: {color}; color: {text_color}; font-weight: bold; border-radius: 5px; padding: 5px;")
            else:
                label.setStyleSheet("background-color: green; color: white; border-radius: 5px; padding: 5px;")

    def send_email(message_string, recipient_email):
        """
        Sends an email with consisting of the passed string message 
        """
        sender_email = "emergencypatientmonitor@gmail.com"
        sender_app_password = "wgtu wgui rjzx ytbw"
        
        msg = MIMEText(message_string)
        msg['Subject'] = 'Message from Emergency Patient Monitor'
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        try:
            print("Connecting to smtp.gmail.com:465...")
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                print("Logging in...")
                server.login(sender_email, sender_app_password)
                print("Sending email...")
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply dark theme
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(60, 60, 60))
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(60, 60, 60))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(dark_palette)
    
    monitor = PatientMonitor()
    monitor.set_initial_signal("Data/Ventricular_Flutter_no_header.csv")
    monitor.showMaximized()
    sys.exit(app.exec_())