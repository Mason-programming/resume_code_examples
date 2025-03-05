"""
The following are small snippets of private repository code.
While these projects cant paint a full example, I hope it can
demonstrate my prefered approaches to scenarios within python.
"""





#-----------------------------------------
"""
Convert shaders to Lambert shaders 
"""
import os
import re
import logging

import maya.cmds as cmds
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf


def gather_mesh_and_ptex_paths(usd_stage_path):
    """
    Gathers selected meshes in Maya and their corresponding ptex files.
    Uses USD to extract mesh names and find ptex paths.
    If a ptex file is not found, assigns a grey Lambert material.
    """
    logging.info("Processing USD Stage: %s", usd_stage_path)

    pattern = r"[0-9]"
    mesh_and_ptex_paths = {}

    # Load the USD Stage
    stage = Usd.Stage.Open(usd_stage_path)
    if not stage:
        logging.error("Failed to open USD stage.")
        return {}

    # Get selected Maya meshes
    selected_meshes = [mesh for mesh in cmds.ls(sl=True, dag=True) or [] if mesh.endswith("_geo")]

    if not selected_meshes:
        logging.warning("No valid geometry selected in Maya.")
        return {}

    for selected_mesh in selected_meshes:
        mesh_prim = stage.GetPrimAtPath(f"/Meshes/{selected_mesh}")
        if not mesh_prim or not mesh_prim.IsA(UsdGeom.Mesh):
            logging.warning(f"Mesh {selected_mesh} not found in USD stage.")
            continue

        # Remove numerical suffix
        element_name = re.sub(pattern, "", selected_mesh)

        # Construct PTex path
        ptex_path = f"/textures/{element_name}/{selected_mesh}.ptx"

        if os.path.exists(ptex_path):
            mesh_and_ptex_paths[selected_mesh] = ptex_path
        else:
            logging.warning(f"Ptex not found for {selected_mesh}. Assigning grey Lambert.")
            create_grey_lambert_shader(selected_mesh)

    return mesh_and_ptex_paths


def create_grey_lambert_shader(mesh_name):
    """
    Creates and assigns a grey Lambert shader in Maya.
    """
    shader_name = f"{mesh_name}_grey_lambert"
    lambert_shader = cmds.shadingNode("lambert", name=shader_name, asShader=True)
    shader_group = cmds.sets(name=f"{shader_name}SG", renderable=True, empty=True, noSurfaceShader=True)

    cmds.connectAttr(f"{lambert_shader}.outColor", f"{shader_group}.surfaceShader")
    cmds.setAttr(f"{lambert_shader}.color", 0.5, 0.5, 0.5, type="double3")
    cmds.sets(mesh_name, forceElement=shader_group)


def process_ptex_data(mesh_data):
    """
    Processes PTex data and assigns materials based on extracted colors.
    """
    rgb_values = {}

    for mesh, ptex_path in mesh_data.items():
        color_value = extract_ptex_color(ptex_path)
        converted_color = convert_pixel_to_display_color(color_value)

        if converted_color not in rgb_values:
            rgb_values[converted_color] = [mesh]
        else:
            rgb_values[converted_color].append(mesh)

    return rgb_values


def extract_ptex_color(ptex_path):
    """
    Simulates PTex color extraction. (Placeholder value for now).
    """
    return (0.8, 0.6, 0.4)  # Simulated solid color


def convert_pixel_to_display_color(pixel_value):
    """
    Converts a PTex pixel value to display color using gamma correction.
    """
    gamma = 2.2
    return tuple(pow(channel / 255.0, gamma) for channel in pixel_value)


def create_lambert_shader(shader_name, rgb_values):
    """
    Creates and assigns Lambert shaders based on extracted PTex colors.
    """
    for rgb_tuple, meshes in rgb_values.items():
        color_values = list(rgb_tuple)
        cmds.select(meshes, r=True)

        # Create Lambert Shader
        lambert_shader = cmds.shadingNode("lambert", name=shader_name, asShader=True)
        shader_group = cmds.sets(name=f"{shader_name}SG", renderable=True, empty=True, noSurfaceShader=True)

        cmds.connectAttr(f"{lambert_shader}.outColor", f"{shader_group}.surfaceShader")
        cmds.setAttr(f"{lambert_shader}.color", color_values[0], color_values[1], color_values[2], type="double3")
        cmds.sets(meshes, forceElement=shader_group)

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


# ===========================
# Main Execution
# ===========================
if __name__ == '__main__': 
    app = QtWidgets.QApplication([])
    widget = app_tracker_ui() 
    widget.show()
    sys.exit(app.exec())
