from mido.backends.backend import Backend
from mido.messages.messages import Message
from mido.backends.rtmidi import Input

backend = Backend()

print(backend.get_input_names())


dorian = {
    # 2 4 5 7 9 11 12
    0: 2, # C
    1: 0,
    2: 4, # D
    3: 0,
    4: 5, # E
    5: 7, # F
    6: 0,
    7: 9, # G
    8: 0,
    9: 11, # A
    10: 0,
    11: 12 # B
}


def open_inst(index, is_out):
    names = backend.get_output_names() if is_out else backend.get_input_names()
    name = names[index]
    print("opening", '[out]' if is_out else ' [in]', name)
    if is_out:
        return backend.open_output(name)
    else:
        return backend.open_input(name)


vo = open_inst(0, is_out=True)

with open_inst(1, is_out=False) as vi:
    for note_in in vi:
        print('[input]', vi, note_in)
        if note_in.type in ['note_on', 'note_off']:
            octave = int(note_in.note / 12)
            key = note_in.note % 12
            # print(type(octave * 12 + dorian[key]), type(dorian[key]), type(octave), "yo")
            note_out = Message(note_in.type,
                               note=octave * 12 + dorian[key],
                               velocity=note_in.velocity,
                               time=note_in.time,
                               channel=10)  # this is Ableton's channel # minus 1
            vo.send(note_out)
        else:
            vo.send(note_in)
