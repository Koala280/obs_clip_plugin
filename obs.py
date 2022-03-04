from logging import basicConfig, DEBUG, info, error
from pandas import DataFrame, read_csv
from psutil import Process, process_iter
from sqlalchemy import true
from win32process import GetWindowThreadProcessId
from win32gui import GetForegroundWindow
from os.path import dirname, realpath
from os import startfile
from time import sleep
import sys
from traceback import print_exc

PATH = (dirname(sys.executable) if getattr(sys, "frozen", False) else dirname(realpath(__file__))) + "\\"

PATH_CSV = PATH + "programs.csv"
PATH_LOG = PATH + "log.log"
OBS_PROCNAME = "obs64.exe"
OBS64_PATH = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OBS Studio\obs_rb.lnk"
programs = DataFrame(data={"window_name": [], "folder_name": [], "is_game": []})
game_running = ""

basicConfig(filename=(PATH_LOG), level=DEBUG, format='%(asctime)s:%(levelname)s: obs - %(message)s')

def write_csv():
    global programs
    programs.to_csv(PATH_CSV, index=False)

def get_data():
    global programs
    try: programs = read_csv(PATH_CSV)
    except FileNotFoundError: write_csv()

get_data()

# check whether the process name matches
def get_process(name): return [ process for process in process_iter() if process.name() == name ]

def process_active(proc_name): return len(get_process(proc_name)) > 0

def run_obs(): 
    info("run_obs()")
    if not process_active(OBS_PROCNAME): startfile(OBS64_PATH)

def kill_obs():
    info("kill_obs()")
    if process_active(OBS_PROCNAME):
        for process in get_process(OBS_PROCNAME): process.kill()

def get_active_window_name():
    window_name = ""
    timer = 60 # seconds
    while (len(window_name) == 0) and (timer >= 0):
        pid = GetWindowThreadProcessId(GetForegroundWindow())
        try: window_name = Process(pid[-1]).name()
        except ValueError: 
            error("get_active_window_name no Process found. Try again. Timer: " + timer)
            sleep(5)
            timer -= 5
    if timer <= 0: error("Time out: get_active_window_name. No Process found")   
    return window_name

def get_program_by_window_name(window_name):
    return programs.loc[programs.window_name == window_name]

def stop_obs():
    info("stop_obs()")
    global game_running
    while process_active(game_running): sleep(10)
    kill_obs()
    game_running = ""

def start_obs(counter):
    info(f"start_obs({counter})")
    try:
        while True:
            global programs, game_running
            active_window = get_active_window_name()
            program = get_program_by_window_name(active_window)
            try: 
                #program_window_name = program.get("window_name").values.tolist()[0] == 1
                #program_folder_name = program.get("folder_name").values.tolist()[0] == 1
                program_is_game = program.get("is_game").values.tolist()[0] == 1
            except IndexError:
                get_data()
                programs = programs.append({
                    "window_name": active_window,
                    "folder_name": active_window.split(".")[0],
                    "is_game": 0
                }, ignore_index=True)
                write_csv()
            else:
                if program_is_game and len(game_running) == 0:
                    run_obs()
                    game_running = active_window
                    stop_obs()
            sleep(10)
    except Exception as e:
        error('WARNING CRITICAL EXCEPTION RAISED: ', e.__class__.__name__)
        print_exc()
        start_obs(counter + 1)
start_obs(0)