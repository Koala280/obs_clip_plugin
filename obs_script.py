# %%
from os import startfile
from psutil import NoSuchProcess
from time import sleep
from threading import Thread
import helpers
import event

exit_obs_allowed: bool = True
programs: list = list()
active_game: helpers.Program = None
active_program: helpers.Program = None

OBS64_PATH: str = r"C:\Users\tomsb\Desktop\obs clips.lnk"
OBS_PROCNAME: str = "obs64.exe"

EVENT_PROGRAMS_UPDATED = "programs_updated"
EVENT_ACTIVE_PROGRAM_UPDATED = "active_program_updated"
EVENT_ACTIVE_GAME_UPDATED = "active_game_updated"

def stop_obs() -> None:
    helpers.log("stop_obs()")
    # wait till game is closed then stop obs
    if not helpers.process_active(OBS_PROCNAME):
        helpers.err("OBS were not running")
        helpers.notification("OBS were not running")
    elif not exit_obs_allowed:
        helpers.err("Exit OBS not allowed")
        helpers.notification("Exit OBS not allowed")
    else:
        processes = helpers.get_process(OBS_PROCNAME)
        for process in processes:
            try:
                process.kill()
            except NoSuchProcess:
                pass
        helpers.notification("OBS stopped")


def start_obs() -> None:
    helpers.log("start_obs()")
    if helpers.process_active(OBS_PROCNAME):
        helpers.err("OBS already running.")
    else:
        startfile(OBS64_PATH)
        helpers.notification("OBS started")


def update_active_program() -> None:
    helpers.log("update_active_program()")
    global programs, active_program
    programs = helpers.csv_load()
    while True:
        active_process = helpers.get_active_process()
        if not helpers.program_exists(active_process, programs):
            programs = helpers.new_program(active_process, programs)
            event.post(EVENT_PROGRAMS_UPDATED)
        active_program = helpers.get_program_by_process(active_process, programs)
        event.post(EVENT_ACTIVE_PROGRAM_UPDATED)
        sleep(30)


def handle_active_program_updated_event():
    global active_game

    if (active_game == None) and (active_program.is_game):
        active_game = active_program
        event.post(EVENT_ACTIVE_GAME_UPDATED)
        helpers.log(f"{active_program.process} running. Start OBS")
        start_obs()
    elif (active_game != None) and (not helpers.process_active(active_game.process)):
        active_game = None
        event.post(EVENT_ACTIVE_GAME_UPDATED)
        stop_obs()


def handle_programs_updated_event():
    helpers.csv_save(programs)


def handle_active_game_updated_event():
    if active_game != None:
        helpers.set_active_game_folder_name(active_game.folder)
    else:
        helpers.set_active_game_folder_name(None)


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
