from pynput import keyboard


from listen import call_obs_api


def on_volume_up():
    print("GOT: VOLUME UP")
    call_obs_api()

# volume_key = [keyboard.Key.media_volume_up]

def run_hotkey_listener(block=False):
    listener = keyboard.GlobalHotKeys({
        '<media_volume_up>': on_volume_up,
    })
    listener.start()
    print("Hotkey listener started...")
    if block:
        listener.join()


run_hotkey_listener(True)
