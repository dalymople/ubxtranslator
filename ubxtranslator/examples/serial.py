"""An example of how to use the light parser for parsing UBX messages from a serial device.

You will need to change the port name to that of the port you want to connect to. Also make sure that the baud rate is
correct and that the device has been setup to output the messages via UBX protocol to your desired port!

The serial package could easily be replaced with an alternative.
"""

import serial

from ubxtranslator.core import Parser
from ubxtranslator.predefined import NAV_CLS, ACK_CLS


def run():
    port = serial.Serial('[your port here]', baudrate=9600, timeout=0.1)

    parser = Parser([
        NAV_CLS, ACK_CLS
    ])

    print("Starting to listen for UBX packets")

    try:
        while True:
            try:
                msg = parser.receive_from(port)
                print(msg)
            except (ValueError, IOError) as err:
                print(err)

    finally:
        port.close()


if __name__ == '__main__':
    run()
