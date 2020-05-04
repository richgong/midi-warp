# https://github.com/patrickkidd/pyrtmidi


#import gevent
#from gevent import monkey
#monkey.patch_all()
import os
import time
from rtmidi import RtMidiIn
import requests
import threading


def print_message(midi, port):
    if midi.isNoteOn():
        print('%s: ON: ' % port, midi.getMidiNoteName(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('%s: OFF:' % port, midi.getMidiNoteName(midi.getNoteNumber()))
    elif midi.isController():
        print('%s: CONTROLLER' % port, midi.getControllerNumber(), midi.getControllerValue())
        if midi.getControllerNumber() == 65 and midi.getControllerValue() == 0:
            call_obs_api()


class Collector:
    def __init__(self, device, port):
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True) # bool midiSysex=true, bool midiTime=true, bool midiSense=true
        self.device.setCallback(self.onMessage)

    def onMessage(self, msg):
        print_message(msg, self.portName)


def call_obs_api(command='pause-toggle'):
    url = f'http://localhost:28000/{command}'
    print("Calling:", url)
    response = requests.get(url).json()
    print("OBS RESPONSE:", response)
    if response['msg']:
        os.system(f"say '[[volm 0.10]] {response['msg']}'")


dev = RtMidiIn()
collectors = []
for i in range(dev.getPortCount()):
    device = RtMidiIn()
    print('OPENING',dev.getPortName(i))
    collector = Collector(device, i)



while True:
    # print("HI")
    time.sleep(100)
    #gevent.sleep(1.0)
    #gevent.spawn_later(0.1, call_obs_api)

