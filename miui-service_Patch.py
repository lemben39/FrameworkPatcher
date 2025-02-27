import os
import re
import logging
import sys
import utils

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

isCN = sys.argv[1].lower() == 'true'
fixNotification = sys.argv[2].lower() == 'true'
multiFloatingWindow = sys.argv[3].lower() == 'true'
addGboard = sys.argv[4].lower() == 'true'
disable_flag_secure = sys.argv[5].lower() == 'true'

def modify_file(file_path, search_pattern, add_line_template):
    logging.info(f"Modifying file: {file_path}")
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    for line in lines:
        modified_lines.append(line)
        match = re.search(search_pattern, line)
        if match:
            vX = match.group(1)
            add_line = add_line_template.format(vX=vX)
            logging.info(f"Found pattern in file: {file_path} with variable {vX}")
            modified_lines.append(add_line + '\n')
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)
    logging.info(f"Completed modification for file: {file_path}")

def replace_string_in_file(file_path, search_string, replace_string):
    logging.info(f"Replacing string in file: {file_path}")
    with open(file_path, 'r') as file:
        content = file.read()
    modified_content = content.replace(search_string, replace_string)
    with open(file_path, 'w') as file:
        file.write(modified_content)
    logging.info(f"Completed string replacement in file: {file_path}")

def modify_policy_manager(file_path):
    logging.info(f"Modifying PolicyManager file: {file_path}")
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    pattern_found = False
    search_pattern = r'sput-boolean v0, Lcom/miui/server/greeze/PolicyManager;->CN_MODEL:Z'
    add_line = '    const/4 v0, 0x0\n'

    for line in lines:
        if re.search(search_pattern, line):
            logging.info(f"Found pattern in file: {file_path}")
            modified_lines.append(add_line)
            pattern_found = True
        modified_lines.append(line)

    if not pattern_found:
        logging.warning(f"Pattern not found in file: {file_path}")
    else:
        with open(file_path, 'w') as file:
            file.writelines(modified_lines)
        logging.info(f"Completed modification for file: {file_path}")

def modify_smali_files(directories):
    notification_classes = [
        'com/android/server/AppOpsServiceStubImpl.smali',
        'com/android/server/alarm/AlarmManagerServiceStubImpl.smali',
        'com/android/server/am/BroadcastQueueModernStubImpl.smali',
        'com/android/server/am/ProcessManagerService.smali',
        'com/android/server/am/ProcessSceneCleaner.smali',
        'com/android/server/job/JobServiceContextImpl.smali',
        'com/android/server/notification/NotificationManagerServiceImpl.smali',
        'com/miui/server/greeze/GreezeManagerService.smali',
        'miui/app/ActivitySecurityHelper.smali',
    ]
    window_classes = [
        'com/android/server/am/ActivityManagerServiceImpl.smali',
        'com/android/server/ForceDarkAppListManager.smali',
        'com/android/server/wm/WindowManagerServiceImpl.smali'
    ]
    multiFloatingWindow_classes = [
        'com/android/server/wm/MiuiFreeFormStackDisplayStrategy.smali',
    ]
    addGboard_classes = [
        'com/android/server/am/ActivityManagerServiceImpl$1.smali',
        'com/android/server/input/InputManagerServiceStubImpl.smali',
        'com/android/server/inputmethod/InputMethodManagerServiceImpl.smali',
        'com/android/server/wm/MiuiSplitInputMethodImpl.smali'
    ]

    search_pattern = r'sget-boolean (v\d+), Lmiui/os/Build;->IS_INTERNATIONAL_BUILD:Z'
    add_line_template = '    const/4 {vX}, 0x1'
    search_string = "com.baidu.input_mi"
    replace_string = "com.google.android.inputmethod.latin"

    for directory in directories:
        logging.info(f"Scanning directory: {directory}")
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".smali"):
                    filepath = os.path.join(root, file)
                    utils.patch(filepath)

        if disable_flag_secure:
            for class_file in window_classes:
                file_path = os.path.join(directory, class_file)
                if os.path.exists(file_path):
                    logging.info(f"Found file: {file_path}")
                    utils.modify_file(file_path, "")
                else:
                    logging.warning(f"File not found: {file_path}")

        if fixNotification and isCN:
            for class_file in notification_classes:
                file_path = os.path.join(directory, class_file)
                if os.path.exists(file_path):
                    logging.info(f"Found file: {file_path}")
                    modify_file(file_path, search_pattern, add_line_template)
                else:
                    logging.warning(f"File not found: {file_path}")

            policy_manager_file = os.path.join(directory, 'com/miui/server/greeze/PolicyManager.smali')
            if os.path.exists(policy_manager_file):
                logging.info(f"Found file: {policy_manager_file}")
                modify_policy_manager(policy_manager_file)
            else:
                logging.warning(f"File not found: {policy_manager_file}")

        if multiFloatingWindow:
            for class_file in multiFloatingWindow_classes:
                file_path = os.path.join(directory, class_file)
                if os.path.exists(file_path):
                    logging.info(f"Found file: {file_path}")
                    utils.modify_file(file_path, "")
                else:
                    logging.warning(f"File not found: {file_path}")

        if addGboard and isCN:
            for class_file in addGboard_classes:
                file_path = os.path.join(directory, class_file)
                if os.path.exists(file_path):
                    logging.info(f"Found file: {file_path}")
                    replace_string_in_file(file_path, search_string, replace_string)
                else:
                    logging.warning(f"File not found: {file_path}")

if __name__ == "__main__":
    directories = ["miui_services_classes"]
    modify_smali_files(directories)