#import gevent
#from gevent import monkey
#monkey.patch_all()

import time
from mido.backends.backend import Backend
from mido.messages.messages import Message
from mido.backends.rtmidi import Input, Output
from pynput import keyboard
import requests
import threading


# SEND_KEYS = ['command', 'option', 'ctrl', '0']
# SEND_KEYS2 = [keyboard.Key.cmd, keyboard.Key.alt, keyboard.Key.ctrl, '1']

my_keyboard = keyboard.Controller()


def on_hotkey():
    print("LISTENER: HOT KEY DETECTED!")


def run_hotkey_listener(block=False):
    listener = keyboard.GlobalHotKeys({
        # for some reason, letter-based hot keys don't work, only number-based ones
        # can do multiple sets here...
        '<cmd>+<alt>+<ctrl>+1': on_hotkey,
    })
    listener.start()
    print("Hotkey listener started...")
    if block:
        listener.join()


run_hotkey_listener()
# threading.Thread(target=run_hotkey_listener, kwargs=dict(block=True)).start()


backend = Backend()


def call_obs_api(command='pause-toggle'):
    url = f'http://localhost:28000/{command}'
    print("Calling:", url)
    response = requests.get(url).json()
    print("OBS RESPONSE:", response)


class Inst:
    def __init__(self, index, is_out):
        self.is_out = is_out
        self.index = index

        names = backend.get_output_names() if self.is_out else backend.get_input_names()
        self.name = names[self.index]
        print(f"opening index={index}", '[out]' if self.is_out else ' [in]', self.name)
        if self.is_out:
            self.output = backend.open_output(self.name)
        else:
            self.input = backend.open_input(self.name, callback=self.input_callback)

    def input_callback(self, note_in):
        if note_in.type != 'clock':
            print('[input]', self, note_in, f'/ real_channel={note_in.channel + 1}' if hasattr(note_in, 'channel') else '')
            if note_in.type == 'control_change' and note_in.control == 65 and note_in.value == 0:
                # Add permissions for iTerm2: https://stackoverflow.com/questions/54973241/applescript-application-is-not-allowed-to-send-keystrokes
                print("Special key pressed!")

                threading.Thread(target=call_obs_api, kwargs=dict(command='pause-toggle'), daemon=True).start()
                print("NEXT....")

                """
                pyautogui.hotkey(*SEND_KEYS, interval=0.1)
                #"""

                """
                for key in SEND_KEYS:
                    pyautogui.keyDown(key)
                for key in reversed(SEND_KEYS):
                    pyautogui.keyUp(key)
                #"""

                """
                for key in SEND_KEYS2:
                    my_keyboard.press(key)
                for key in reversed(SEND_KEYS2):
                    my_keyboard.release(key)
                #"""

        """
        if note_in.type in ['note_on', 'note_off']:
            octave = int(note_in.note / 12)
            key = note_in.note % 12
        #"""

    def __repr__(self):
        return f'<Inst name={self.name}>'


input_names = backend.get_input_names()
output_names = backend.get_output_names()

print("All readable inputs:", input_names)
for i in range(len(input_names)):
    Inst(index=i, is_out=False)

print("All writable outputs:", output_names)
#for i in range(len(output_names)):
#    Inst(index=i, is_out=True)

while True:
    time.sleep(100)
