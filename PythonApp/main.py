"""
==============================================================================

🕒  Time-Keeper Application

------------------------------------------------------------------------------

Author: Soumik Sarkar
GitHub Profile: scarecrow021
Email: soumiksarkar1997@gmail.com
Repository: https://github.com/soumik-sarkar/time-keeper
License: MIT License
Version: 1.3.0
------------------------------------------------------------------------------

DISCLAIMER:
This software is provided "as-is" for personal time logging and authenticity tracking.
The generated PDF logs are designed to reflect the user's real work activity without
manual alteration. Each log entry is recorded verbatim, and the resulting PDF report
is automatically secured to prevent editing.

Tampering with generated files, modifying timestamps, or altering application behavior
to falsify logs violates the intended use of this software.

By using Time-Keeper, you acknowledge that:
- The software does not allow modification or deletion of submitted log messages.
- The application should remain open during the actual work session to ensure authenticity.
- Any log file that appears inconsistent, incomplete, or altered should not be considered valid.

(c) Soumik Sarkar — Time-Keeper Application.
------------------------------------------------------------------------------

Note: 
1) Change Log for version before 1.3.0 is neither available nor necessary.

==============================================================================
"""

import sys
import os
import getpass
import socket
from datetime import datetime, timedelta
import platform
import subprocess
import requests  # for location lookup

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMessageBox

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

from PyPDF2 import PdfReader, PdfWriter

from mainwindow import Ui_MainWindow  # your generated UI file

# --- Constants ---
LOG_DIR = "daily_log"
PASSWORD = "BYEBYE"  # close app password
GITHUB_URL = "https://github.com/scarecrow021/Time-Keeper.git"  # example
APP_VERSION = "1.3.0"
IDEAL_WORK_HOURS = 8
ACTUAL_WORK_HOURS = 10

# --- Utility functions ---
def get_system_info():
    """
    Returns a dict containing system make and model.
    Works on Windows, macOS, and Linux.
    """
    system = platform.system()
    info = {"make": "Unknown", "model": "Unknown"}

    try:
        if system == "Windows":
            # Try using wmic (no external modules needed)
            make = subprocess.check_output(["wmic", "computersystem", "get", "manufacturer"]).decode().split("\n")[1].strip()
            model = subprocess.check_output(["wmic", "computersystem", "get", "model"]).decode().split("\n")[1].strip()
            info["make"] = make or "Unknown"
            info["model"] = model or "Unknown"

        elif system == "Darwin":  # macOS
            make = "Apple"
            model = subprocess.check_output(["sysctl", "-n", "hw.model"]).decode().strip()
            info["make"], info["model"] = make, model

        elif system == "Linux":
            # Most Linux systems expose this info via /sys
            try:
                with open("/sys/devices/virtual/dmi/id/sys_vendor") as f:
                    info["make"] = f.read().strip()
                with open("/sys/devices/virtual/dmi/id/product_name") as f:
                    info["model"] = f.read().strip()
            except Exception:
                pass

    except Exception:
        pass

    return info

def get_location():
    """Return full location info as a dictionary."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        # Ensure all keys exist even if missing
        keys = ["ip", "city", "region", "country", "loc", "postal", "timezone"]
        return {k: data.get(k, "") for k in keys}
    except:
        # Return empty strings if API fails
        return {k: "" for k in ["ip", "city", "region", "country", "loc", "postal", "timezone"]}

def create_pdf_path():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    today_str = datetime.now().strftime("%d_%m_%Y")
    return os.path.join(LOG_DIR, f"{today_str}.pdf")

def format_timedelta(td: timedelta) -> str:
    """Return HH:MM:SS string for a timedelta"""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def build_pdf(pdf_path, log_entries, header_info):
    """
    Build an enhanced PDF with header info and logs, including a copyright page.
    """
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()

    # --- Styles ---
    title_style = ParagraphStyle(
        name="Title",
        fontName="Helvetica-Bold",
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=24
    )

    timestamp_style = ParagraphStyle(
        name="Timestamp",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.darkblue,
        spaceAfter=2
    )

    log_style = ParagraphStyle(
        name="Log",
        fontName="Helvetica",
        fontSize=11,
        leftIndent=12,
        spaceAfter=12
    )

    copyright_style = ParagraphStyle(
        name="Copyright",
        fontName="Helvetica",
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.darkgray,
        spaceAfter=12
    )

    # --- Story ---
    story = []

    # Title with dynamic date
    story.append(Paragraph(f"Time-Keeper : [{header_info['login_date']}]", title_style))

    # Header Info Table
    location_info = header_info["location"]

    data = [
        ["Name:", header_info['user_name']],
        ["PC Hostname:", header_info['pc_name']],
        ["System Make:", header_info.get('system_make', 'Unknown')],
        ["System Model:", header_info.get('system_model', 'Unknown')],
        ["Date:", header_info['login_date']],
        ["Login Time:", header_info['login_time']],
        ["Logout Time:", header_info['logout_time']],
        ["Hours Worked:", header_info.get('hours_worked', '--:--:--')],
    ]

    # Add location info rows
    for key in ["ip", "city", "region", "country", "loc", "postal", "timezone"]:
        data.append([f"{key.capitalize()}:", location_info.get(key, "")])

    table = Table(data, colWidths=[120, 330])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1, -1), 11),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color="#000000", spaceBefore=12, spaceAfter=12))

    # Logs
    for i, (ts, msg) in enumerate(log_entries):
        bg_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        entry_table = Table([
            [Paragraph(ts, timestamp_style)],
            [Paragraph(msg, log_style)]
        ], colWidths=[doc.width])
        entry_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4)
        ]))
        story.append(entry_table)
        story.append(Spacer(1, 6))

    # --- Add Copyright Page ---
    story.append(PageBreak())
    disclaimer_text = (
        f"This file is generated by the Time-Keeper application (c) 2025, Soumik Sarkar, "
        f"available at {GITHUB_URL}, written under MIT license, version {APP_VERSION}.\n\n"
        "This file is a secured PDF; its metadata can be checked for authenticity.\n\n"
        "The content of this PDF reflects verbatim the log messages submitted by the user. "
        "Users are not allowed to modify or erase log messages.\n\n"
        "The application encourages keeping it open throughout the workday to capture authentic logs. "
        "If the file seems tampered with, or the logged times do not reflect the actual work time claimed, "
        "this PDF should not be accepted."
    )
    story.append(Paragraph(disclaimer_text, copyright_style))

    # --- Page Number Footer ---
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(A4[0] - 40, 20, f"Page {page_num}")

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

def make_pdf_non_editable(pdf_path):
    """
    Make PDF non-editable but readable. Overwrites original PDF.
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    # Encrypt with empty passwords to prevent editing
    writer.encrypt(user_password="", owner_password="", use_128bit=True)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return pdf_path

# --- Main Window ---
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- Window title ---
        self.setWindowTitle(f"Time-Keeper : [{datetime.now().strftime('%d/%m/%Y')}]")

        # --- Disable minimize ---
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window |
            QtCore.Qt.WindowType.WindowTitleHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.CustomizeWindowHint
        )

        # --- Timer setup ---
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=IDEAL_WORK_HOURS)
        self.show_colons = True
        self.leave_time = self.start_time + timedelta(hours=ACTUAL_WORK_HOURS)

        # --- Setup LCDs ---
        self.setup_lcd(self.timeStarted, "#B0B0B0")   # grey
        self.setup_lcd(self.timeSpent, "#00FF00")     # green
        self.setup_lcd(self.timeRemaining, "#FFD300") # amber
        self.setup_lcd(self.currentTime, "#00BFFF")   # blue
        self.setup_lcd(self.countdown, "#FF00FF")     # magenta
        self.timeStarted.display(self.start_time.strftime("%H:%M:%S"))

        # --- Leave time setup (HH:MM:SS) ---
        self.leaveTimeEdit.setDisplayFormat("HH:mm:ss")
        self.leaveTimeEdit.setTime(self.leave_time.time())
        self.leaveTimeEdit.timeChanged.connect(self.update_leave_time)

        # --- Timer ---
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_times)
        self.timer.start(1000)
        self.update_times()

        # --- Logging ---
        self.pdf_path = create_pdf_path()
        self.log_entries = []

        # Auto-filled header info
        self.user_name = getpass.getuser()
        self.pc_name = socket.gethostname()
        self.login_time = self.start_time.strftime("%H:%M:%S")
        self.login_date = self.start_time.strftime("%d/%m/%Y")
        self.system_info = get_system_info()
        self.location = get_location()
        self.header_info = {
            "user_name": self.user_name,
            "login_date": self.login_date,
            "login_time": self.login_time,
            "logout_time": "--:--:--",
            "pc_name": self.pc_name,
            "system_make": self.system_info["make"],
            "system_model": self.system_info["model"],
            "location": self.location,
            "hours_worked": "--:--:--"
        }

        build_pdf(self.pdf_path, self.log_entries, self.header_info)

        # --- Submit button ---
        self.submitButton.clicked.connect(self.handle_submit)

    # --- LCD Setup ---
    def setup_lcd(self, lcd, color):
        lcd.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        lcd.setDigitCount(8)
        lcd.setStyleSheet(f"""
            QLCDNumber {{
                background-color: #000000;
                color: {color};
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 4px;
            }}
        """)
        lcd.display("--:--:--")

    # --- Leave Time Edit Changed ---
    def update_leave_time(self, qtime):
        today = datetime.today()
        self.leave_time = datetime.combine(today, qtime.toPyTime())

    # --- Format time with blinking colon ---
    def format_time(self, dt: datetime) -> str:
        text = dt.strftime("%H:%M:%S")
        if not self.show_colons:
            text = text.replace(":", " ")
        return text

    # --- Update LCDs ---
    def update_times(self):
        now = datetime.now()
        self.show_colons = not self.show_colons

        # Current time
        self.currentTime.display(self.format_time(now))

        # Time spent
        elapsed = now - self.start_time
        self.timeSpent.display(format_timedelta(elapsed) if self.show_colons else format_timedelta(elapsed).replace(":", " "))

        # Time remaining
        remaining = self.end_time - now
        if remaining.total_seconds() <= 0:
            self.timeRemaining.display("00:00:00")
            self.timeRemaining.setStyleSheet(self.timeRemaining.styleSheet().replace("#FFD300", "#FF3B30"))
        else:
            self.timeRemaining.display(format_timedelta(remaining) if self.show_colons else format_timedelta(remaining).replace(":", " "))
            if remaining.total_seconds() < 1800:
                self.timeRemaining.setStyleSheet(self.timeRemaining.styleSheet().replace("#FFD300", "#FF3B30"))
            else:
                self.timeRemaining.setStyleSheet(self.timeRemaining.styleSheet().replace("#FF3B30", "#FFD300"))

        # Countdown
        countdown_delta = self.leave_time - now
        if countdown_delta.total_seconds() <= 0:
            self.countdown.display("00:00:00")
        else:
            self.countdown.display(format_timedelta(countdown_delta) if self.show_colons else format_timedelta(countdown_delta).replace(":", " "))

    # --- Submit button ---
    def handle_submit(self):
        msg = self.logMessage.toPlainText().strip()
        if not msg:
            return
        timestamp = datetime.now().strftime("%d-%m-%Y - %H:%M:%S")
        self.log_entries.append((timestamp, msg))
        build_pdf(self.pdf_path, self.log_entries, self.header_info)
        self.logMessage.clear()

    # --- Close Event ---
    def closeEvent(self, event):
        text, ok = QtWidgets.QInputDialog.getText(
            self,
            "Password Required",
            "Enter password to close:",
            QtWidgets.QLineEdit.EchoMode.Password
        )
        if ok and text == PASSWORD:
            # Update logout time & hours worked
            self.header_info["logout_time"] = datetime.now().strftime("%H:%M:%S")
            worked_time = datetime.now() - self.start_time
            self.header_info["hours_worked"] = format_timedelta(worked_time)

            build_pdf(self.pdf_path, self.log_entries, self.header_info)
            make_pdf_non_editable(self.pdf_path)
            QMessageBox.information(self, "Log Saved", f"Daily log saved at:\n{self.pdf_path}")
            event.accept()
        else:
            QMessageBox.warning(self, "Access Denied", "Incorrect password. Cannot close application.")
            event.ignore()


# --- Run App ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
