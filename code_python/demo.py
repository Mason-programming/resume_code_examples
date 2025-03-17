"""
The following are small snippets of private repository code.
While these projects cant paint a full example, I hope it can
demonstrate my prefered approaches to scenarios within python.
"""


"""
This Python script serves as a custom launcher for Blender that allows a user to pass in a USD file
and automatically open Blender with the appropriate environment settings. It also executes a custom
script (run_in_blender.py) inside Blender.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add source directory to PYTHONPATH
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from dcc_commands.commands import Commands  # Base class

class BlenderLauncher(Commands):
    def __init__(self):
        super().__init__()
        self.blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
        self.bridge_script = project_root / "src/bridge_scripts/run_in_blender.py"

    def configure_env(self):
        """Set Blender-specific environment variables."""
        os.environ["BLENDER_USE_USD"] = "1"
        if self.usd_file:
            os.environ["USD_FILE_PATH"] = self.usd_file
            print(f"🔗 Set USD_FILE_PATH to {self.usd_file}")

    def launch(self):
        """Launch Blender in detached mode with the bridge script."""
        command = [
            self.blender_path,
            "--python", str(self.bridge_script)
        ]

        try:
            subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            print(f"🚀 Blender launched with script: {self.bridge_script.name}")
        except Exception as e:
            print(f"❌ Failed to launch Blender: {e}")

if __name__ == "__main__":
    launcher = BlenderLauncher()
    launcher.base_env()              # Load core pipeline envs
    launcher.configure_env()         # Set Blender-specific envs
    launcher.launch()                # Run Blender
    if launcher.usd_file:
        launcher.save_usd_path()     # Cache for "resume session" feature

#!/usr/bin/env python3
import os
import subprocess
import sys
import pwd

# Base class for shared utilities
class Commands:
    
    def __init__(self):
        self.username = pwd.getpwuid(os.getuid()).pw_name
        self.usd_file = self.parse_args()

    def parse_args(self):
        if len(sys.argv) > 1:
            usd_scene = sys.argv[1]

            if os.path.isdir(usd_scene):
                usd_file = self.find_stage(usd_scene)
                return usd_file

            if usd_scene.endswith(".usd") and os.path.exists(usd_scene):
                return usd_scene
            else:
                print("❌ Please provide a valid .usd file path.")
                sys.exit(1)
        return ""


    def find_stage(self, usd_scene): 

        for root, _, files in os.walk(usd_scene):
            if "stage.usd" in files:
                return os.path.join(root, "stage.usd")

        print("Could not find a USD file")
        return None


    def save_usd_path(self):
        path_file = f"/Users/{self.username}/Desktop/USD_Bridge/last_usd_path.txt"
        with open(path_file, "w") as f:
            f.write(self.usd_file)

    def base_env(self):
        os.environ["PYTHONPATH"] = f"/Users/{self.username}/Desktop/USD_Bridge/modules:" + os.environ.get("PYTHONPATH", "")
        os.environ["USD_PLUGIN_PATH"] = f"/Users/{self.username}/Desktop/USD_Bridge/plugins"


#-----------------------        
"""
The Job Application Tracker helps users manage job applications by extracting job titles and company names from URLs. 
"""
import sys
from datetime import datetime, timedelta
from urllib.parse import unquote, urlparse
from PySide6 import QtCore, QtWidgets, QtMultimedia
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox, QApplication
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect

# ===========================
# Application Tracker Class
# ===========================
class app_tracker: 
    """
    Handles tracking of job applications, including storing URLs, timestamps, 
    extracting job titles, saving/loading data, and checking for past-due applications.
    """

    def __init__(self): 
        self.apps = {}  # Dictionary to store applications {job_title: [timestamp, url]}
        self.count = 0  # Total number of stored applications
        self.apps_past_due = []  # Stores applications that are older than 14 days

    def open_file(self): 
        """
        Reads job applications from 'app_file.txt' and loads them into memory.
        """
        try:
            with open("app_file.txt", "r") as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        elements = value.strip().split()
                        timestamp = elements[0] + " " + elements[1]  # Combine date and time
                        url = " ".join(elements[2:])
                        self.apps[key.strip()] = [timestamp, url]
                        self.count += 1 
        except FileNotFoundError:
            print("No existing file found. Creating new file.")

    def new_app(self, url): 
        """
        Extracts job title from URL and adds it as a new app entry with the current timestamp.
        """
        job_name = self.extract_job_title(url)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if job_name in self.apps: 
            print(f"{job_name} already exists.")
        else: 
            self.apps[job_name] = [timestamp, url]
            self.count += 1 
            print(f"Added new job: {job_name} at {timestamp}")

    def extract_job_title(self, url):
        """
        Dynamically extracts a job title and company name from any job URL.
        """
        parsed_url = urlparse(url)  # Parse the URL into components
        path_parts = unquote(parsed_url.path).split('/')  # Split the path into segments
        netloc_parts = parsed_url.netloc.split('.')

        company = "Unknown Company"
        job_title = "Unknown Job Title"

        # Special handling for Greenhouse URLs
        if "greenhouse.io" in parsed_url.netloc:
            if len(path_parts) > 2 and path_parts[1] != "jobs":
                company = path_parts[1].capitalize()
            else:
                company = "Greenhouse"

            for part in reversed(path_parts):
                if part and not part.isnumeric() and part.lower() != "jobs":
                    job_title = part.replace("-", " ").replace("_", " ").title()
                    break
            return f"{company} - {job_title}"

        # General case for other URLs
        if len(netloc_parts) > 1:
            company = netloc_parts[1].capitalize()

        for part in reversed(path_parts):
            if part and not part.isnumeric() and part.lower() != "jobs":
                job_title = part.replace("-", " ").replace("_", " ").title()
                return f"{company} - {job_title}"

        return f"{company} - Unknown Job Title"

    def save_to_file(self): 
        """
        Saves all tracked applications to 'app_file.txt' for persistence.
        """
        with open("app_file.txt", "w") as f: 
            for key, value in self.apps.items(): 
                f.write(f'{key}: ')
                for element in value: 
                    f.write(f'{element} ')
                f.write(f'\n')

    def check_dates(self): 
        """
        Checks for applications older than 14 days and adds them to the overdue list.
        """
        current_date = datetime.now() 
        for app, elements in self.apps.items(): 
            time = elements[0]
            app_date = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")  # Convert string to datetime
            if current_date - app_date > timedelta(days=14):  # Check if more than 14 days
                self.apps_past_due.append(app)


# ===========================
# Application Tracker UI
# ===========================
class app_tracker_ui(QtWidgets.QWidget): 
    """
    PyQt-based GUI for the Application Tracker. Allows users to add job applications,
    view them in a table, and receive notifications for overdue applications.
    """

    def __init__(self): 
        super().__init__()
        self.setWindowTitle("App Tracker")
        self.resize(700, 400)

        # UI Layout
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Enter Job URL:")
        self.layout.addWidget(self.label)

        self.url_input = QLineEdit(self)
        self.layout.addWidget(self.url_input)

        self.add_button = QPushButton("Add Job")
        self.layout.addWidget(self.add_button)

        self.table = QTableWidget()  
        self.table.setColumnCount(3)  # Columns: App Name, Time Added, URL
        self.table.setHorizontalHeaderLabels(["App Name", "Time Added", "Job URL"])
        self.layout.addWidget(self.table)

        # Load data from file
        self.tracker = app_tracker() 
        self.tracker.open_file()  
        self.populate_ui()

        # Check for overdue applications
        self.tracker.check_dates()
        if len(self.tracker.apps_past_due) != 0: 
            self.show_notification()

        # Connect button click to function
        self.add_button.clicked.connect(self.add_job_from_url)

        # Sound effect for ping
        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile("ping.wav"))  # Add a valid path to a sound file

    def populate_ui(self): 
        """
        Populates the table with stored applications.
        """
        self.table.setRowCount(len(self.tracker.apps))
        for row, (app_name, data_apps) in enumerate(self.tracker.apps.items()):
            timestamp = data_apps[0]
            url = data_apps[1]
            link_label = QLabel(f'<a href="{url}">{url}</a>')
            link_label.setOpenExternalLinks(True)  # Open link in browser
            self.table.setItem(row, 0, QTableWidgetItem(app_name))  # App Name
            self.table.setItem(row, 1, QTableWidgetItem(timestamp))  # Time Added
            self.table.setCellWidget(row, 2, link_label)  # Embed label in the cell

    def show_notification(self):
        """
        Displays a notification for applications submitted over 14 days ago.
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Applications Submitted 14 Days Ago")
        msg_box.setText('Applications that you submitted 14 days ago\n')
        messages = [f'{index}: {app_name}' for index, app_name in enumerate(self.tracker.apps_past_due)]
        msg_box.setText('\n'.join(messages))
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.NoButton)
        msg_box.show()

        QTimer.singleShot(10000, msg_box.close)  # Auto close after 10 seconds

    def add_job_from_url(self):
        """
        Handles adding a new job application from the input field.
        """
        url = self.url_input.text().strip()
        if not url:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter a valid URL.")
            return

        time_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tracker.new_app(url)

        # Update UI and save to file
        self.populate_ui()
        self.tracker.save_to_file()
        self.url_input.clear()