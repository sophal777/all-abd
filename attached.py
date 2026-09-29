import subprocess

LDCONSOLE = r"D:/leidian/LDPlayer9/ldconsole.exe"
ADB = r"C:\platform-tools\adb.exe"

def run_ldconsole(*args):
    result = subprocess.run([LDCONSOLE] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def adb(*cmd):
    return subprocess.run([ADB] + list(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

result = adb("devices")

for line in result.stdout.splitlines()[1:]:
    if "\tdevice" in line:
        device_id = line.split("\t")[0]
        port = device_id.split("-")[-1]
        device_name = f"Sophal - {port}"
        print(device_name)
