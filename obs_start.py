# %%
from os import startfile
from psutil import process_iter, NoSuchProcess
from time import sleep
from obs_config import *

c: Config = Config("obs_start")
exit_obs_allowed: bool = True

OBS64_PATH: str = r"C:\Users\Toms\Desktop\obs clips.lnk"
OBS_PROCNAME: str = "obs64.exe"

# check whether the process name matches


def get_process(name: str) -> list:
    process: list = []
    for proc in process_iter():
        try:
            if proc.name() == name:
                process.append(proc)
        except NoSuchProcess:
            pass

    return process


def process_active(
    proc_name: str) -> bool: return len(get_process(proc_name)) > 0


def kill_obs() -> None:
    c.info("kill_obs()")
    if not process_active(OBS_PROCNAME):
        c.error("OBS were not running")
    elif not exit_obs_allowed:
        c.error("Exit OBS not allowed")
    else:
        processes = get_process(OBS_PROCNAME)
        for process in processes:
            try:
                process.kill()
            except NoSuchProcess:
                pass


def stop_obs() -> None:
    c.info("stop_obs()")
    # wait till game is closed then stop obs
    while process_active(c.active_game_name):
        _ = c.get_active_program()
        sleep(10)
    kill_obs()
    c.active_game_name = ""
    c.notification("OBS stopped")


def run_obs() -> None:
    c.info("run_obs()")
    if process_active(OBS_PROCNAME):
        c.error("OBS already running.")
        global exit_obs_allowed
        exit_obs_allowed = False
    else:
        startfile(OBS64_PATH)
        c.notification("OBS started")


def start_obs() -> None:
    c.info("start_obs()")
    while True:
        if (len(c.active_game_name) == 0) and (c.get_active_program_is_game()):
            c.active_game_name = c.get_active_window_name()
            run_obs()
            stop_obs()
        sleep(10)


start_obs()
# %%
