import time
from mido.backends.backend import Backend
from mido.messages.messages import Message
from mido.backends.rtmidi import Input, Output


backend = Backend()


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
        if note_in.type in ['note_on', 'note_off']:
            octave = int(note_in.note / 12)
            key = note_in.note % 12

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

