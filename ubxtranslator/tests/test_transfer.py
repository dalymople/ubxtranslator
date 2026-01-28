import unittest
import struct
from io import BytesIO
from ubxtranslator.core import *

class UbxTransferTester(unittest.TestCase):
    def setUp(self):
        self.fields = [
            Field('F1', 'U1'),
            BitField('F2', 'X1', [
                Flag('SF1', 0, 4),
                Flag('SF2', 4, 8)
            ]),
            RepeatedBlock('RB', [
                Field('RF1', 'U2')
            ])
        ]
        self.msg = Message(0x01, 'TEST_MSG', self.fields)
        self.cls = Cls(0x01, 'TEST_CLS', [self.msg])
        self.parser = Parser([self.cls])

    def test_pack_basic(self):
        values = {
            'F1': 10,
            'F2': {'SF1': 1, 'SF2': 2},
            'RB': [{'RF1': 100}, {'RF1': 200}]
        }
        payload = self.msg.pack(values)
        # F1(1) + F2(1) + RB(2*2) = 6 bytes
        self.assertEqual(len(payload), 6)

        # Unpack to verify
        # F1: 10 (0x0A)
        # F2: SF1=1, SF2=2 => 0x21
        # RB[0]: 100 (0x0064)
        # RB[1]: 200 (0x00C8)
        # fmt: 'BBHH'
        expected = struct.pack('<BBHH', 10, 0x21, 100, 200)
        self.assertEqual(payload, expected)

    def test_round_trip(self):
        prepared = self.parser.prepare_msg('TEST_CLS', 'TEST_MSG')
        prepared['F1'] = 50
        prepared['F2']['SF1'] = 8
        prepared['F2']['SF2'] = 15
        prepared['RB'] = [{'RF1': 1000}, {'RF1': 2000}, {'RF1': 3000}]

        stream = BytesIO()
        self.parser.transfer_to(prepared, stream)

        # Now parse it back
        stream.seek(0)
        cls_name, msg_name, resp = self.parser.receive_from(stream)

        self.assertEqual(cls_name, 'TEST_CLS')
        self.assertEqual(msg_name, 'TEST_MSG')
        self.assertEqual(resp.F1, 50)
        self.assertEqual(resp.F2.SF1, 8)
        self.assertEqual(resp.F2.SF2, 15)
        self.assertEqual(len(resp.RB), 3)
        self.assertEqual(resp.RB[0].RF1, 1000)
        self.assertEqual(resp.RB[1].RF1, 2000)
        self.assertEqual(resp.RB[2].RF1, 3000)

    def test_checksum_error(self):
        prepared = self.parser.prepare_msg('TEST_CLS', 'TEST_MSG')
        stream = BytesIO()
        self.parser.transfer_to(prepared, stream)

        data = bytearray(stream.getvalue())
        # Flip a bit in the payload
        data[6] ^= 0xFF

        corrupted_stream = BytesIO(data)
        with self.assertRaises(ValueError) as cm:
            self.parser.receive_from(corrupted_stream)
        self.assertIn("Checksum mismatch", str(cm.exception))

    def test_empty_repeated_block(self):
        values = {
            'F1': 10,
            'F2': {'SF1': 1, 'SF2': 2},
            'RB': []
        }
        with self.assertRaises(ValueError) as cm:
            self.msg.pack(values)
        self.assertIn("cannot be empty", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
