import psutil
import win32gui
import win32process

def get_window_info_by_process(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            windows = []

            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    _, proc_id = win32process.GetWindowThreadProcessId(hwnd)
                    if proc_id == pid:
                        windows.append(hwnd)
                return True

            win32gui.EnumWindows(callback, windows)
            executable_path = psutil.Process(pid).exe()
            return windows, executable_path

    return None, None

# Example usage
process_name = "Discord.exe"  # Replace with the name of the process you want to retrieve information for
windows, executable_path = get_window_info_by_process(process_name)

if windows:
    print("Executable Path:", executable_path)
    print("Windows:")
    for hwnd in windows:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        print("Title:", title)
        print("Class:", class_name)
        print("-----")
else:
    print("Process not found.")