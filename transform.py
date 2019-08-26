import mido


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
    name = mido.get_output_names()[index]
    print("opening", '[out]' if is_out else ' [in]', name)
    if is_out:
        return mido.open_output(name)
    else:
        return mido.open_input(name)


vo = open_inst(0, is_out=True)

with open_inst(1, is_out=False) as vi:
    for mi in vi:
        print(mi)
        if mi.type in ['note_on', 'note_off']:
            octave = int(mi.note / 12)
            key = mi.note % 12
            # print(type(octave * 12 + dorian[key]), type(dorian[key]), type(octave), "yo")
            mo = mido.Message(mi.type,
                              note=octave * 12 + dorian[key],
                              velocity=mi.velocity,
                              time=mi.time)
            vo.send(mo)
        else:
            print(mi.type)
            vo.send(mi)
