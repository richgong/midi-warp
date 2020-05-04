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


class Collector(threading.Thread):
    def __init__(self, device, port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.quit = False

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
            if self.quit:
                return
            msg = self.device.getMessage()
            if msg:
                print_message(msg, self.portName)




def call_obs_api(command='pause-toggle'):
    url = f'http://localhost:28000/{command}'
    print("Calling:", url)
    response = requests.get(url).json()
    print("OBS RESPONSE:", response)
    os.system(f"say '{response['msg']}'")

dev = RtMidiIn()
collectors = []
for i in range(dev.getPortCount()):
    device = RtMidiIn()
    print('OPENING',dev.getPortName(i))
    collector = Collector(device, i)
    collector.start()
    collectors.append(collector)



while True:
    # print("HI")
    time.sleep(100)
    #gevent.sleep(1.0)
    #gevent.spawn_later(0.1, call_obs_api)

