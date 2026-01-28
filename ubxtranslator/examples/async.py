"""An example of a state class with an async parser using pyserial-asyncio.

You will need to change the port name to that of the port you want to connect to. Also make sure that the baud rate is
correct and that the device has been setup to output UBX messages protocol to your desired port!
"""

import asyncio
from asyncio import Event

import serial_asyncio

from ubxtranslator.core import Parser
from ubxtranslator.predefined import NAV_CLS, ACK_CLS


class GnssService:
    def __init__(self, port, baud_rate):
        self.parser = Parser([NAV_CLS, ACK_CLS])
        self.port = port
        self.baud_rate = baud_rate
        self.last_message = None
        self.new_message_event = Event()

    async def read_serial(self):
        """Read from serial port asynchronously using pyserial-asyncio."""
        while True:
            try:
                reader, _ = await serial_asyncio.open_serial_connection(
                    url=self.port, baudrate=self.baud_rate
                )
                print(f"Starting to listen for UBX packets on {self.port}")
                while True:
                    try:
                        msg = await self.parser.receive_from_async(reader)
                        if msg:
                            self.last_message = msg
                            self.new_message_event.set()

                    except (ValueError, IOError, asyncio.IncompleteReadError) as e:
                        print(f"Error parsing UBX message: {e}")
                        continue

            except Exception as e:
                print(f"Could not open serial port {self.port}: {e}")
                # Wait before trying to reconnect
                await asyncio.sleep(5)

    async def print_last_message(self):
        """An event based approach to consumption."""
        while True:
            await self.new_message_event.wait()
            print(self.last_message)
            self.new_message_event.clear()

    async def run(self):
        """Run the service."""
        await asyncio.gather(self.read_serial(), self.print_last_message())

