# ubxtranslator [![Build Status](https://travis-ci.org/dalymople/ubxtranslator.svg?branch=master)](https://travis-ci.org/dalymople/ubxtranslator)

## Overview
This module provides a simple way to decode messages from uBlox GPS devices in the UBX format. 
Like the high accuracy NEO-M8U module that I have created, 
<a href="https://www.tindie.com/products/dalymople/gps-dead-reckoning-board-neo-m8u-gnss">click here for more info.</a><br>
<br>
This package has no dependencies! This is written in pure python using only the standard lib and supports any
standard byte stream. The predefined messages are not added to the parser by default, this allows
you to have tight control over what messages can be parsed.

Is this the fastest implementation of a UBX parser? Probably not. If speed is critical then you 
probably need to go write something in C. If you want something that is fast enough
and easy to use, you are in the right place. Keep reading.

Supports Python 3.5 and up.


## Quickstart

Install the package with pip<br>
`pip install ubxtranslator`

Import the core module<br>
`from ubxtranslator import core`

If the message class you want has already been defined simply import it. 
If not you will need to construct the messages and classes yourself, see the examples for more information.<br>
`from ubxtranslator.predefined import CLS_ACK, CLS_NAV`

Construct the parser<br>
`parser = core.Parser([CLS_ACK, CLS_NAV])`

Then you can use the parser to decode messages from any byte stream.<br>
`cls_name, msg_name, payload = parser.receive_from(port)`

The payload is the named tuple of the message<br>
`print(cls_name, msg_name, payload.lat, payload.lng)`

## Examples
For full examples see the examples directory. 

## TODO's
Want to contribute? Please feel free to submit issues or pull requests. 
Nothing in this package is very complicated, please have a crack and help me to improve this.

- Add the ability to pack messages into packets for two way communications
- Add repeated blocks
- Add more and better tests
- Add Field type RU1_3
- Add async support
