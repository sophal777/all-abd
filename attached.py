import sys
import subprocess
import re
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QTableWidget, QTableWidgetItem

LDCONSOLE = r"D:/leidian/LDPlayer9/ldconsole.exe"
ADB = r"C:\platform-tools\adb.exe"

def run_ldconsole(*args):
    cmd = [LDCONSOLE] + list(args)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def adb(*cmd):
    return subprocess.run([ADB] + list(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

def get_devices():
    result = adb("devices")
    devices = []

    for line in result.stdout.splitlines():
        if "\tdevice" in line:
            devices.append(line.split("\t")[0])

    return devices

def get_running_names():
    stdout, stderr, code = run_ldconsole("runninglist")
    return stdout.splitlines()

def get_imei(device):
    result = adb("-s", device, "shell", "service", "call", "iphonesubinfo", "1")
    s = re.sub(r"\d{4,}", "", result.stdout)
    s = s.replace("0x", "").replace(":", "").replace(".", "").replace("'", "")
    s = re.sub(r"[A-Za-z]", "", s)
    numbers = re.findall(r"\d+", s)
    return "".join(numbers)

def get_model(device):
    return adb("-s", device, "shell", "getprop", "ro.product.model").stdout.strip()

def get_manufacturer(device):
    return adb("-s", device, "shell", "getprop", "ro.product.manufacturer").stdout.strip()

def get_ip(device):
    result = adb("-s", device, "shell", "ip", "route")
    ip_match = re.search(r"src\s+(\d+\.\d+\.\d+\.\d+)", result.stdout)
    return ip_match.group(1) if ip_match else ""

def get_treble(device):
    result = adb("-s", device, "shell", "getprop", "ro.treble.enabled")
    return result.stdout.strip()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LDPlayer Manager")
        self.resize(900, 500)

        self.device_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.treble_button = QPushButton("Treble")
        self.result = QLabel("Ready")

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Name", "Device", "IMEI", "Model", "Manufacturer", "IP", "Treble"])

        self.refresh_button.clicked.connect(self.load_devices)
        self.treble_button.clicked.connect(self.check_treble)

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.device_combo)
        self.top_layout.addWidget(self.refresh_button)
        self.top_layout.addWidget(self.treble_button)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.table)
        self.main_layout.addWidget(self.result)

        self.load_devices()

    def load_devices(self):
        self.device_combo.clear()
        self.table.setRowCount(0)

        devices = get_devices()
        names = get_running_names()

        for i, device in enumerate(devices):
            name = names[i] if i < len(names) else f"Device-{i + 1}"
            imei = get_imei(device)
            model = get_model(device)
            manufacturer = get_manufacturer(device)
            ip = get_ip(device)
            treble = get_treble(device)

            display_name = f"{name} - {device.split('-')[-1]}"

            self.device_combo.addItem(display_name, device)

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(device))
            self.table.setItem(row, 2, QTableWidgetItem(imei))
            self.table.setItem(row, 3, QTableWidgetItem(model))
            self.table.setItem(row, 4, QTableWidgetItem(manufacturer))
            self.table.setItem(row, 5, QTableWidgetItem(ip))
            self.table.setItem(row, 6, QTableWidgetItem(treble))

        self.result.setText(f"Devices: {len(devices)}")

    def check_treble(self):
        device = self.device_combo.currentData()

        if not device:
            self.result.setText("No Device Selected")
            return

        treble = get_treble(device)

        if treble == "true":
            status = "Supported"
        elif treble == "false":
            status = "Not Supported"
        else:
            status = treble if treble else "Unknown"

        self.result.setText(f"{device} | Treble: {status}")

        for row in range(self.table.rowCount()):
            if self.table.item(row, 1).text() == device:
                self.table.setItem(row, 6, QTableWidgetItem(status))
                break

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
