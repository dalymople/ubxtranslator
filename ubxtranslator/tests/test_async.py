import unittest
import asyncio
from ubxtranslator.core import *


class MockStreamReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    async def read(self, n):
        chunk = self.data[self.pos:self.pos + n]
        self.pos += len(chunk)
        return chunk

    async def readexactly(self, n):
        chunk = self.data[self.pos:self.pos + n]
        if len(chunk) < n:
            raise asyncio.IncompleteReadError(chunk, n)
        self.pos += n
        return chunk


class UbxAsyncParserTester(unittest.IsolatedAsyncioTestCase):
    async def test_parser_async(self):
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

        with self.subTest(msg='Test correct async usage'):
            test_packet = bytes([1, 1, 6, 0, 0, 1, 2, 3, 4, 5])
            test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)

            test_stream = MockStreamReader(test_packet)

            cls_name, msg_name, msg = await parser.receive_from_async(test_stream)

            self.assertEqual(msg.F1, 1)
            self.assertEqual(msg.F2, 2)
            self.assertEqual(msg.F3, 4)
            self.assertEqual(msg.F4.SF1, 5)
            self.assertEqual(msg.F4.SF2, 0)

        with self.subTest(msg='Test async bad class id'):
            test_packet = bytes([2, 1, 6, 0, 0, 1, 2, 3, 4, 5])
            test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)
            test_stream = MockStreamReader(test_packet)
            with self.assertRaises(ValueError):
                await parser.receive_from_async(test_stream)

        with self.subTest(msg='Test async bad msg'):
            test_packet = bytes([1, 2, 6, 0, 0, 1, 2, 3, 4, 5])
            test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)
            test_stream = MockStreamReader(test_packet)
            with self.assertRaises(ValueError):
                await parser.receive_from_async(test_stream)

        with self.subTest(msg='Test async bad checksum'):
            test_packet = bytes([1, 1, 6, 0, 0, 1, 2, 3, 4, 5])
            test_packet = parser.PREFIX + test_packet + bytes([0, 1])
            test_stream = MockStreamReader(test_packet)
            with self.assertRaises(ValueError):
                await parser.receive_from_async(test_stream)

        with self.subTest(msg='Test async insufficient data'):
            test_packet = bytes([1, 1, 6, 0, 0, 1, 2, 3, 5])
            test_packet = parser.PREFIX + test_packet + parser._generate_fletcher_checksum(test_packet)
            test_stream = MockStreamReader(test_packet)
            with self.assertRaises(asyncio.IncompleteReadError):
                await parser.receive_from_async(test_stream)

    async def test_read_until_async(self):
        data = b"some junk" + Parser.PREFIX + b"more data"
        stream = MockStreamReader(data)

        # Test reading until PREFIX
        result = await Parser._read_until_async(stream, terminator=Parser.PREFIX)
        self.assertEqual(result, b"some junk" + Parser.PREFIX)

        # Test reading with size limit
        stream = MockStreamReader(b"1234567890")
        result = await Parser._read_until_async(stream, terminator=b"XYZ", size=5)
        self.assertEqual(result, b"12345")

        # Test reading until EOF
        stream = MockStreamReader(b"eof reach")
        result = await Parser._read_until_async(stream, terminator=b"NOT_HERE")
        self.assertEqual(result, b"eof reach")


if __name__ == '__main__':
    unittest.main()
