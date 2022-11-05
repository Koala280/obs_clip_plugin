# %%
from os import startfile
from psutil import process_iter, NoSuchProcess
from time import sleep
from threading import Thread
import helpers as h
from win32process import GetWindowThreadProcessId
from win32gui import GetForegroundWindow
from psutil import Process
import event

exit_obs_allowed: bool = True
programs: list = list()
active_game: h.Program = None
active_program: h.Program = None

OBS64_PATH: str = r"C:\Users\Toms\Desktop\obs clips.lnk"
OBS_PROCNAME: str = "obs64.exe"

EVENT_PROGRAMS_UPDATED = "programs_updated"
EVENT_ACTIVE_PROGRAM_UPDATED = "active_program_updated"
EVENT_ACTIVE_GAME_UPDATED = "active_game_updated"


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


def stop_obs() -> None:
    h.log("stop_obs()")
    # wait till game is closed then stop obs
    if not process_active(OBS_PROCNAME):
        h.err("OBS were not running")
        h.notification("OBS were not running")
    elif not exit_obs_allowed:
        h.err("Exit OBS not allowed")
        h.notification("Exit OBS not allowed")
    else:
        processes = get_process(OBS_PROCNAME)
        for process in processes:
            try:
                process.kill()
            except NoSuchProcess:
                pass
        h.notification("OBS stopped")


def start_obs() -> None:
    h.log("start_obs()")
    if process_active(OBS_PROCNAME):
        h.err("OBS already running.")
    else:
        startfile(OBS64_PATH)
        h.notification("OBS started")


def update_active_program() -> None:
    h.log("update_active_program()")
    global programs, active_program
    programs = h.csv_load()
    while True:
        try:
            active_process = Process(GetWindowThreadProcessId(
                GetForegroundWindow())[-1]).name()
        except:
            h.err("get_active_window_name no Process found.")
            active_process = None
        if not h.program_exists(active_process, programs):
            programs = h.new_program(active_process, programs)
            event.post(EVENT_PROGRAMS_UPDATED)
        active_program = h.get_program_by_process(active_process, programs)
        event.post(EVENT_ACTIVE_PROGRAM_UPDATED)
        sleep(10)




def handle_active_program_updated_event():
    global active_game

    if (active_game == None) and (active_program.is_game):
        active_game = active_program
        h.log(f"{active_program.process} running. Start OBS")
        start_obs()
    elif (active_game != None) and (not process_active(active_game.process)):
        active_game = None
        stop_obs()


def handle_programs_updated_event():
    h.csv_save(programs)


def handle_active_game_updated_event():
    h.set_active_game_folder_name(active_game.folder)


def main():
    event.subscribe(EVENT_ACTIVE_PROGRAM_UPDATED,
                    handle_active_program_updated_event)
    event.subscribe(EVENT_PROGRAMS_UPDATED, handle_programs_updated_event)
    event.subscribe(EVENT_ACTIVE_GAME_UPDATED,
                    handle_active_game_updated_event)
    t1 = Thread(target=update_active_program)
    t1.start()


if __name__ == '__main__':
    main()

# %%
