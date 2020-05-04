# https://github.com/patrickkidd/pyrtmidi

import sys
from pynput import keyboard
import os
import time
from rtmidi import RtMidiIn
import requests
import logging
import threading


class Listener:
    def __init__(self, port_index):
        self.device = RtMidiIn()
        self.device_name = self.device.getPortName(port_index)
        print("[Device]", self.device_name)
        self.device.openPort(port_index)
        self.device.ignoreTypes(True, False, True) # bool midiSysex=true, bool midiTime=true, bool midiSense=true
        self.device.setCallback(self.on_message)

    def on_message(self, msg):
        try:
            channel = msg.getChannel()
            if msg.isNoteOn():
                note = msg.getNoteNumber()
                print(f'[{self.device_name}] ch={channel} n={note}/{msg.getMidiNoteName(note)} v={msg.getVelocity()}')
            elif msg.isNoteOff():
                note = msg.getNoteNumber()
                print(f'[{self.device_name}] ch={channel} n={note}/{msg.getMidiNoteName(note)} v=0')
            elif msg.isController():
                print(f'[{self.device_name}] ch={channel} cc={msg.getControllerNumber()} v={msg.getControllerValue()}')
            else:
                print("Unknown message:", msg)
            if msg.getControllerNumber() == 65 and msg.getControllerValue() == 0:
                call_obs_api()
        except Exception as e:
            logging.exception(e)


def call_obs_api(command='pause-toggle'):
    def __thread():
        try:
            url = f'http://localhost:28000/{command}'
            # print("Calling:", url)
            response = requests.get(url).json()
            print("OBS RESPONSE:", response)
            #if response['msg']: os.system(f"say '[[volm 0.10]] {response['msg']}'")
        except Exception as e:
            logging.exception(e)
    threading.Thread(target=__thread, kwargs={}, daemon=True).start()


def on_volume_up():
    print("[Hotkey] Volume up")
    call_obs_api()


def on_hotkey():
    print("[Hotkey] Hot key detected")
    call_obs_api()


def run_hotkey_listener(block=False):
    # volume_key = [keyboard.Key.media_volume_up]
    key_map = {
        '<cmd>+<alt>+<ctrl>+1': on_hotkey,
    }
    if len(sys.argv) >= 2 and sys.argv[1] == 'v':
        key_map['<media_volume_up>'] = on_volume_up
    listener = keyboard.GlobalHotKeys(key_map)
    listener.start()
    print("[Hotkey] Listener started on:", ', '.join(key_map.keys()))
    if block:
        listener.join()


if __name__ == '__main__':
    run_hotkey_listener(False)

    dev = RtMidiIn()
    collectors = []
    for i in range(dev.getPortCount()):
        Listener(i)

    while True:
        # print("HI")
        time.sleep(100)
        #gevent.sleep(1.0)
        #gevent.spawn_later(0.1, call_obs_api)
