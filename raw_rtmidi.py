import time
from rtmidi import MidiIn, MidiOut

midi_in = MidiIn()
midi_out = MidiOut()

in_ports = midi_in.get_ports()
out_ports = midi_out.get_ports()

print("IN ports:", in_ports)
print("OUT ports:", out_ports)

def callback(msg_data, data):
    print(msg_data, data)

midi_in.open_port(1)
midi_in.set_callback(callback)

print("Press any midi key...")
time.sleep(100)
