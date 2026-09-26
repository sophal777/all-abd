import os
import subprocess


ADB = r"C:\platform-tools\adb.exe"

all_My_file = "My_file"

myPhth = "Phth"
myVideos = "Videos"
Pull_APK = "Pulled_APK"


def create_folders(*folder_names):

    for folder_name in folder_names:

        path = os.path.join(
            all_My_file,
            folder_name
        )

        os.makedirs(
            path,
            exist_ok=True
        )


create_folders(
    myPhth,
    myVideos,
    Pull_APK
)


def apk_manager(device=None):

    # =========================
    # 1. Get Installed Apps
    # =========================

    command = [ADB]

    if device:
        command += ["-s", device]

    command += [
        "shell",
        "pm",
        "list",
        "packages",
        "-3"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    if result.returncode != 0:
        print(result.stderr)
        return []

    apps = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if line.startswith("package:"):

            package_name = line.replace(
                "package:",
                "",
                1
            ).strip()

            if package_name:
                apps.append(package_name)

    # =========================
    # 2. Show Installed Apps
    # =========================

    print("Installed Apps:")

    for i, package_name in enumerate(apps, 1):

        print(
            f"{i}. {package_name}"
        )

    # =========================
    # 3. Pull All APKs
    # =========================

    output_folder = os.path.join(
        all_My_file,
        Pull_APK
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    print("\nPulling APKs...\n")

    for package_name in apps:

        # =========================
        # Get APK Path
        # =========================

        command = [ADB]

        if device:
            command += ["-s", device]

        command += [
            "shell",
            "pm",
            "path",
            package_name
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode != 0:

            print(
                f"APK Path not found: {package_name}"
            )

            continue

        apk_paths = []

        for line in result.stdout.splitlines():

            line = line.strip()

            if line.startswith("package:"):

                apk_path = line.replace(
                    "package:",
                    "",
                    1
                ).strip()

                if apk_path:
                    apk_paths.append(apk_path)

        # =========================
        # Pull APK
        # =========================

        for index, apk_path in enumerate(
            apk_paths,
            1
        ):

            if len(apk_paths) == 1:

                filename = (
                    f"{package_name}.apk"
                )

            else:

                filename = (
                    f"{package_name}_{index}.apk"
                )

            output_file = os.path.join(
                output_folder,
                filename
            )

            command = [ADB]

            if device:
                command += ["-s", device]

            command += [
                "pull",
                apk_path,
                output_file
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            if result.returncode == 0:

                print(
                    f"Pulled: {output_file}"
                )

            else:

                print(
                    f"Failed: {package_name}"
                )

                print(result.stderr)

    return apps


# =========================
# Run
# =========================

apps = apk_manager()
