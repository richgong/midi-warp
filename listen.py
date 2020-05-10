# https://github.com/patrickkidd/pyrtmidi

import argparse
import sys
from pynput import keyboard
import os
import time
from rtmidi import RtMidiIn, RtMidiOut, MidiMessage
import requests
import logging
import threading
import time


PAUSE_TIMER = None
RECORDING_STATE = 0
HOTKEY_LAST_TIME = 0
VIRTUAL_OUTPUT_NAME = 'IAC Driver Gong TheGongPort'
VIRTUAL_OUTPUT = None


def throttle():
    global HOTKEY_LAST_TIME
    now = time.time()
    delta = now - HOTKEY_LAST_TIME
    HOTKEY_LAST_TIME = now
    return delta < 1


def smart_continue(send_midi=False):
    global RECORDING_STATE, VIRTUAL_OUTPUT
    # no need to wait, unlike pause
    if send_midi and VIRTUAL_OUTPUT:
        VIRTUAL_OUTPUT.send_cc_momentary(8, 68) # record new
        VIRTUAL_OUTPUT.send_cc(8, 64, 127) # start recording
        RECORDING_STATE = 2
    if throttle():
        return
    call_obs_api('continue')


def smart_pause(send_midi=False):
    global RECORDING_STATE, VIRTUAL_OUTPUT, PAUSE_TIMER
    if send_midi and VIRTUAL_OUTPUT and RECORDING_STATE > 0:
        if RECORDING_STATE == 2:
            VIRTUAL_OUTPUT.send_cc(8, 64, 0) # stop recording, but hear playback
        elif RECORDING_STATE == 1:
            VIRTUAL_OUTPUT.send_cc_momentary(8, 67) # stop playing
        RECORDING_STATE -= 1
    if throttle():
        return
    if PAUSE_TIMER:
        return
    PAUSE_TIMER = threading.Timer(4.0, call_obs_api, ('pause',))
    PAUSE_TIMER.start()


class Writer:
    def __init__(self, port_index):
        self.device = RtMidiOut()
        self.device_name = self.device.getPortName(port_index)
        print("[Device] Output:", self.device_name)
        self.device.openPort(port_index)

    def send_cc_momentary(self, channel, cc):
        self.send_cc(channel, cc, 127)
        self.send_cc(channel, cc, 0)

    def send_cc(self, channel, cc, v):
        # see: https://github.com/patrickkidd/pyrtmidi/blob/master/rtmidi/randomout.py
        msg = MidiMessage.controllerEvent(channel, cc, v)
        self.device.sendMessage(msg)


class Reader:
    def __init__(self, port_index):
        self.device = RtMidiIn()
        self.device_name = self.device.getPortName(port_index)
        print("[Device] Input:", self.device_name)
        self.device.openPort(port_index)
        self.device.ignoreTypes(False, False, False) # midiSysex, midiTime, midiSense
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
                print(f'[{self.device_name}] other: {msg}')
            if msg.isController():
                cc = msg.getControllerNumber()
                v = msg.getControllerValue()
                if cc == 64 and self.device_name != VIRTUAL_OUTPUT_NAME:
                    if v > 0:
                        smart_continue(send_midi=False)
                    else:
                        smart_pause(send_midi=False)

        except Exception as e:
            logging.exception(e)


def call_obs_api(command='pause-toggle'):
    global PAUSE_TIMER
    if PAUSE_TIMER:
        PAUSE_TIMER.cancel()
        PAUSE_TIMER = None

    def __thread():
        try:
            url = f'http://localhost:28000/{command}'
            print("[OBS] Send:", command)
            response = requests.get(url).json()
            print("[OBS] Reponse:", response)
            global RECORDING_STATE
        except Exception as e:
            print(f"[OBS] Error: {e.__class__.__name__}")
    threading.Thread(target=__thread, kwargs={}, daemon=True).start()


def hotkey_listener(key):
    def __listener():
        print(f"[Hotkey] Detected: {key}")
        global RECORDING_STATE
        if RECORDING_STATE:
            smart_pause(send_midi=ARGS.send_midi)
        else:
            smart_continue(send_midi=ARGS.send_midi)
    return __listener


def run_hotkey_listener(block=False):
    # volume_key = [keyboard.Key.media_volume_up]
    key_map = {
        '<cmd>+<alt>+<ctrl>+8': hotkey_listener('<8>'),
    }
    if ARGS.volume:
        key_map['<media_volume_up>'] = hotkey_listener('<volume>')
    if ARGS.accent or ARGS.send_midi:
        key_map['`'] = hotkey_listener('<accent>')
    listener = keyboard.GlobalHotKeys(key_map)
    listener.start()
    print("[Hotkey] Waiting for:", ', '.join(key_map.keys()))
    if block:
        listener.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A MIDI/Keyboard signal router.")
    parser.add_argument('-v', '--volume', dest="volume",
                        help='Listen for volume key.', action='store_true', required=False)
    parser.add_argument('-a', '--accent', dest="accent",
                        help='Listen for accent key.', action='store_true', required=False)
    parser.add_argument('-m', '--midi', dest="send_midi",
                        help='Send synthetic MIDI sustain', action='store_true', required=False)
    ARGS = parser.parse_args()

    run_hotkey_listener()

    for i in range(RtMidiIn().getPortCount()):
        Reader(i)

    fake_out = RtMidiOut()
    for i in range(fake_out.getPortCount()):
        if fake_out.getPortName(i) == VIRTUAL_OUTPUT_NAME:
            VIRTUAL_OUTPUT = Writer(i)


    while True:
        # print("HI")
        time.sleep(100)
        #gevent.sleep(1.0)
        #gevent.spawn_later(0.1, call_obs_api)
