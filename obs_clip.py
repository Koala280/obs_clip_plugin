from time import sleep
from os.path import exists, isdir, isfile
from os import listdir, rename, mkdir
from pathlib import Path
import obspython as obs
import helpers
from threading import Thread
import json
from win32gui import GetForegroundWindow, GetClassName, GetWindowText

videos_path: str = str(Path.home()) + "\Videos\\"
clip_path: str = videos_path + "Clips\\"
enabled: bool = True
debug: bool = helpers.debug
game_capture_source_name_video: str = "Game Capture"
game_capture_source_name_audio: str = "Game Capture Audio"

MISSING_FOLDER_NAME = "Unsorted"

class Hotkey:
    def __init__(self, callback, obs_settings, _id, description_hk = ""):
        self.obs_data = obs_settings
        self.hotkey_id = obs.OBS_INVALID_HOTKEY_ID
        self.hotkey_saved_key = None
        self.callback = callback
        self._id = _id
        self.description = description_hk

        self.load_hotkey()
        self.register_hotkey()
        self.save_hotkey()

    def register_hotkey(self):
        self.hotkey_id = obs.obs_hotkey_register_frontend(
            "htk_id" + str(self._id), self.description, self.callback
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
class h: htk_copy = None  # this attribute will hold instance of Hotkey

# Exceptions
class IsNotDir(Exception): pass

def create_folder(folder_name: str) -> None:
    helpers.log("create_folder()")
    if not exists(clip_path + folder_name): mkdir(clip_path + folder_name)
    elif not isdir(clip_path + folder_name): raise IsNotDir(clip_path + folder_name)

def get_files_in_folder(path: str) -> list:
    #helpers.log("get_files_in_folder()") spamming too much
    return [ i for i in listdir(path) if isfile(path + i) ]

def sort_folder() -> None:
    helpers.log("sort_folder()")
    files: list = get_files_in_folder(clip_path)
    if len(files) != 0:
        create_folder(MISSING_FOLDER_NAME)
        for f in files: rename(clip_path + f, clip_path + MISSING_FOLDER_NAME + "\\" + f)

def get_clip_name() -> str:
    helpers.log("get_clip_name()")
    files = get_files_in_folder(clip_path)
    while len(files) == 0:
        files = get_files_in_folder(clip_path)
        sleep(0.1)
    return files[0]

def move_clip(clip_name, folder_name, timeout = 1000):
    if timeout <= 0:
        helpers.err("Couldn't move clip")
    try: rename(clip_path + clip_name, clip_path + folder_name + "\\" + clip_name)
    except PermissionError: 
        sleep(0.1)
        move_clip(clip_name, folder_name, timeout - 1)

def save_replay() -> None:
    helpers.log("save_replay()")
    sort_folder()
    if not obs.obs_frontend_replay_buffer_active(): 
        helpers.notification("WARNING Not Clipped")
        helpers.err("replay buffer not active")
    else:
        obs.obs_frontend_replay_buffer_save()
        helpers.notification("Clipped")
        
        folder_name: str = helpers.get_active_game_folder_name()
        clip_name: str = get_clip_name()
        create_folder(folder_name)
        move_clip(clip_name, folder_name)

        helpers.log(f"New clip in: { folder_name }")

def cb_hk_save_replay(pressed) -> None:
    helpers.log("cb_hk_save_replay: " + str(pressed))
    if pressed: save_replay()

def cb_get_data(props, prop) -> None:
    helpers.log("cb_get_data")
    helpers.csv_load()

def cb_save_replay(props, prop) -> None:
    helpers.log("cb_save_replay")
    save_replay()

def get_active_window_info():
    return f"{GetWindowText(GetForegroundWindow())}:{GetClassName(GetForegroundWindow())}:{helpers.get_active_process()}"
     
def test():
    sleep(3)
    for source in obs.obs_enum_sources():
        source_name = obs.obs_source_get_name(source)
        
        if source_name == game_capture_source_name_video:
            source_settings_video = obs.obs_source_get_settings(source)
            source_settings_readable_video = json.loads(obs.obs_data_get_json(source_settings_video))
        if source_name == game_capture_source_name_audio:
            source_settings_audio = obs.obs_source_get_settings(source)
    print(source_settings_readable_video)
    update_game_capture_audio_source()
    for source in obs.obs_enum_sources():
        source_name = obs.obs_source_get_name(source)
        
        if source_name == game_capture_source_name_video:
            source_settings_video = obs.obs_source_get_settings(source)
            source_settings_readable_video = json.loads(obs.obs_data_get_json(source_settings_video))
        if source_name == game_capture_source_name_audio:
            source_settings_audio = obs.obs_source_get_settings(source)
    print(source_settings_readable_video)



def cb_test(props, prop) -> None:
    helpers.log("cb_test")
    test()

def update_game_capture_audio_source() -> None:
    for source in obs.obs_enum_sources():
        source_name = obs.obs_source_get_name(source)
        
        if source_name == game_capture_source_name_video:
            source_settings_video = obs.obs_source_get_settings(source)
            #source_settings_readable_video = json.loads(obs.obs_data_get_json(source_settings_video))
        if source_name == game_capture_source_name_audio:
            source_settings_audio = obs.obs_source_get_settings(source)
    
    #obs.obs_data_set_string(source_settings_audio, "window", source_settings_readable_video["window"])
    obs.obs_data_set_string(source_settings_video, "window", f"{get_active_window_info()}")
    obs.obs_data_set_string(source_settings_audio, "window", f"{get_active_window_info()}")
    
    obs.obs_source_update(source, source_settings_video)
    obs.obs_source_update(source, source_settings_audio)


def capture_sound_of_game() -> None:
    helpers.log("capture_sound_of_game()")
    programs = helpers.csv_load()
    active_game = None
    while True:
        active_process = helpers.get_active_process()
        active_program = helpers.get_program_by_process(active_process, programs)
        if (active_game == None) and (active_program.is_game):
            active_game = active_program
            # hotkey capture video game capture
            sleep(5)
            update_game_capture_audio_source()
        elif (active_game != None) and (not helpers.process_active(active_game.process)):
            active_game = None
        sleep(30)

# API
def script_load(settings) -> None:
    helpers.log("script_load()")
    h1.htk_copy = Hotkey(cb_hk_save_replay, settings, "hk_clip", "Clip Replay Buffer and sort into folder")
    Thread(target=capture_sound_of_game)

# API
def script_save(settings) -> None:
    helpers.log("script_save()")
    h1.htk_copy.save_hotkey()

# API
# Description displayed in the Scripts dialog window
def script_description() -> str: return "OBS Clipping Script"

# API
def script_defaults(settings) -> None:
    helpers.log("script_defaults()")
    
    global enabled, debug, clip_path, game_capture_source_name_video, game_capture_source_name_audio

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_bool(settings, "debug", debug)
    obs.obs_data_set_default_string(settings, "clip_path", clip_path)
    obs.obs_data_set_default_string(settings, "game_capture_source_name_video", game_capture_source_name_video)
    obs.obs_data_set_default_string(settings, "game_capture_source_name_audio", game_capture_source_name_audio)
    
    if not exists(Path.home()): raise Exception('Home path "' + str(Path.home()) + '" doesn\'t exist')
    elif not isdir(Path.home()): raise IsNotDir('Home path "' + str(Path.home()) + '" is not a dir')

    if not exists(videos_path): mkdir(videos_path)
    elif not isdir(videos_path): raise IsNotDir(videos_path)

    if not exists(clip_path): mkdir(clip_path)
    elif not isdir(clip_path): raise IsNotDir(clip_path)
    helpers.log(
f"""
Enabled: {obs.obs_data_get_bool(settings, 'enabled')}
Debug: {obs.obs_data_get_bool(settings, 'debug')}
""")

# API
# Run on every script update
# Called when the script’s settings (if any) have been changed by the user.
def script_update(settings) -> None:
    helpers.log("script_update()")

    global enabled, debug, clip_path, game_capture_source_name_video, game_capture_source_name_audio

    if debug and not obs.obs_data_get_bool(settings, "debug"): helpers.log("Debug stop")
    elif not debug and obs.obs_data_get_bool(settings, "debug"): helpers.log("Debug start")

    debug = obs.obs_data_get_bool(settings, "debug")
    enabled = obs.obs_data_get_bool(settings, "enabled")
    clip_path = obs.obs_data_get_string(settings, "clip_path") + "\\"
    game_capture_source_name_video = obs.obs_data_get_string(settings, "game_capture_source_name_video")
    game_capture_source_name_audio = obs.obs_data_get_string(settings, "game_capture_source_name_audio")


# API
# Script view under the description
def script_properties():
    helpers.log("script_properties()")
    global clip_path
    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "Enabled")
    obs.obs_properties_add_bool(props, "debug", "Debug")
    obs.obs_properties_add_button(props, "btn_get_data", "Refresh Data", cb_get_data)
    obs.obs_properties_add_button(props, "btn_save_replay", "Save Replay", cb_save_replay)
    obs.obs_properties_add_path(props, "clip_path", "Clips Path", obs.OBS_PATH_DIRECTORY, "", clip_path)
    obs.obs_properties_add_text(props, "game_capture_source_name_video", "Game Capture Source Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "game_capture_source_name_audio", "Game Capture Audio Source Name", obs.OBS_TEXT_DEFAULT)


    obs.obs_properties_add_button(props, "btn_cb_test", "Test", cb_test)
    #obs.obs_properties_add_button(props, "btn_test", "Test", cb_test)
    #obs.obs_properties_add_list(props, "programs", "Programs", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    #obs.obs_properties_add_list(props, "folder", "Folder", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    #obs.obs_properties_add_bool(props, "is_game", "Is it a game")

    return props

# Hotkey instance
h1: h = h()