import subprocess
import re

ADB = r"C:\platform-tools\adb.exe"


def cmd(*args):
    return subprocess.run(
        [ADB, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    ).stdout.strip()


def imei(serial):
    s = cmd("-s", serial, "shell", "service", "call", "iphonesubinfo", "1")
    s = re.sub(r"\d{4,}|0x|:|[A-Za-z.']", "", s)
    return "".join(re.findall(r"\d+", s))


devices = cmd("devices").splitlines()[1:]

for line in devices:
    p = line.split()

    if len(p) >= 2 and p[1] == "device":
        serial = p[0]

        model = cmd("-s", serial, "shell", "getprop", "ro.product.model")
        manufacturer = cmd(
            "-s", serial,
            "shell", "getprop", "ro.product.manufacturer"
        )

        print("Name         :", serial)
        print("Model        :", model)
        print("IMEI         :", imei(serial))
        print("Manufacturer :", manufacturer)
        print("-" * 40)
