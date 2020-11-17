"""An example of how to define a message and message class.

If the message and/or class that you need is not predefined then you can define your own messages and class.
this it quite simple, just import the building blocks and then follow the datasheet to build the fields, messages
and class.

"""

from ubxtranslator.core import Message, Cls, PadByte, Field, Flag, BitField

CUSTOM_CLS = Cls(0x01, 'NAV', [
    Message(0x07, 'PVT', [
        Field('iTOW', 'U4'),
        Field('year', 'U2'),
        Field('month', 'U1'),
        Field('day', 'U1'),
        Field('hour', 'U1'),
        Field('min', 'U1'),
        Field('sec', 'U1'),
        BitField('valid', 'X1', [
            Flag('validDate', 0, 1),
            Flag('validTime', 1, 2),
            Flag('fullyResolved', 2, 3),
            Flag('validMag', 3, 4),
        ]),
        Field('tAcc', 'U4'),
        Field('nano', 'I4'),
        Field('fixType', 'U1'),
        BitField('flags', 'X1', [
            Flag('gnssFixOK', 0, 1),
            Flag('diffSoln', 1, 2),
            Flag('headVehValid', 2, 5),
            Flag('carrSoln', 6, 8),
        ]),
        BitField('flags2', 'X1', [
            Flag('confirmedAvai', 5, 6),
            Flag('confirmedDate', 6, 7),
            Flag('confirmedTime', 7, 8),
        ]),
        Field('numSV', 'U1'),
        Field('lon', 'I4'),
        Field('lat', 'I4'),
        Field('height', 'I4'),
        Field('hMSL', 'I4'),
        Field('hAcc', 'U4'),
        Field('vAcc', 'U4'),
        Field('velN', 'I4'),
        Field('velE', 'I4'),
        Field('velD', 'I4'),
        Field('gSpeed', 'I4'),
        Field('headMot', 'I4'),
        Field('sAcc', 'U4'),
        Field('headAcc', 'U4'),
        Field('pDOP', 'U2'),
        PadByte(5),
        Field('headVeh', 'I4'),
        Field('magDec', 'I2'),
        Field('magAcc', 'U2'),
    ])
])
