import sys
import os
import re
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLabel, QFileDialog, QTableWidgetItem, QPushButton, QLineEdit, QTableWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QHeaderView, QAbstractItemView, QComboBox, QListView, QStackedWidget
from PyQt5.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import time
import threading
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
        self.top_button3 = QPushButton("Panel 4")

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
        self.path_edit.setPlaceholderText("Enter Path...")

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
                self.table.item(row, 2).setText("✨ Start")
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
                self.table.item(row, 2).setText("Stopping")
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

        self.combo_row1 = QHBoxLayout()

        self.action_combo = QComboBox()
        self.action_combo.addItems(["Install APK", "Uninstall APK", "Pull APK"])

        self.combo = QComboBox()
        self.combo.setView(QListView())
        self.combo.setModel(self.model)

        self.combo_row1.addWidget(self.action_combo)
        self.combo_row1.addWidget(self.combo)

        self.button_row1 = QHBoxLayout()

        self.get_devices_button = QPushButton("Get Devices")
        self.execute_button = QPushButton("APK")
        self.button3 = QPushButton("app")

        self.get_devices_button.setMinimumHeight(42)
        self.execute_button.setMinimumHeight(42)
        self.button3.setMinimumHeight(42)

        self.button_row1.addWidget(self.get_devices_button)
        self.button_row1.addWidget(self.execute_button)
        self.button_row1.addWidget(self.button3)

        self.button_row2 = QHBoxLayout()


        self.button4 = QPushButton("Upload Video")


        self.Video_Image = QComboBox()
        self.Video_Image.addItems([ "Image", "Video"])





        self.app = QComboBox()
        self.app.addItems(["facebook", "facebook Lite", "youtube", "telegram"])







        self.button4.setMinimumHeight(42)
        self.app.setMinimumHeight(42)
        self.Video_Image.setMinimumHeight(42)

        self.button_row2.addWidget(self.button4)
        self.button_row2.addWidget(self.app)
        self.button_row2.addWidget(self.Video_Image)

        self.button_row3 = QHBoxLayout()

        self.button7 = QPushButton("Button 7")
        self.button8 = QPushButton("Button 8")

        self.button7.setMinimumHeight(42)
        self.button8.setMinimumHeight(42)

        self.button_row3.addWidget(self.button7)
        self.button_row3.addWidget(self.button8)

        self.panel2_layout.addWidget(self.device_table)
        self.panel2_layout.addLayout(self.combo_row1)
        self.panel2_layout.addLayout(self.button_row1)
        self.panel2_layout.addLayout(self.button_row2)
        self.panel2_layout.addLayout(self.button_row3)








        self.get_devices_button.clicked.connect(self.get_devices)
        self.combo.view().pressed.connect(self.toggle_item)
        self.execute_button.clicked.connect(self.execute)
        self.button3.clicked.connect(self.load_apk)
        self.button4.clicked.connect(self.upload_media_to_adb)
        self.button3.clicked.connect(self.open_selected_app)



        self.load_apk()






    def auto_click(self, device, x, y):
        subprocess.run(["adb", "-s", device, "shell", "input", "tap", str(x), str(y)], capture_output=True)
    def start(self):
        Rut = threading.Thread(target=self.open_selected_app)
        Rut.start()
    def open_selected_app(self):

        devices = self.get_adb_devices()

        if not devices:
            self.result.setText("No ADB device found")
            return

        device = devices[0]
        app_name = self.app.currentText()

        if app_name == "facebook":
            self.open_facebook(device)
            time.sleep(5)
            self.auto_click(device, 72, 213)
            time.sleep(5)
            time.sleep(5)
            self.auto_click(device, 70, 255)
            time.sleep(5)
            time.sleep(5)
            self.auto_click(device, 126, 299)
            time.sleep(5)


        elif app_name == "facebook Lite":
            self.open_facebook_lite(device)
        elif app_name == "youtube":
            self.open_youtube(device)
        elif app_name == "telegram":
            self.open_telegram(device)



    def open_facebook(self, device):
        subprocess.run(["adb", "-s", device, "shell", "monkey", "-p", "com.facebook.katana", "1"], capture_output=True)
        self.result.setText("Facebook Opened")




    def open_youtube(self, device):
        subprocess.run(["adb", "-s", device, "shell", "monkey", "-p", "com.google.android.youtube", "1"], capture_output=True)
        self.result.setText("YouTube Opened")
    def open_telegram(self, device):
        subprocess.run(["adb", "-s", device, "shell", "monkey", "-p", "org.telegram.messenger", "1"], capture_output=True)
        self.result.setText("Telegram Opened")
    def upload_media_to_adb(self):
        media_type = self.Video_Image.currentText()

        if media_type == "Video":
            folder = QFileDialog.getExistingDirectory(self, "Select Video Folder")
            extensions = [".mp4", ".mkv", ".avi", ".mov", ".webm"]
            target_folder = "/sdcard/Movies/"
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
            extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
            target_folder = "/sdcard/Pictures/"

        if not folder:
            return

        devices = self.get_adb_devices()

        if not devices:
            self.result.setText("No ADB device found")
            return

        device = devices[0]

        files = []

        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)

            if os.path.isfile(path) and os.path.splitext(filename)[1].lower() in extensions:
                files.append(path)

        if not files:
            self.result.setText(f"No {media_type.lower()} found")
            return

        subprocess.run(["adb", "-s", device, "shell", "mkdir", "-p", target_folder], capture_output=True)

        success = 0

        for file_path in files:
            filename = os.path.basename(file_path)
            target = target_folder + filename

            result = subprocess.run(["adb", "-s", device, "push", file_path, target], capture_output=True, text=True, encoding="utf-8", errors="ignore")

            if result.returncode == 0:
                success += 1

        self.result.setText(f"Uploaded {success}/{len(files)} {media_type}")
    def load_apk(self):
        os.makedirs(self.folder, exist_ok=True)
        self.model.clear()

        for file in os.listdir(self.folder):
            if file.lower().endswith(".apk"):
                item = QStandardItem(file)
                item.setCheckable(True)
                item.setCheckState(Qt.Unchecked)
                self.model.appendRow(item)

        self.combo.setCurrentText("Select APK")

    def toggle_item(self, index):
        item = self.model.itemFromIndex(index)

        if not item:
            return

        item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked)
        self.combo.setCurrentText(f"Selected: {len(self.selected_items())}")
        self.combo.showPopup()

    def selected_items(self):
        return [self.model.item(i).text() for i in range(self.model.rowCount()) if self.model.item(i).checkState() == Qt.Checked]

    def execute(self):
        action = self.action_combo.currentText()

        if action == "Install APK":
            self.install_apk()
        elif action == "Uninstall APK":
            self.uninstall_apk()
        elif action == "Pull APK":
            self.pull_apk()

    def install_apk(self):
        devices = self.get_adb_devices()

        if not devices:
            return

        for apk in self.selected_items():
            path = os.path.join(self.folder, apk)

            for device in devices:
                subprocess.run([self.ADB, "-s", device, "install", "-r", path], creationflags=subprocess.CREATE_NO_WINDOW)

    def uninstall_apk(self):
        devices = self.get_adb_devices()

        if not devices:
            return

        for apk in self.selected_items():
            package = os.path.splitext(apk)[0]

            for device in devices:
                subprocess.run([self.ADB, "-s", device, "uninstall", package], creationflags=subprocess.CREATE_NO_WINDOW)

    def pull_apk(self):
        devices = self.get_adb_devices()

        if not devices:
            return

        for device in devices:
            packages = self.cmd("-s", device, "shell", "pm", "list", "packages", "-3").splitlines()

            for package_line in packages:
                package = package_line.replace("package:", "").strip()

                if package:
                    remote = self.cmd("-s", device, "shell", "pm", "path", package)

                    if remote.startswith("package:"):
                        remote = remote.splitlines()[0].replace("package:", "").strip()
                        filename = package + ".apk"
                        local = os.path.join(self.folder, filename)
                        subprocess.run([self.ADB, "-s", device, "pull", remote, local], creationflags=subprocess.CREATE_NO_WINDOW)

        self.load_apk()

    def cmd(self, *args):
        try:
            result = subprocess.run([self.ADB, *args], capture_output=True, text=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
            return result.stdout.strip()
        except Exception:
            return ""

    def get_imei(self, serial):
        s = self.cmd("-s", serial, "shell", "service", "call", "iphonesubinfo", "1")
        s = re.sub(r"\d{4,}", "", s)
        s = s.replace("0x", "").replace(":", "").replace(".", "").replace("'", "")
        s = re.sub(r"[A-Za-z]", "", s)
        numbers = re.findall(r"\d+", s)
        return "".join(numbers)

    def get_devices(self):
        self.device_table.setRowCount(0)

        output = self.cmd("devices")

        if not output:
            return

        self.devices = output.splitlines()[1:]

        for line in self.devices:
            parts = line.split()

            if len(parts) < 2 or parts[1] != "device":
                continue

            serial = parts[0]
            model = self.cmd("-s", serial, "shell", "getprop", "ro.product.model")
            manufacturer = self.cmd("-s", serial, "shell", "getprop", "ro.product.manufacturer")
            imei = self.get_imei(serial)

            row = self.device_table.rowCount()
            self.device_table.insertRow(row)

            self.device_table.setItem(row, 0, QTableWidgetItem(serial))
            self.device_table.setItem(row, 1, QTableWidgetItem(model))
            self.device_table.setItem(row, 2, QTableWidgetItem(imei))
            self.device_table.setItem(row, 3, QTableWidgetItem(manufacturer))

    def create_panel3(self):
        self.panel3 = QWidget()
        self.panel3_layout = QVBoxLayout(self.panel3)
        self.panel3_layout.setContentsMargins(10, 10, 10, 10)
        self.panel3_layout.setSpacing(8)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Position", "Text"])

        self.result = QLineEdit()
        self.result.setReadOnly(True)
        self.result.setPlaceholderText("Click on screenshot...")

        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Enter text...")

        self.add_button = QPushButton("Add")
        self.saved_combo = QComboBox()
        self.save_button = QPushButton("Save")
        self.show_button = QPushButton("Show")
        self.refresh_button = QPushButton("Refresh")

        self.screen = ClickableLabel(self)
        self.screen.setMinimumHeight(250)

        self.print_result = QLineEdit()
        self.print_result.setReadOnly(True)
        self.print_result.setPlaceholderText("Screen text will appear here...")

        self.copy_button = QPushButton("Copy")

        self.row1 = QHBoxLayout()
        self.row1.addWidget(self.mode_combo)
        self.row1.addWidget(self.result)

        self.row2 = QHBoxLayout()
        self.row2.addWidget(self.input_text)
        self.row2.addWidget(self.add_button)
        self.row2.addWidget(self.saved_combo)
        self.row2.addWidget(self.save_button)

        self.row3 = QHBoxLayout()
        self.row3.addWidget(self.show_button)
        self.row3.addWidget(self.refresh_button)

        self.row4 = QHBoxLayout()
        self.row4.addWidget(self.screen)

        self.row5 = QHBoxLayout()
        self.row5.addWidget(self.print_result)
        self.row5.addWidget(self.copy_button)

        self.panel3_layout.addLayout(self.row1)
        self.panel3_layout.addLayout(self.row2)
        self.panel3_layout.addLayout(self.row3)
        self.panel3_layout.addLayout(self.row4)
        self.panel3_layout.addLayout(self.row5)

        self.refresh_button.clicked.connect(self.get_screenshot)
        self.show_button.clicked.connect(self.show_screen_text)
        self.save_button.clicked.connect(self.save_combo)
        self.add_button.clicked.connect(self.add_result)
        self.copy_button.clicked.connect(self.copy_value)

        self.load_combo_files()

    def create_panel4(self):
        self.panel4 = QWidget()
        self.panel4_layout = QVBoxLayout(self.panel4)
        self.panel4_layout.setContentsMargins(10, 10, 10, 10)
        self.panel4_layout.setSpacing(8)

        self.panel4_title = QLabel("Panel 4")
        self.panel4_title.setAlignment(Qt.AlignCenter)

        self.panel4_button1 = QPushButton("Panel 4 Button 1")
        self.panel4_button2 = QPushButton("Panel 4 Button 2")
        self.panel4_button3 = QPushButton("Panel 4 Button 3")

        self.panel4_button1.setMinimumHeight(42)
        self.panel4_button2.setMinimumHeight(42)
        self.panel4_button3.setMinimumHeight(42)

        self.panel4_layout.addWidget(self.panel4_title)
        self.panel4_layout.addWidget(self.panel4_button1)
        self.panel4_layout.addWidget(self.panel4_button2)
        self.panel4_layout.addWidget(self.panel4_button3)
        self.panel4_layout.addStretch()

    def get_adb_devices(self):
        try:
            result = subprocess.run([self.ADB, "devices"], capture_output=True, text=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
            devices = []

            for line in result.stdout.splitlines()[1:]:
                parts = line.strip().split()

                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])

            return devices

        except Exception as e:
            print("ADB Error:", e)
            return []

    def get_screenshot(self):
        devices = self.get_adb_devices()

        if not devices:
            self.result.setText("No ADB device found")
            self.print_result.clear()
            return

        device = devices[0]

        try:
            result = subprocess.run([self.ADB, "-s", device, "exec-out", "screencap", "-p"], capture_output=True)

            if result.returncode != 0:
                self.result.setText("Screenshot failed")
                return

            image = QImage.fromData(result.stdout)

            if image.isNull():
                self.result.setText("Invalid screenshot")
                return

            self.screen.set_image(image)
            self.result.setText(f"Device: {device}")

        except Exception as e:
            self.result.setText(str(e))

    def adb_read_screen_text(self, device):
        try:
            dump = subprocess.run([self.ADB, "-s", device, "shell", "uiautomator", "dump", "/sdcard/window.xml"], capture_output=True, text=True, encoding="utf-8", errors="ignore")

            if dump.returncode != 0:
                return []

            result = subprocess.run([self.ADB, "-s", device, "shell", "cat", "/sdcard/window.xml"], capture_output=True, text=True, encoding="utf-8", errors="ignore")

            if result.returncode != 0:
                return []

            return re.findall(r'text="([^"]*)"', result.stdout)

        except Exception as e:
            print("Read Text Error:", e)
            return []

    def show_screen_text(self):
        devices = self.get_adb_devices()

        if not devices:
            self.print_result.setText("No ADB device found")
            return

        device = devices[0]
        texts = self.adb_read_screen_text(device)
        texts = [text.strip() for text in texts if text.strip()]

        self.print_result.setText(" | ".join(texts) if texts else "No text found")

    def find_text(self, x, y):
        self.result.setText(f"Text at X={x}, Y={y}")

    def add_result(self):
        value = self.input_text.text().strip()

        if value:
            self.saved_combo.addItem(value)
            self.input_text.clear()

    def save_combo(self):
        folder = "My_file/Data"
        os.makedirs(folder, exist_ok=True)

        index = 0

        while True:
            filename = "ComboBox.txt" if index == 0 else f"ComboBox{index}.txt"
            path = os.path.join(folder, filename)

            if not os.path.exists(path):
                break

            index += 1

        with open(path, "w", encoding="utf-8") as file:
            for i in range(self.saved_combo.count()):
                file.write(self.saved_combo.itemText(i) + "\n")

        self.result.setText(f"Saved: {filename}")

    def load_combo_files(self):
        folder = "My_file/Data"

        if not os.path.exists(folder):
            return

        files = []

        for filename in os.listdir(folder):
            if re.fullmatch(r"ComboBox(?:\d+)?\.txt", filename):
                if filename == "ComboBox.txt":
                    number = 0
                else:
                    number = int(re.search(r"\d+", filename).group())

                files.append((number, filename))

        files.sort()

        self.saved_combo.clear()

        for _, filename in files:
            path = os.path.join(folder, filename)

            try:
                with open(path, "r", encoding="utf-8") as file:
                    for line in file:
                        value = line.strip()

                        if value:
                            self.saved_combo.addItem(value)

            except Exception as e:
                print("Load Error:", e)

    def copy_value(self):
        value = self.print_result.text().strip()

        if value:
            QApplication.clipboard().setText(value)
            print("Copied:", value)

    def set_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #111111;
                color: #FFFFFF;
                font-size: 14px;
            }

            QFrame#Panel {
                background: #181818;
                border: 1px solid #444444;
                border-radius: 8px;
            }

            QLabel {
                color: #D4AF37;
                font-weight: bold;
            }

            QPushButton {
                background: #222222;
                color: #D4AF37;
                border: 1px solid #D4AF37;
                border-radius: 6px;
                padding: 8px;
            }

            QPushButton:hover {
                background: #333333;
            }

            QLineEdit {
                background: #151515;
                color: #D4AF37;
                border: 1px solid #D4AF37;
                border-radius: 6px;
                padding: 8px;
            }

            QComboBox {
                background: #222222;
                color: #D4AF37;
                border: 1px solid #D4AF37;
                border-radius: 6px;
                padding: 6px;
            }

            QComboBox QAbstractItemView {
                background: #181818;
                color: #FFFFFF;
                selection-background-color: #333333;
                selection-color: #D4AF37;
            }

            QTableWidget {
                background: #151515;
                color: #FFFFFF;
                gridline-color: #444444;
                border: 1px solid #444444;
            }

            QHeaderView::section {
                background: #222222;
                color: #D4AF37;
                padding: 6px;
                border: 1px solid #444444;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
