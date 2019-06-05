"""The core structure definitions"""

import struct
from collections import namedtuple


class UbxMsgDef:
    """Defines a message"""
    __slots__ = ['id_', 'name', 'fields', 'nt', ]

    def __init__(self, id_: int, name: str, *fields):
        self.id_ = id_
        self.name = name.upper()
        self.fields = fields
        self.nt = namedtuple(self.name, [f.name for f in self.fields])

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.name)

    def parse(self, pavload: bytes) -> namedtuple:
        """Return a named tuple parsed from the provided payload"""
        fmt = ''.join([f.fmt for f in self.fields])
        data = struct.unpack(fmt, pavload)

        it = iter(data)
        return self.name, self.nt(**{k: v for k, v in [f.parse(it) for f in self.fields] if k is not None})


class UbxClassDef:
    """Defines a message class"""
    __slots__ = ['id_', 'name', 'messages', ]

    def __init__(self, id_: int, name: str, *messages):
        self.id_ = id_
        self.name = name.upper()

        self.messages = {}
        for msg in messages:
            self.messages[msg.id_] = msg

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.name)

    def __iter__(self):
        return self.messages.__iter__()

    def __contains__(self, item):
        return self.messages.__contains__(item)

    def __getitem__(self, item):
        try:
            return self.messages[item]
        except KeyError:
            raise ValueError("A message of id {} has not been registered within {!r}".format(
                item, self
            ))

    def register_msg_type(self, msg: UbxMsgDef):
        """Register a message type."""
        self.messages[msg.id_] = msg


class UbxParser:
    """A lightweight UBX message parser"""
    PREFIX = bytes((0xB5, 0x62))

    def __init__(self, *classes):
        self._input_buffer = b''

        self.classes = {}
        for cls_ in classes:
            self.classes[cls_.id_] = cls_

    def register_msg_cls(self, cls_: UbxClassDef):
        """Register a message  class."""
        self.classes[cls_.id_] = cls_

    def receive_from(self, stream) -> namedtuple:
        """Receive a message from a stream and return as a namedtuple.
        raise IOError or ValueError on errors.
        """
        while True:
            # Search for the prefix
            buff = stream.read_until(expected=self.PREFIX)
            if buff[-2:] != self.PREFIX:
                continue

        # read the first four bytes
        buff = stream.read(4)

        if len(buff) != 4:
            raise IOError("A stream read returned {} bytes, expected 4 bytes".format(len(buff)))

        # convert them into the packet descriptors
        msg_cls, msg_id, length = struct.unpack('BBH', buff)

        # check the packet validity
        if msg_cls not in self.classes:
            raise ValueError("Received unsupported message class of {:x}".format(msg_cls))

        if msg_id not in self.classes[msg_cls]:
            raise ValueError("Received unsupported message id of {:x} in class {:x}".format(
                msg_id, msg_cls))

        # Read the payload
        buff += stream.read(length)
        if len(buff) != (4 + length):
            raise IOError("A stream read returned {} bytes, expected {} bytes".format(
                len(buff), 4 + length))

        # Read the checksum
        checksum_sup = stream.read(2)
        if len(checksum_sup) != 2:
            raise IOError("A stream read returned {} bytes, expected 2 bytes".format(len(buff)))

        checksum_cal = self._generate_fletcher_checksum(buff)
        if checksum_cal != checksum_sup:
            raise ValueError("Checksum mismatch. Calculated {:x} {:x}, received {:x} {:x}".format(
                checksum_cal[0], checksum_cal[1], checksum_sup[0], checksum_sup[1]
            ))

        return self.classes[msg_cls][msg_id].parse(buff[4:])

    @staticmethod
    def _generate_fletcher_checksum(payload: bytes) -> bytes:
        """Return the checksum for the provided payload"""
        check_a = 0
        check_b = 0

        for char in payload:
            check_a += char
            check_a &= 0xFF

            check_b += check_a
            check_b &= 0xFF

        return bytes((check_a, check_b))
