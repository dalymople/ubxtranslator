"""An example of how to use the parser to pack and transfer UBX messages.

This example demonstrates:
1. Preparing a message with default values.
2. Modifying the message data.
3. Packing the message into a UBX packet.
4. Sending the packet to a stream.
5. Receiving it back from the stream to verify.
"""

from io import BytesIO
from ubxtranslator.core import Parser
from ubxtranslator.predefined import ACK_CLS, NAV_CLS


def run():
    # 1. Initialize the parser with some predefined classes
    parser = Parser([ACK_CLS, NAV_CLS])

    # 2. Prepare an ACK-ACK message
    # prepare_msg returns a dictionary prefilled with default values for all fields
    print("Preparing ACK-ACK message...")
    msg_dict = parser.prepare_msg('ACK', 'ACK')
    print(f"Default values: {msg_dict}")

    # 3. Modify the fields
    # clsID and msgID in ACK-ACK message indicate which message is being acknowledged
    msg_dict['clsID'] = 0x01  # NAV class
    msg_dict['msgID'] = 0x07  # PVT message
    print(f"Modified values: {msg_dict}")

    # 4. Transfer to a stream (using BytesIO to simulate a serial port)
    # The parser handles packing and metadata internally
    stream = BytesIO()
    print("\nTransferring message to stream...")
    parser.transfer_to(msg_dict, stream)

    # Show the raw bytes in the stream
    stream.seek(0)
    raw_bytes = stream.read()
    print(f"Raw UBX packet (hex): {raw_bytes.hex(' ')}")

    # 5. Receive and parse it back from the stream to verify
    stream.seek(0)
    print("\nReceiving message back from stream...")
    cls_name, msg_name, parsed_msg = parser.receive_from(stream)

    print(f"Received: {cls_name}-{msg_name}")
    print(f"Parsed data: {parsed_msg}")

    # Example with a more complex message (NAV-CLOCK)
    print("\n--- Complex message example (NAV-CLOCK) ---")
    clock_dict = parser.prepare_msg('NAV', 'CLOCK')
    clock_dict['iTOW'] = 123456
    clock_dict['clkB'] = -1000
    clock_dict['clkD'] = 50
    clock_dict['tAcc'] = 100
    clock_dict['fAcc'] = 500

    stream_clock = BytesIO()
    parser.transfer_to(clock_dict, stream_clock)

    stream_clock.seek(0)
    _, _, parsed_clock = parser.receive_from(stream_clock)
    print(f"Parsed NAV-CLOCK: {parsed_clock}")


if __name__ == '__main__':
    run()
