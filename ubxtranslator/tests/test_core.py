"""Basic unit testing of the core module"""

import unittest
from itertools import permutations
import struct
from io import BytesIO

from ubxtranslator.core import *


class UbxMsgTester(unittest.TestCase):
    def test_msg_basic(self):
        fields = [
            PadByte(),
            Field('F1', 'U1'),
            Field('F2', 'I1'),
            PadByte(),
            Field('F3', 'U1'),
            BitField('F4', 'X1', [
                Flag('SF1', 0, 4),
                Flag('SF2', 4, 8)
            ])
        ]

        with self.assertRaises(ValueError):
            Message(-1, 'TEST', fields)

        with self.assertRaises(ValueError):
            Message(0xFF + 1, 'TEST', fields)

        m = Message(1, 'TEST', fields)

        self.assertEqual(struct.calcsize(m.fmt), 6)

        payload = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0xA8])
        name, resp = m.parse(payload)

        self.assertEqual(name, 'TEST')
        self.assertEqual(resp.F1, 0x02)
        self.assertEqual(resp.F2, 0x03)
        self.assertEqual(resp.F3, 0x05)
        self.assertEqual(resp.F4.SF1, 0x8)
        self.assertEqual(resp.F4.SF2, 0xA)

    def test_msg(self):
        types = {'U1': {'type_': int},
                 'I1': {'type_': int},
                 'U2': {'type_': int},
                 'I2': {'type_': int},
                 'U4': {'type_': int},
                 'I4': {'type_': int},
                 'R4': {'type_': float},
                 'R8': {'type_': float},
                 'C': {'type_': lambda x: bytes([x])},
                 }

        keys = [x for x in types]

        for key_list in permutations(keys, 5):
            with self.subTest(key_list=key_list):
                m = Message(1, 'TEST',
                            [Field('F{}'.format(i), x) for i, x in enumerate(key_list)]
                            )

                payload_parts = [types[k]['type_'](i) for i, k in enumerate(key_list)]

                payload = struct.pack(m.fmt, *payload_parts)

                name, resp = m.parse(payload)

                self.assertEqual(name, 'TEST')

                for i, k in enumerate(key_list):
                    self.assertEqual(getattr(resp, 'F{}'.format(i)), payload_parts[i])

    def test_msg_repeated(self):
        fields = [
            RepeatedBlock('RB1', [
                Field('F1', 'U1'),
                PadByte(repeat=1),
                BitField('F2', 'X1', [
                    Flag('SF1', 0, 4),
                    Flag('SF2', 4, 8)
                ]),
            ]),
            Field('F3', 'U1'),
            PadByte(repeat=2),
        ]

        m = Message(1, 'TEST', fields)
        self.assertEqual(struct.calcsize(m.fmt), 8)

        for i in range(100):
            m._repeated_block.repeat = i
            with self.subTest(msg='calc size', repeat=i):
                self.assertEqual(struct.calcsize(m.fmt), (i * 4) + 8)

        for i in range(1, 100):
            payload = bytes([x & 0xFF for x in range((i * 4) + 8)])
            name, resp = m.parse(payload)
            with self.subTest(msg='parse', repeat=i):
                self.assertEqual(name, 'TEST')
                self.assertEqual(len(resp.RB1), i + 1)

                for j in range(i + 1):
                    self.assertEqual(resp.RB1[j].F1, (j * 4) & 0xFF)
                    self.assertEqual(resp.RB1[j].F2.SF1, ((j * 4) + 3) & 0x0F)
                    self.assertEqual(resp.RB1[j].F2.SF2, (((j * 4) + 3) & 0xF0) >> 4)

                self.assertEqual(resp.F3, ((i * 4) + 4) & 0xFF)

    def test_multiple_repeats(self):
        fields = [
            RepeatedBlock('RB1', [
                Field('F1', 'U1'),
                PadByte(repeat=1),
                BitField('F2', 'X1', [
                    Flag('SF1', 0, 4),
                    Flag('SF2', 4, 8)
                ]),
            ]),
            RepeatedBlock('RB2', [
                Field('F3', 'U1'),
                PadByte(repeat=2),
            ]),
        ]

        with self.assertRaises(ValueError):
            m = Message(1, 'TEST', fields)


class UbxClsTester(unittest.TestCase):
    def test_cls(self):
        fields = [
            PadByte(),
            Field('F1', 'U1'),
            Field('F2', 'I1'),
            PadByte(),
            Field('F3', 'U1'),
            BitField('F4', 'X1', [
                Flag('SF1', 0, 4),
                Flag('SF2', 4, 8)
            ])
        ]
        m = Message(1, 'TEST', fields)

        with self.assertRaises(ValueError):
            Cls(-1, 'TEST', [m, ])

        with self.assertRaises(ValueError):
            Cls(0xFF + 1, 'TEST', [m, ])

        cls = Cls(1, 'TEST', [m, ])
        self.assertEqual(cls[1], m)
        with self.assertRaises(KeyError):
            _ = cls[2]

        m2 = Message(2, 'OTHER_TEST', fields)
        cls.register_msg(m2)
        self.assertEqual(2, len(cls._messages))
        self.assertEqual(cls[2], m2)

        self.assertTrue(1 in cls)
        self.assertTrue(2 in cls)
        self.assertFalse(3 in cls)


class UbxParserTester(unittest.TestCase):
    def test_parser(self):
        cls = Cls(1, 'TEST', [
            Message(1, 'TEST', [
                PadByte(),
                Field('F1', 'U1'),
                Field('F2', 'I1'),
                PadByte(),
                Field('F3', 'U1'),
                BitField('F4', 'X1', [
                    Flag('SF1', 0, 4),
                    Flag('SF2', 4, 8)
                ])
            ])
        ])

        parser = Parser([cls])

        with self.subTest(msg='Test correct use age'):
            test_packet = bytes([1, 1, 6, 0, 0, 1, 2, 3, 4, 5])
            test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)

            test_stream = BytesIO(test_packet)

            cls_name, msg_name, msg = parser.receive_from(test_stream)

            self.assertEqual(msg.F1, 1)
            self.assertEqual(msg.F2, 2)
            self.assertEqual(msg.F3, 4)
            self.assertEqual(msg.F4.SF1, 5)
            self.assertEqual(msg.F4.SF2, 0)

        with self.subTest(msg='Test bad class id'):
            with self.assertRaises(ValueError):
                test_packet = bytes([2, 1, 6, 0, 0, 1, 2, 3, 4, 5])
                test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)

                test_stream = BytesIO(test_packet)

                parser.receive_from(test_stream)

        with self.subTest(msg='Test bad msg'):
            with self.assertRaises(ValueError):
                test_packet = bytes([1, 2, 6, 0, 0, 1, 2, 3, 4, 5])
                test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)

                test_stream = BytesIO(test_packet)

                parser.receive_from(test_stream)

        with self.subTest(msg='Test bad length'):
            with self.assertRaises(IOError):
                test_packet = bytes([1, 1, 7, 0, 0, 1, 2, 3, 4, 5])
                test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)

                test_stream = BytesIO(test_packet)

                parser.receive_from(test_stream)

        with self.subTest(msg='Test bad length'):
            with self.assertRaises(IOError):
                test_packet = bytes([1, 1, 6, 0, 0, 1, 2, 3, 5])
                test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)

                test_stream = BytesIO(test_packet)

                parser.receive_from(test_stream)

        with self.subTest(msg='Test bad checksum'):
            with self.assertRaises(ValueError):
                test_packet = bytes([1, 1, 6, 0, 0, 1, 2, 3, 4, 5])
                test_packet = parser.PREFIX + test_packet + bytes([0, 1])

                test_stream = BytesIO(test_packet)

                parser.receive_from(test_stream)
