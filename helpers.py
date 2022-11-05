import sys
from os.path import dirname, realpath
from logging import error, basicConfig, DEBUG, info
import csv
import subprocess

PATH: str = (dirname(sys.executable) if getattr(
    sys, "frozen", False) else dirname(realpath(__file__))) + "\\"
PATH_PROGRAMS_CSV: str = PATH + "programs.csv"
PATH_LOG: str = PATH + "obs_log.log"
PATH_NOTIFICATION = PATH + "obs_notification_controller.exe"
PATH_GAME_CSV: str = PATH + "game.csv"

PROCESS: int = 0
FOLDER: int = 1
IS_GAME: int = 2

""" LOG """
debug: bool = True

basicConfig(filename=(PATH_LOG), level=DEBUG,
            format='%(asctime)s:%(levelname)s: %(message)s')


def log(msg: str) -> None:
    if debug:
        print(msg)
        info(msg)


def err(msg: str) -> None:
    if debug:
        print(msg)
        error(msg)


""" 
Program class
process: name of process (mostly just name of executable)
folder: name of folder
is_game: is this program a game
"""


class Program:

    def __init__(self, process, folder, is_game=False):
        self.process = process
        self.folder = folder
        self.is_game = bool(int(is_game))


""" CSV """


def csv_save(programs: list) -> None:
    log("csv_save()")
    if programs == []:
        programs = [Program("obs_notification_controller.exe",
                            "obs_notification_controller.exe")]
    with open(PATH_PROGRAMS_CSV, "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(['process', 'folder', "is_game"])
        w.writerows(map(lambda x: [x.process, x.folder, int(x.is_game)], programs))


def csv_load() -> list:
    log("csv_load()")
    try:
        with open(PATH_PROGRAMS_CSV, "r", newline='') as f: #TODO SWITCH TO a instead of r
            r = csv.reader(f)
            next(r)
            programs = []
            for row in r:
                if row[PROCESS] != []:
                    programs.append(Program(row[PROCESS], row[FOLDER], row[IS_GAME]))
            return programs
    except FileNotFoundError:
        csv_save([])
        return csv_load()

    
def set_active_game_folder_name(folder_name: str) -> None:
    log("set_active_game_folder_name()")
    with open(PATH_GAME_CSV, "w") as f:
        w = csv.writer(f)
        w.writerow(folder_name)
    
def get_active_game_folder_name() -> str:
    log("get_active_game_folder_name()")
    with open(PATH_GAME_CSV, "r") as f:
        r = csv.reader(f)
        return next(r)
            

""" Program Helpers """


def program_exists(process: str, programs: list) -> bool: return len(
    [program for program in programs if program.process == process]) != 0


def get_program_by_process(process: str, programs: list) -> Program:
    return [
        program for program in programs if program.process == process][0]


def new_program(new_program_name: str, programs: list) -> None:
    log(f"add_program({ new_program_name })")
    programs.append(
        Program(new_program_name, new_program_name.split(".")[0], 0))
    return programs

""" Notification """
def notification(msg: str) -> None: subprocess.run([PATH_NOTIFICATION, msg])