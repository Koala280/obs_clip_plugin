# %%
from os import startfile
from psutil import process_iter, NoSuchProcess
from time import sleep
from obs_config import *

c: Config = Config("obs_start")
active_game_name: str = ""

OBS64_PATH: str = r"C:\Users\Toms\Desktop\obs_rb.lnk"
OBS_PROCNAME: str = "obs64.exe"

# check whether the process name matches
def get_process(name: str) -> list: 
    process = []
    for proc in process_iter():
        try:
            if proc.name() == name: process.append(proc)
        except NoSuchProcess: pass
            
    return process

def process_active(proc_name: str) -> bool: return len(get_process(proc_name)) > 0

def kill_obs() -> None:
    c.info("kill_obs()")
    if not process_active(OBS_PROCNAME): c.error("OBS were not running")
    else:
        processes = get_process(OBS_PROCNAME)
        for process in processes:
            try:
                process.kill()
            except NoSuchProcess: pass
    
def stop_obs() -> None:
    c.info("stop_obs()")
    global active_game_name
    # wait till game is closed then stop obs
    while process_active(active_game_name):
        ignore = c.get_active_program()
        sleep(10)
    kill_obs()
    active_game_name = ""
    c.notification("OBS stopped")

def run_obs() -> None:
    c.info("run_obs()")
    if process_active(OBS_PROCNAME):
        c.error("OBS already running. Restarting")
        kill_obs()
        sleep(10)
    startfile(OBS64_PATH)
    c.notification("OBS started")

def start_obs() -> None:
    c.info("start_obs()")
    global active_game_name
    while True:
        if (len(active_game_name) == 0) and (c.get_active_program_is_game()):
                active_game_name = c.get_active_window_name()
                run_obs()
                stop_obs()
        sleep(10)

start_obs()
# %%
