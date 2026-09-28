import sys
import os
import subprocess
import time
import threading

from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLabel, QFileDialog, QTableWidgetItem, QPushButton, QLineEdit, QTableWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QHeaderView, QAbstractItemView, QComboBox, QListView, QStackedWidget
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal


all_My_file = "My_file"
myPhth = "Phth"
myVideos = "Videos"
Pull_APK = "Pulled_APK"


def create_folders(*folder_names):
    for folder_name in folder_names:
        path = os.path.join(all_My_file, folder_name)
        os.makedirs(path, exist_ok=True)


create_folders(myPhth, myVideos, Pull_APK)

path_file = os.path.join(all_My_file, myPhth, "path.txt")


class ClickableLabel(QLabel):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        self.image = None
        self.original_width = 0
        self.original_height = 0
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(250)

    def set_image(self, image):
        self.image = image
        self.original_width = image.width()
        self.original_height = image.height()
        self.setPixmap(QPixmap.fromImage(image).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image:
            self.setPixmap(QPixmap.fromImage(self.image).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        if not self.image or not self.pixmap() or self.pixmap().isNull():
            return

        pixmap = self.pixmap()
        x = event.pos().x()
        y = event.pos().y()
        px = (self.width() - pixmap.width()) // 2
        py = (self.height() - pixmap.height()) // 2

        if x < px or y < py or x > px + pixmap.width() or y > py + pixmap.height():
            return

        real_x = int((x - px) * self.original_width / pixmap.width())
        real_y = int((y - py) * self.original_height / pixmap.height())

        if self.main.mode_combo.currentText() == "Position":
            self.main.result.setText(f"X = {real_x}, Y = {real_y}")
        else:
            self.main.find_text(real_x, real_y)


class MainWindow(QWidget):
    result_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.ldconsole_path = ""
        self.devices = []
        self.ADB = r"C:\platform-tools\adb.exe"

        self.setWindowTitle("LDPlayer Manager")
        self.resize(800, 500)

        os.makedirs("My_file/Data", exist_ok=True)

        self.create_ui()
        self.load_saved_path()

        self.result_signal.connect(self.show_result)

    def create_ui(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)
        self.main_layout.setColumnStretch(0, 3)
        self.main_layout.setColumnStretch(1, 7)
        self.main_layout.setRowStretch(2, 1)

        self.create_panel1()

        self.title = QLabel("LDPlayer Tools")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setMinimumHeight(40)

        self.top_button_row = QHBoxLayout()
        self.top_button_row.setSpacing(8)

        self.top_button1 = QPushButton("ADB / APK")
        self.top_button2 = QPushButton("Screen / Text")
        self.top_button3 = QPushButton("Tools")

        self.top_button1.setMinimumHeight(42)
        self.top_button2.setMinimumHeight(42)
        self.top_button3.setMinimumHeight(42)

        self.top_button_row.addWidget(self.top_button1)
        self.top_button_row.addWidget(self.top_button2)
        self.top_button_row.addWidget(self.top_button3)

        self.pages = QStackedWidget()

        self.create_panel2()
        self.create_panel3()
        self.create_panel4()

        self.pages.addWidget(self.panel2)
        self.pages.addWidget(self.panel3)
        self.pages.addWidget(self.panel4)

        self.main_layout.addWidget(self.title, 0, 0, 1, 2)
        self.main_layout.addLayout(self.top_button_row, 1, 0, 1, 2)
        self.main_layout.addWidget(self.panel1, 2, 0, 1, 1)
        self.main_layout.addWidget(self.pages, 2, 1, 1, 1)

        self.top_button1.clicked.connect(lambda: self.pages.setCurrentWidget(self.panel2))
        self.top_button2.clicked.connect(lambda: self.pages.setCurrentWidget(self.panel3))
        self.top_button3.clicked.connect(lambda: self.pages.setCurrentWidget(self.panel4))

        self.set_style()

    def create_panel1(self):
        self.panel1 = QFrame()
        self.panel1.setObjectName("Panel")

        self.panel1_layout = QVBoxLayout(self.panel1)
        self.panel1_layout.setContentsMargins(10, 10, 10, 10)
        self.panel1_layout.setSpacing(8)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Status"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.panel1_layout.addWidget(self.table)

        self.path_row = QHBoxLayout()
        self.path_row.setSpacing(8)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("LDPlayer Path...")

        self.open_button = QPushButton("Open Path")
        self.open_button.setMinimumHeight(42)

        self.path_row.addWidget(self.path_edit)
        self.path_row.addWidget(self.open_button)

        self.panel1_layout.addLayout(self.path_row)

        self.control_row = QHBoxLayout()
        self.control_row.setSpacing(8)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        self.start_button.setMinimumHeight(42)
        self.stop_button.setMinimumHeight(42)

        self.control_row.addWidget(self.start_button)
        self.control_row.addWidget(self.stop_button)

        self.panel1_layout.addLayout(self.control_row)

        self.open_button.clicked.connect(self.open_path)
        self.start_button.clicked.connect(self.start_selected)
        self.stop_button.clicked.connect(self.stop_selected)

    def load_saved_path(self):
        if not os.path.isfile(path_file):
            return

        try:
            with open(path_file, "r", encoding="utf-8") as file:
                folder = file.read().strip()

            if not folder:
                return

            ldconsole = os.path.join(folder, "ldconsole.exe")

            if not os.path.isdir(folder):
                return

            if not os.path.isfile(ldconsole):
                return

            self.ldconsole_path = ldconsole
            self.path_edit.setText(folder)
            self.load_ldplayer()

        except Exception as e:
            print(e)

    def save_path(self, folder):
        try:
            with open(path_file, "w", encoding="utf-8") as file:
                file.write(folder)

            return True

        except Exception as e:
            print(e)
            return False

    def open_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select LDPlayer Folder")

        if not folder:
            return

        ldconsole = os.path.join(folder, "ldconsole.exe")

        if not os.path.isfile(ldconsole):
            self.show_result("ldconsole.exe not found")
            return

        self.ldconsole_path = ldconsole
        self.path_edit.setText(folder)
        self.save_path(folder)
        self.load_ldplayer()

    def load_ldplayer(self):
        if not self.ldconsole_path or not os.path.isfile(self.ldconsole_path):
            return

        try:
            result = subprocess.run([self.ldconsole_path, "list2"], capture_output=True, text=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode != 0:
                return

            self.table.setRowCount(0)

            for count, line in enumerate(result.stdout.strip().splitlines(), 1):
                if not line.strip():
                    continue

                parts = [x.strip() for x in line.split(",")]

                if len(parts) < 2:
                    continue

                index = parts[0]
                name = parts[1]
                status = "🛑 Stop"

                if len(parts) >= 3 and parts[2] == "1":
                    status = "✨ Running"

                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, QTableWidgetItem(str(count)))

                name_item = QTableWidgetItem(name)
                name_item.setData(Qt.UserRole, index)

                self.table.setItem(row, 1, name_item)
                self.table.setItem(row, 2, QTableWidgetItem(status))

        except Exception as e:
            print(e)

    def get_selected_rows(self):
        rows = []

        for index in self.table.selectionModel().selectedRows():
            row = index.row()

            if row not in rows:
                rows.append(row)

        rows.sort()

        return rows

    def start_selected(self):
        rows = self.get_selected_rows()

        if not rows or not self.ldconsole_path:
            return

        for row in rows:
            name_item = self.table.item(row, 1)

            if not name_item:
                continue

            index = name_item.data(Qt.UserRole)

            try:
                subprocess.Popen([self.ldconsole_path, "launch", "--index", str(index)], creationflags=subprocess.CREATE_NO_WINDOW)
                self.table.item(row, 2).setText("✨ Running")

            except Exception as e:
                self.table.item(row, 2).setText("Error")
                print(e)

    def stop_selected(self):
        rows = self.get_selected_rows()

        if not rows or not self.ldconsole_path:
            return

        for row in rows:
            name_item = self.table.item(row, 1)

            if not name_item:
                continue

            index = name_item.data(Qt.UserRole)

            try:
                subprocess.Popen([self.ldconsole_path, "quit", "--index", str(index)], creationflags=subprocess.CREATE_NO_WINDOW)
                self.table.item(row, 2).setText("🛑 Stopping")

            except Exception as e:
                self.table.item(row, 2).setText("Error")
                print(e)

    def create_panel2(self):
        self.panel2 = QWidget()

        self.panel2_layout = QVBoxLayout(self.panel2)
        self.panel2_layout.setContentsMargins(10, 10, 10, 10)
        self.panel2_layout.setSpacing(8)

        self.device_table = QTableWidget(0, 4)
        self.device_table.setHorizontalHeaderLabels(["Name", "Model", "IMEI", "Manufacturer"])
        self.device_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.device_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.device_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.device_table.verticalHeader().setVisible(False)
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.folder = os.path.join("My_file", "Pulled_APK")
        os.makedirs(self.folder, exist_ok=True)

        self.model = QStandardItemModel(self)

        self.apk_row = QHBoxLayout()
        self.apk_row.setSpacing(8)

        self.action_combo = QComboBox()
        self.action_combo.addItems(["Install APK", "Uninstall APK", "Pull APK"])
        self.action_combo.setMinimumHeight(42)

        self.combo = QComboBox()
        self.combo.setView(QListView())
        self.combo.setModel(self.model)
        self.combo.setMinimumHeight(42)

        self.apk_row.addWidget(self.action_combo)
        self.apk_row.addWidget(self.combo)

        self.apk_button_row = QHBoxLayout()
        self.apk_button_row.setSpacing(8)

        self.get_devices_button = QPushButton("Refresh Devices")
        self.execute_button = QPushButton("Run APK Action")
        self.refresh_apk_button = QPushButton("Refresh APK")

        self.get_devices_button.setMinimumHeight(42)
        self.execute_button.setMinimumHeight(42)
        self.refresh_apk_button.setMinimumHeight(42)

        self.apk_button_row.addWidget(self.get_devices_button)
        self.apk_button_row.addWidget(self.execute_button)
        self.apk_button_row.addWidget(self.refresh_apk_button)

        self.app_row = QHBoxLayout()
        self.app_row.setSpacing(8)

        self.app = QComboBox()
        self.app.addItems(["Facebook", "Facebook Lite", "YouTube", "Telegram"])
        self.app.setMinimumHeight(42)

        self.open_app_button = QPushButton("Open App")
        self.open_app_button.setMinimumHeight(42)

        self.app_row.addWidget(self.app)
        self.app_row.addWidget(self.open_app_button)

        self.media_row = QHBoxLayout()
        self.media_row.setSpacing(8)

        self.Video_Image = QComboBox()
        self.Video_Image.addItems(["Video", "Image"])
        self.Video_Image.setMinimumHeight(42)

        self.upload_media_button = QPushButton("Upload Media")
        self.upload_media_button.setMinimumHeight(42)

        self.media_row.addWidget(self.Video_Image)
        self.media_row.addWidget(self.upload_media_button)

        self.result = QLabel("Ready")
        self.result.setObjectName("Result")
        self.result.setMinimumHeight(35)
        self.result.setAlignment(Qt.AlignCenter)

        self.panel2_layout.addWidget(self.device_table)
        self.panel2_layout.addLayout(self.apk_row)
        self.panel2_layout.addLayout(self.apk_button_row)
        self.panel2_layout.addLayout(self.app_row)
        self.panel2_layout.addLayout(self.media_row)
        self.panel2_layout.addWidget(self.result)

        self.get_devices_button.clicked.connect(self.get_devices)
        self.combo.view().pressed.connect(self.toggle_item)
        self.execute_button.clicked.connect(self.execute)
        self.refresh_apk_button.clicked.connect(self.load_apk)
        self.open_app_button.clicked.connect(self.start)
        self.upload_media_button.clicked.connect(self.upload_media_to_adb)

        self.load_apk()

    def create_panel3(self):
        self.panel3 = QWidget()

        self.panel3_layout = QVBoxLayout(self.panel3)
        self.panel3_layout.setContentsMargins(10, 10, 10, 10)
        self.panel3_layout.setSpacing(8)

        self.screen_title = QLabel("Screen / Text Tools")
        self.screen_title.setAlignment(Qt.AlignCenter)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Position", "Text"])

        self.screen_label = ClickableLabel(self)
        self.screen_label.setText("Screen Preview")

        self.screen_result = QLabel("Click screen to get position")
        self.screen_result.setAlignment(Qt.AlignCenter)

        self.panel3_layout.addWidget(self.screen_title)
        self.panel3_layout.addWidget(self.mode_combo)
        self.panel3_layout.addWidget(self.screen_label)
        self.panel3_layout.addWidget(self.screen_result)

    def create_panel4(self):
        self.panel4 = QWidget()

        self.panel4_layout = QVBoxLayout(self.panel4)
        self.panel4_layout.setContentsMargins(10, 10, 10, 10)
        self.panel4_layout.setSpacing(8)

        self.tools_title = QLabel("Tools")
        self.tools_title.setAlignment(Qt.AlignCenter)

        self.reload_button = QPushButton("Reload LDPlayer")
        self.reload_button.setMinimumHeight(42)

        self.check_adb_button = QPushButton("Check ADB")
        self.check_adb_button.setMinimumHeight(42)

        self.tools_result = QLabel("Ready")
        self.tools_result.setAlignment(Qt.AlignCenter)

        self.panel4_layout.addWidget(self.tools_title)
        self.panel4_layout.addWidget(self.reload_button)
        self.panel4_layout.addWidget(self.check_adb_button)
        self.panel4_layout.addWidget(self.tools_result)
        self.panel4_layout.addStretch()

        self.reload_button.clicked.connect(self.load_ldplayer)
        self.check_adb_button.clicked.connect(self.check_adb)

    def get_adb_devices(self):
        try:
            if not os.path.isfile(self.ADB):
                return []

            result = subprocess.run([self.ADB, "devices"], capture_output=True, text=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)

            devices = []

            for line in result.stdout.splitlines():
                line = line.strip()

                if not line or line.startswith("List of devices"):
                    continue

                parts = line.split()

                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])

            return devices

        except Exception as e:
            print(e)
            return []

    def get_devices(self):
        self.devices = self.get_adb_devices()
        self.device_table.setRowCount(0)

        for device in self.devices:
            row = self.device_table.rowCount()
            self.device_table.insertRow(row)

            model = self.cmd("-s", device, "shell", "getprop", "ro.product.model").strip()
            manufacturer = self.cmd("-s", device, "shell", "getprop", "ro.product.manufacturer").strip()

            if not model:
                model = "Unknown"

            if not manufacturer:
                manufacturer = "Unknown"

            self.device_table.setItem(row, 0, QTableWidgetItem(device))
            self.device_table.setItem(row, 1, QTableWidgetItem(model))
            self.device_table.setItem(row, 2, QTableWidgetItem("N/A"))
            self.device_table.setItem(row, 3, QTableWidgetItem(manufacturer))

        self.show_result(f"ADB Devices: {len(self.devices)}")

    def cmd(self, *args):
        try:
            result = subprocess.run([self.ADB, *args], capture_output=True, text=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)

            return result.stdout.strip()

        except Exception as e:
            print(e)
            return ""

    def auto_click(self, device, x, y):
        subprocess.run([self.ADB, "-s", device, "shell", "input", "tap", str(x), str(y)], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def start(self):
        thread = threading.Thread(target=self.open_selected_app, daemon=True)
        thread.start()

    def open_selected_app(self):
        devices = self.get_adb_devices()

        if not devices:
            self.result_signal.emit("No ADB device found")
            return

        device = devices[0]
        app_name = self.app.currentText()

        if app_name == "Facebook":
            self.open_facebook(device)
            time.sleep(5)
            self.auto_click(device, 72, 213)
            time.sleep(5)
            self.auto_click(device, 70, 255)
            time.sleep(5)
            self.auto_click(device, 126, 299)
            self.result_signal.emit("Facebook Opened")

        elif app_name == "Facebook Lite":
            self.open_facebook_lite(device)

        elif app_name == "YouTube":
            self.open_youtube(device)

        elif app_name == "Telegram":
            self.open_telegram(device)

    def open_facebook(self, device):
        subprocess.run([self.ADB, "-s", device, "shell", "monkey", "-p", "com.facebook.katana", "1"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def open_facebook_lite(self, device):
        subprocess.run([self.ADB, "-s", device, "shell", "monkey", "-p", "com.facebook.lite", "1"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.result_signal.emit("Facebook Lite Opened")

    def open_youtube(self, device)f, device)
