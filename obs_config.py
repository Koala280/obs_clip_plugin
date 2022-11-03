from os.path import dirname, realpath
from logging import error, basicConfig, DEBUG, info
import sys
from psutil import Process
from win32process import GetWindowThreadProcessId
from win32gui import GetForegroundWindow
import subprocess
from csv import reader, writer

PATH: str = (dirname(sys.executable) if getattr(sys, "frozen", False) else dirname(realpath(__file__))) + "\\"
PATH_CSV: str = PATH + "programs.csv"
PATH_LOG: str = PATH + "obs_log.log"
PATH_NOTIFICATION = PATH + "obs_notification_controller.exe"

WINDOW_NAME: int = 0
FOLDER_NAME: int = 1
IS_GAME: int = 2

class Config():

    programs: list = list()
    active_game_name: str = ""

    def get_program_window_name(self, program: tuple) -> str: return program[WINDOW_NAME]
    def get_program_folder_name(self, program: tuple) -> str: return program[FOLDER_NAME]
    def get_program_is_game(self, program: tuple) -> bool: return int(program[IS_GAME]) != 0
    def get_folder_name_by_window_name(self, window_name: str) -> str: return self.get_program_folder_name(self.get_program_by_window_name(window_name))
    def get_is_game_by_window_name(self, window_name: str) -> bool: return self.get_program_is_game(self.get_program_by_window_name(window_name))
    def get_active_program_folder_name(self) -> str: return self.get_program_folder_name(self.get_active_program())
    def get_active_program_is_game(self) -> bool: return self.get_program_is_game(self.get_active_program())
    def program_exists(self, window_name: str) -> bool: return len([item for item in self.programs if item[WINDOW_NAME] == window_name]) == 0

    def __init__(self, script_name: str):
        basicConfig(filename=(PATH_LOG), level=DEBUG, format='%(asctime)s:%(levelname)s: {} - %(message)s'.format(script_name))
        self.get_programs_from_csv()

    def error(self, msg: str) -> None: error(msg)

    def info(self, msg: str) -> None: info(msg)

    def write_csv(self, data: list, path) -> None:
        info("write_csv()")
        with open(path, "w", newline='') as f: 
            w = writer(f)
            for row in data: w.writerow(row)

    def write_programs_to_csv(self) -> None:
        info("write_programs_to_csv()")
        self.write_csv(self.programs, PATH_CSV)

    def get_data_from_csv(self, path: str) -> list:
        try:
            with open(path, "r", newline='') as f: return list(map(tuple, reader(f)))
        except FileNotFoundError:
            self.write_programs_to_csv()
            return list()

    def get_programs_from_csv(self) -> None: self.programs = self.get_data_from_csv(PATH_CSV)

    def notification(self, msg: str) -> None: subprocess.run([PATH_NOTIFICATION, msg])        

    def get_active_window_name(self) -> str:
        try: return Process(GetWindowThreadProcessId(GetForegroundWindow())[-1]).name()
        except:
            self.error("get_active_window_name no Process found.")
            return ""

    def get_program_by_window_name(self, window_name: str) -> tuple:
        if window_name == "": error("window_name empty")
        self.get_programs_from_csv()
        if self.program_exists(window_name): self.add_program(window_name)
        return [item for item in self.programs if item[WINDOW_NAME] == window_name][0]
    
    def window_name_in_programs(self, window_name: str) -> bool: return len(self.get_program_by_window_name(window_name)) != 0
    
    def get_active_program(self) -> tuple:
        return self.get_program_by_window_name(self.get_active_window_name())
    
    def add_program(self, new_program_name: str) -> None:
        self.info(f"add_program({ new_program_name })")
        self.programs.append((new_program_name, new_program_name.split(".")[0], 0))
        self.write_programs_to_csv()