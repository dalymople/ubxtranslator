"""A lightweight package for parsing uBlox UBX messages"""

import struct
from collections import namedtuple


class LightParser:
    """A lightweight message parser"""
    PREFIX = bytes((0xB5, 0x62))

    def __init__(self, port):
        self._message_store = {}
        self._input_buffer = b''
        self._port = port

    def register_msg_type(self, class_id: int, msg_id: int, name: str, msg_format: str, *fields):
        """Register a packet with the message store."""
        if class_id not in self._message_store:
            self._message_store[class_id] = {}

        nt = namedtuple(name, [*fields])

        self._message_store[class_id][msg_id] = dict(fmt=msg_format, nt=nt)

    def receive_message(self) -> namedtuple:
        """Receive a message and return as a namedtuple.
        raise IOError or ValueError on errors.
        """
        while True:
            # Search for the prefix
            buff = self._port.read_until(expected=self.PREFIX)
            if buff[-2:] != self.PREFIX:
                continue

        # read the first four bytes
        buff = self._port.read(4)

        if len(buff) != 4:
            raise IOError("A port read returned {} bytes, expected 4 bytes".format(len(buff)))

        # convert them into the packet descriptors
        msg_cls, msg_id, length = struct.unpack('BBH', buff)

        # check the packet validity
        if msg_cls not in self._message_store:
            raise ValueError("Received unsupported message class of {:x}".format(msg_cls))

        if msg_id not in self._message_store[msg_cls]:
            raise ValueError("Received unsupported message id of {:x} in class {:x}".format(
                msg_id, msg_cls))

        # Read the payload
        buff += self._port.read(length)
        if len(buff) != (4 + length):
            raise IOError("A port read returned {} bytes, expected {} bytes".format(
                len(buff), 4 + length))

        # Read the checksum
        checksum_sup = self._port.read(2)
        if len(checksum_sup) != 2:
            raise IOError("A port read returned {} bytes, expected 2 bytes".format(len(buff)))

        checksum_cal = self._generate_fletcher_checksum(buff)
        if checksum_cal != checksum_sup:
            raise ValueError("Checksum mismatch. Calculated {:x} {:x}, received {:x} {:x}".format(
                checksum_cal[0], checksum_cal[1], checksum_sup[0], checksum_sup[1]
            ))

        # Retrieve the descriptors
        nt = self._message_store[msg_cls][msg_id]['nt']
        fmt = self._message_store[msg_cls][msg_id]['fmt']

        # Return the correct namedtuple
        return nt(*struct.unpack(fmt, buff[4:]))

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
