import time
from rtmidi import MidiIn, MidiOut
from mido.messages.messages import *


class Message(BaseMessage):
    def __init__(self, type, **args):
        msgdict = make_msgdict(type, args)
        if type == 'sysex':
            msgdict['data'] = SysexData(convert_py2_bytes(msgdict['data']))
        check_msgdict(msgdict)
        vars(self).update(msgdict)

    def copy(self, **overrides):
        """Return a copy of the message.

        Attributes will be overridden by the passed keyword arguments.
        Only message specific attributes can be overridden. The message
        type can not be changed.
        """
        if not overrides:
            # Bypass all checks.
            msg = self.__class__.__new__(self.__class__)
            vars(msg).update(vars(self))
            return msg

        if 'type' in overrides and overrides['type'] != self.type:
            raise ValueError('copy must be same message type')

        if 'data' in overrides:
            overrides['data'] = bytearray(overrides['data'])

        msgdict = vars(self).copy()
        msgdict.update(overrides)
        check_msgdict(msgdict)
        return self.__class__(**msgdict)

    @classmethod
    def from_bytes(cl, data, time=0):
        """Parse a byte encoded message.

        Accepts a byte string or any iterable of integers.

        This is the reverse of msg.bytes() or msg.bin().
        """
        msg = cl.__new__(cl)
        msgdict = decode_message(data, time=time)
        if 'data' in msgdict:
            msgdict['data'] = SysexData(msgdict['data'])
        vars(msg).update(msgdict)
        return msg

    @classmethod
    def from_hex(cl, text, time=0, sep=None):
        """Parse a hex encoded message.

        This is the reverse of msg.hex().
        """
        # bytearray.fromhex() is a bit picky about its input
        # so we need to replace all whitespace characters with spaces.
        text = re.sub(r'\s', ' ', text)

        if sep is not None:
            # We also replace the separator with spaces making sure
            # the string length remains the same so char positions will
            # be correct in bytearray.fromhex() error messages.
            text = text.replace(sep, ' ' * len(sep))

        return cl.from_bytes(bytearray.fromhex(text), time=time)

    @classmethod
    def from_str(cl, text):
        """Parse a string encoded message.

        This is the reverse of str(msg).
        """
        return cl(**str2msg(text))

    def __len__(self):
        if self.type == 'sysex':
            return 2 + len(self.data)
        else:
            return SPEC_BY_TYPE[self.type]['length']

    def __str__(self):
        return msg2str(vars(self))

    def __repr__(self):
        return '<message {}>'.format(str(self))

    def _setattr(self, name, value):
        if name == 'type':
            raise AttributeError('type attribute is read only')
        elif name not in vars(self):
            raise AttributeError('{} message has no '
                                 'attribute {}'.format(self.type,
                                                       name))
        else:
            check_value(name, value)
            if name == 'data':
                vars(self)['data'] = SysexData(value)
            else:
                vars(self)[name] = value

    __setattr__ = _setattr

    def bytes(self):
        """Encode message and return as a list of integers."""
        return encode_message(vars(self))


midi_in = MidiIn()
midi_out = MidiOut()

in_ports = midi_in.get_ports()
out_ports = midi_out.get_ports()

print("IN ports:", in_ports)
print("OUT ports:", out_ports)

def callback(msg_data, data):
    print(msg_data, data, Message.from_bytes(msg_data[0]))

midi_in.open_port(1)
midi_in.set_callback(callback)

print("Press any midi key...")
while True:
    time.sleep(100)

