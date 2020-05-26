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


my_keyboard = keyboard.Controller()
STOP_TIMER = None
RECORDING_STATE = 0
PLAYING_STATE = False
HOTKEY_LAST_TIME = 0
VIRTUAL_OUTPUT_NAME = 'IAC Driver Gong TheGongPort'
VIRTUAL_OUTPUT = None


def say(s):
    cmd = f"say '[[volm 0.50]] {s}'"
    logging.info(f"Running cmd: {cmd}")
    os.system(cmd)
    return s


def type_key(key):
    my_keyboard.press(key)
    my_keyboard.release(key)


def throttle():
    global HOTKEY_LAST_TIME
    now = time.time()
    delta = now - HOTKEY_LAST_TIME
    HOTKEY_LAST_TIME = now
    return delta < 1


def smart_start(send_midi=None):
    global RECORDING_STATE, PLAYING_STATE, VIRTUAL_OUTPUT
    # no need to wait, unlike for stop
    if VIRTUAL_OUTPUT:
        if send_midi == 'record':
            RECORDING_STATE = 2
            VIRTUAL_OUTPUT.send_cc_momentary(8, 68, 'RECORD NEW')
            VIRTUAL_OUTPUT.send_cc_raw(8, 64, 127, 'RECORD START')
        elif send_midi == 'play':
            PLAYING_STATE = 1
            VIRTUAL_OUTPUT.send_cc_momentary(8, 66, 'PLAY')

    if throttle():
        return
    call_obs_api('start')


def smart_stop(send_midi=False):
    global RECORDING_STATE, PLAYING_STATE, VIRTUAL_OUTPUT, STOP_TIMER
    if VIRTUAL_OUTPUT:
        if send_midi == 'record':
            if RECORDING_STATE == 2:
                VIRTUAL_OUTPUT.send_cc_raw(8, 64, 0, 'RECORD STOP')
            elif RECORDING_STATE == 1:
                VIRTUAL_OUTPUT.send_cc_momentary(8, 67, 'PLAY STOP')
            RECORDING_STATE -= 1
        elif send_midi == 'play':
            PLAYING_STATE = 0
            VIRTUAL_OUTPUT.send_cc_momentary(8, 67, 'PLAY STOP')
    if throttle():
        return
    if STOP_TIMER:
        return
    STOP_TIMER = threading.Timer(4.0, call_obs_api, ('stop',))
    STOP_TIMER.start()


def smart_toggle():
    if throttle():
        return
    call_obs_api()


class Writer:
    def __init__(self, port_index):
        self.device = RtMidiOut()
        self.device_name = self.device.getPortName(port_index)
        print("[Device] Output:", self.device_name)
        self.device.openPort(port_index)

    def send_cc_momentary(self, channel, cc, label=None):
        if label:
            print('[Virtual] send_cc_momentary:', label)
        self.send_cc_raw(channel, cc, 127)
        self.send_cc_raw(channel, cc, 0)

    def send_cc_raw(self, channel, cc, v, label=None):
        if label:
            print('[Virtual] send_cc_raw:', label)
        # see: https://github.com/patrickkidd/pyrtmidi/blob/master/rtmidi/randomout.py
        msg = MidiMessage.controllerEvent(channel, cc, v)
        self.device.sendMessage(msg)


class Reader:
    def __init__(self, port_index):
        self.device = RtMidiIn()
        self.device_name = self.device.getPortName(port_index)
        print("[Device] Input:", self.device_name)
        self.device.openPort(port_index)
        self.device.ignoreTypes(False, True, False) # midiSysex, midiTime, midiSense
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
                        smart_start(send_midi=None)
                    else:
                        smart_stop(send_midi=None)

        except Exception as e:
            logging.exception(e)


def call_obs_api(command='pause-toggle'):
    global STOP_TIMER
    if STOP_TIMER:
        STOP_TIMER.cancel()
        STOP_TIMER = None

    def __thread():
        try:
            url = f'http://localhost:28000/{command}'
            print("[OBS]", command)
            response = requests.get(url).json()
            print("[OBS] Reponse:", response)
            global RECORDING_STATE
        except Exception as e:
            print(f"[OBS] Error: {e.__class__.__name__}")
    threading.Thread(target=__thread, kwargs={}, daemon=True).start()


def hotkey_listener(key_name):
    def __listener():
        print(f"[Hotkey] Detected: <{key_name}>")
        if key_name == 'volume':
            print('[Hotkey] VOLUME DOWN')
            type_key(keyboard.Key.media_volume_down)
        if ARGS.send_midi_record:
            global RECORDING_STATE
            if RECORDING_STATE:
                smart_stop(send_midi='record')
            else:
                smart_start(send_midi='record')
        elif ARGS.send_midi_play:
            global PLAYING_STATE
            if PLAYING_STATE:
                smart_stop(send_midi='play')
            else:
                smart_start(send_midi='play')
        else:
            smart_toggle()
    return __listener


def listen_to_hot_keys(block=False):
    key_map = {
        '<cmd>+<alt>+<ctrl>+8': hotkey_listener('8'),
    }
    if ARGS.volume:
        key_map['<media_volume_up>'] = hotkey_listener('volume')
    if ARGS.accent or ARGS.send_midi_record or ARGS.send_midi_play:
        key_map['`'] = hotkey_listener('accent')
    listener = keyboard.GlobalHotKeys(key_map)
    listener.start()
    print("[Hotkey] Waiting for:", ', '.join(key_map.keys()))
    if block:
        listener.join()


def listen_to_all_keys():
    def __on_press(key):
        print(f'{key} pressed')

    def __on_release(key):
        print(f'{key} released')

    listener = keyboard.Listener(on_press=__on_press, on_release=__on_release)
    listener.start()
    listener.join()


if __name__ == '__main__':
    say("Listening.")  # Shows that speech synthesis isn't blocked.
    parser = argparse.ArgumentParser(description="A MIDI/Keyboard signal router.")
    parser.add_argument('-v', '--volume', dest="volume",
                        help='Listen for volume key.', action='store_true', required=False)
    parser.add_argument('-a', '--accent', dest="accent",
                        help='Listen for accent key.', action='store_true', required=False)
    parser.add_argument('-r', '--record', dest="send_midi_record",
                        help='Send synthetic MIDI record/stop/new', action='store_true', required=False)
    parser.add_argument('-p', '--play', dest="send_midi_play",
                        help='Send synthetic MIDI play/stop', action='store_true', required=False)
    ARGS = parser.parse_args()

    #listen_to_all_keys()
    listen_to_hot_keys()

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
