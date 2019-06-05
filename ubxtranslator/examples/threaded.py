"""An example of a multi-threaded queue based approach to parsing.

You will need to change the port name to that of the port you want to connect to. Also make sure that the baud rate is
correct and that the device has been setup to output UBX messages protocol to your desired port!

Placing the messages on a queue as they are received allows an asynchronous approach to message receipt.
"""

import threading
import time
from queue import Queue

import serial

from ubxtranslator.core import Parser
from ubxtranslator.predefined import NAV_CLS, ACK_CLS


def worker(port, parser, q):
    while True:
        try:
            msg = parser.receive_from(port)
            q.put_nowait(msg)

        except (ValueError, IOError) as err:
            print(err)


def run():
    port = serial.Serial('[your port here]', baudrate=9600, timeout=0.1)

    parser = Parser([
        NAV_CLS,
        ACK_CLS,
    ])

    q = Queue()

    thread = threading.Thread(target=worker, args=(port, parser, q))

    print('Starting the worker thread to listen for UBX packets.')
    thread.start()

    try:
        while True:
            print('Doing something else for 10 seconds.')
            time.sleep(10)
            while not q.empty():
                print('Messages are available, lets print them!')
                print(q.get_nowait())

    finally:
        port.close()

        print("Good bye.")
