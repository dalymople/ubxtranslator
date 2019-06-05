"""Basic unit testing of the fields module"""

import struct
import unittest
from itertools import permutations

from ubxtranslator.core import *


class PadFieldTester(unittest.TestCase):
    def test_pad(self):
        p = PadByte()
        self.assertEqual(p.fmt, 'x')

        it = iter(range(1))
        self.assertEqual(p.parse(it), (None, None))

    def test_pad_repeat(self):
        for i in range(1, 10):
            with self.subTest(repeat=i):
                p = PadByte(repeat=i)
                self.assertEqual(p.fmt, 'x' * (i + 1))

                it = iter(range(i + 1))
                self.assertEqual(p.parse(it), (None, None))


class UbxFieldTester(unittest.TestCase):
    types = {'U1': {'fmt': 'B', 'type_': int},
             'I1': {'fmt': 'b', 'type_': int},
             'U2': {'fmt': 'H', 'type_': int},
             'I2': {'fmt': 'h', 'type_': int},
             'U4': {'fmt': 'I', 'type_': int},
             'I4': {'fmt': 'i', 'type_': int},
             'R4': {'fmt': 'f', 'type_': float},
             'R8': {'fmt': 'd', 'type_': float},
             'C': {'fmt': 'c', 'type_': lambda x: bytes([x])},
             }

    def test_ubx_field(self):
        for k, v in self.types.items():
            with self.subTest(type_=k):
                f = Field('TEST', k)
                self.assertEqual(f.fmt, v['fmt'])

                value = v['type_'](0x0F)
                packet = struct.pack(v['fmt'], value)

                self.assertEqual(f.parse(iter(struct.unpack(f.fmt, packet))), ('TEST', value))

    def test_ubx_field_repeat(self):
        for i in range(1, 10):
            for k, v in self.types.items():
                with self.subTest(repeat=i, type_=k):
                    f = Field('TEST', k, repeat=i)
                    self.assertEqual(f.fmt, v['fmt'] * (i + 1))

                    value = [v['type_'](0x0F) for _ in range(i + 1)]
                    packet = struct.pack(f.fmt, *value)

                    self.assertEqual(f.parse(iter(struct.unpack(f.fmt, packet))), ('TEST', value))

    def test_ubx_field_error(self):
        with self.assertRaises(ValueError):
            f = Field('TEST', 'U8')


class UbxBitSubFieldTester(unittest.TestCase):
    def test_bit_subfield(self):
        values = [x for x in range(-1, (4 * 8) + 2)]

        for start, stop in permutations(values, 2):
            with self.subTest(start=start, stop=stop):
                if start < 0 or start > stop or stop > 4 * 8:
                    with self.assertRaises(ValueError):
                        _ = Flag('TEST', start, stop)

                else:
                    b = Flag('TEST', start, stop)

                    mask = 0x00
                    for i in range(start, stop):
                        mask |= 0x01 << i

                    self.assertEqual(b.parse(0xFFFFFFFF), ('TEST', mask >> start))
                    self.assertEqual(b.parse(0x0), ('TEST', 0))


class UbxBitFieldTester(unittest.TestCase):
    def test_bitfield(self):
        with self.assertRaises(ValueError):
            _ = BitField('TEST', 'X8', subfields=[
                Flag('S1', 0, 8)
            ])

        for i in range(1, 16):
            with self.subTest(case='field width', stop=i):
                if i > 8:
                    with self.assertRaises(ValueError):
                        _ = BitField('TEST', 'X1', subfields=[
                            Flag('S1', 0, i)
                        ])

                else:
                    _ = BitField('TEST', 'X1', subfields=[
                        Flag('S1', 0, i)
                    ])

        x1 = BitField('TEST', 'X1', subfields=[
            Flag('S1', 0, 4),
            Flag('S2', 4, 8),
        ])

        x2 = BitField('TEST', 'X2', subfields=[
            Flag('S1', 0, 4),
            Flag('S2', 4, 8),
        ])

        x4 = BitField('TEST', 'X4', subfields=[
            Flag('S1', 0, 4),
            Flag('S2', 4, 8),
        ])

        for value in range(0, 0xFF):
            with self.subTest(case='operation', value=value):
                packet = struct.pack(x1.fmt, value)
                name, resp = x1.parse(iter(struct.unpack(x1.fmt, packet)))
                self.assertEqual(resp.S1, value & 0x0F)
                self.assertEqual(resp.S2, (value & 0xF0) >> 4)

                packet = struct.pack(x2.fmt, value)
                name, resp = x2.parse(iter(struct.unpack(x2.fmt, packet)))
                self.assertEqual(resp.S1, value & 0x0F)
                self.assertEqual(resp.S2, (value & 0xF0) >> 4)

                packet = struct.pack(x4.fmt, value)
                name, resp = x4.parse(iter(struct.unpack(x4.fmt, packet)))
                self.assertEqual(resp.S1, value & 0x0F)
                self.assertEqual(resp.S2, (value & 0xF0) >> 4)
