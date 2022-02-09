from logging import error, basicConfig, DEBUG, info
from pandas import DataFrame, read_csv
from time import sleep
from psutil import Process
from win32process import GetWindowThreadProcessId
from win32gui import GetForegroundWindow
from os.path import exists, isdir, isfile
from os import listdir, rename, mkdir
from os.path import dirname, realpath
from threading import Thread, Timer
import obspython as obs
from pathlib import Path
from pynput.keyboard import Key, Controller

class Hotkey:
    description = ""
    def __init__(self, callback, obs_settings, _id, description_hk):
        self.obs_data = obs_settings
        self.hotkey_id = obs.OBS_INVALID_HOTKEY_ID
        self.hotkey_saved_key = None
        self.callback = callback
        self._id = _id
        global description
        description = description_hk

        self.load_hotkey()
        self.register_hotkey()
        self.save_hotkey()

    def register_hotkey(self):
        global description
        self.hotkey_id = obs.obs_hotkey_register_frontend(
            "htk_id" + str(self._id), description, self.callback
        )
        obs.obs_hotkey_load(self.hotkey_id, self.hotkey_saved_key)

    def load_hotkey(self):
        self.hotkey_saved_key = obs.obs_data_get_array(
            self.obs_data, "htk_id" + str(self._id)
        )
        obs.obs_data_array_release(self.hotkey_saved_key)

    def save_hotkey(self):
        self.hotkey_saved_key = obs.obs_hotkey_save(self.hotkey_id)
        obs.obs_data_set_array(
            self.obs_data, "htk_id" + str(self._id), self.hotkey_saved_key
        )
        obs.obs_data_array_release(self.hotkey_saved_key)

# Hotkey instance class
class h:
    htk_copy = None  # this attribute will hold instance of Hotkey

# Hotkey instance 
h1 = h()

class IsDirError(Exception):
    pass

class WrongIndexError(Exception):
    pass

class SoundNotActivatedError(Exception):
    def __init__(self, active_game, active_window):
        self.active_game = active_game
        self.active_window = active_window

    def __str__(self):
        log(self.message)
        if self.message: return "Couldn't activate Sound for game: {active_game} ; active window: {active_window}".format(active_game=self.active_game, active_window=self.active_window)
        else: return "Couldn't activate Sound"

programs = DataFrame(data={"window_name": [], "folder_name": [], "is_game": []})
active_window = ""
enabled = True
debug = False
videos_path = str(Path.home()) + "\Videos\\"
clip_path = videos_path + "Clips\\"
active_game = ""

def err(msg):
    error(msg) 
    assert(msg)

def log(msg):
    global debug
    if debug: 
        print(msg)
        info(msg)

PATH = dirname(realpath(__file__)) + "\\"
PATH_CSV = PATH + "programs.csv"
PATH_LOG = PATH + "log.log"

MISSING_FOLDER_NAME = "None"

basicConfig(filename=(PATH_LOG), level=DEBUG, format='%(asctime)s: obs_clip - %(message)s ')

def write_csv():
    log("write_csv()")
    global programs
    programs.to_csv(PATH_CSV, index=False)

def get_data():
    log("get_data()")
    global programs
    try: programs = read_csv(PATH_CSV)
    except FileNotFoundError: write_csv()

get_data()

def get_active_window_name():
    pid = GetWindowThreadProcessId(GetForegroundWindow())
    return Process(pid[-1]).name()

def activate_sound(active_game):
    log("activate_sound()")
    global active_window
    counter = 0
    # wait for the game being foreground
    while active_game != active_window:
        active_window = get_active_window_name()
        sleep(1)
        counter += 1
        if counter == 10 * 60: 
            raise SoundNotActivatedError(active_game, active_window)
    # activate sound for game
    press_key(Key.f9)

def get_program_by_window_name(window_name):
    return programs.loc[programs.window_name == window_name]

kc = Controller()

def press_key(key):
    kc.press(key)
    sleep(0.05)
    kc.release(key)

def get_active_window():
    log("get_active_window()")
    global enabled, programs, active_window, active_game
    active_game = ""

    while enabled:
        active_window = get_active_window_name()
        program = get_program_by_window_name(active_window)

        try: program_is_game = program.get("is_game").values.tolist()[0] == 1
        except IndexError:
            get_data()
            programs = programs.append({
                "window_name": active_window,
                "folder_name": active_window.split(".")[0],
                "is_game": 0
            }, ignore_index=True)
            write_csv()
        else: 
            if program_is_game and (active_game != active_window):
                # if active window is a game and if the game isn't already activated
                active_game = active_window
                Timer(30, activate_sound(active_game))
            
        sleep(10)

def create_folder(folder_name):
    log("create_folder()")
    if not exists(clip_path + folder_name): mkdir(clip_path + folder_name)
    elif not isdir(clip_path + folder_name): raise IsDirError(clip_path + folder_name)

def get_files_in_folder(path):
    log("get_files_in_folder()")
    return [ i for i in listdir(path) if isfile(path + i) ]

def sort_folder():
    log("sort_folder()")
    files = get_files_in_folder(clip_path)
    if len(files) != 0:
        create_folder(MISSING_FOLDER_NAME)
        for f in files: rename(clip_path + f, clip_path + MISSING_FOLDER_NAME + "\\" + f)

def get_clip_name():
    log("get_clip_name()")
    files = get_files_in_folder(clip_path)
    while len(files) == 0:
        files = get_files_in_folder(clip_path)
        sleep(0.1)
    return files[0]

def save_replay():
    log("save_replay()")
    sort_folder()
    if not obs.obs_frontend_replay_buffer_active(): err("replay buffer not active")
    else:
        obs.obs_frontend_replay_buffer_save()
        global programs, active_game
        
        try:
            f = get_program_by_window_name(active_window) if active_window != 0 else get_program_by_window_name(active_window)
            folder_name = f.get("folder_name").values.tolist()[0]
        except IndexError:
            err("Index Error for window: " + active_window)
            folder_name = MISSING_FOLDER_NAME

        create_folder(folder_name)

        clip_name = get_clip_name()

        while True:
            try: rename(clip_path + clip_name, clip_path + folder_name + "\\" + clip_name)
            except PermissionError: sleep(0.1)
            else: break

def cb_hk_save_replay(pressed):
    log("cb_hk_save_replay: " + str(pressed))
    if pressed:
        save_replay()

def cb_get_data(props, prop):
    log("cb_get_data")
    get_data()

def cb_save_replay(props, prop):
    log("cb_save_replay")
    save_replay()

# API
def script_load(settings):
    log("script_load()")
    h1.htk_copy = Hotkey(cb_hk_save_replay, settings, "hk_clip", "Clip Replay Buffer and sort into folder")

# API
def script_save(settings):
    log("script_save()")
    h1.htk_copy.save_hotkey()

# API
# Description displayed in the Scripts dialog window
def script_description(): return "OBS Clipping Script"

# API
# Set default values for variables??
def script_defaults(settings):
    log("script_defaults()")
    
    global enabled, debug, clip_path

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_bool(settings, "debug", debug)
    obs.obs_data_set_default_string(settings, "clip_path", clip_path)
    
    if not exists(Path.home()): raise Exception('Home path "' + str(Path.home()) + '" doesn\'t exist')
    elif not isdir(Path.home()): raise IsDirError('Home path "' + str(Path.home()) + '" is not a dir')

    if not exists(videos_path): mkdir(videos_path)
    elif not isdir(videos_path): raise IsDirError(videos_path)

    if not exists(clip_path): mkdir(clip_path)
    elif not isdir(clip_path): raise IsDirError(clip_path)
    log(
f"""
Enabled: {obs.obs_data_get_bool(settings, 'enabled')}
Debug: {obs.obs_data_get_bool(settings, 'debug')}
""")

# API
# Run on every script update
# Called when the script’s settings (if any) have been changed by the user.
def script_update(settings):
    log("script_update()")

    global enabled, debug, clip_path

    if debug and not obs.obs_data_get_bool(settings, "debug"): print("Debug stop")
    elif not debug and obs.obs_data_get_bool(settings, "debug"): print("Debug start")

    debug = obs.obs_data_get_bool(settings, "debug")
    enabled = obs.obs_data_get_bool(settings, "enabled")
    clip_path = obs.obs_data_get_string(settings, "clip_path") + "\\"


# API
# Script view under the description
def script_properties():
    log("script_properties()")
    global clip_path
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debug", "Debug")
    obs.obs_properties_add_button(props, "btn_get_data", "Refresh Data", cb_get_data)
    obs.obs_properties_add_button(props, "btn_save_replay", "Save Replay", cb_save_replay)
    obs.obs_properties_add_path(props, "clip_path", "Clips Path", obs.OBS_PATH_DIRECTORY, "", clip_path)
    #obs.obs_properties_add_list(props, "programs", "Programs", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    #obs.obs_properties_add_list(props, "folder", "Folder", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    #obs.obs_properties_add_bool(props, "is_game", "Is it a game")

    return props

t = Thread(target=get_active_window)
t.start()