# ubxtranslator [![Build Status](https://travis-ci.org/dalymople/ubxtranslator.svg?branch=master)](https://travis-ci.org/dalymople/ubxtranslator)

## Overview
This module provides a simple way to decode messages from uBlox GPS devices in the UBX format. 
Like the high accuracy NEO-M8U module that I have created, 
<a href="https://www.tindie.com/products/dalymople/gps-dead-reckoning-board-neo-m8u-compact/">click here for more info.</a><br>
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
`from ubxtranslator import predefined`

Construct the parser<br>
```
parser = core.Parser([
  predefined.CLS_ACK, 
  predefined.CLS_NAV
])
```

Then you can use the parser to decode messages from any byte stream.<br>
`cls_name, msg_name, payload = parser.receive_from(port)`

The result is a tuple which can be unpacked as shown above.<br>
The variables `cls_name` and `msg_name` are strings, ie. `'NAV'`, `'PVT'`.<br>

The payload is the namedtuple of the message and can be accessed like an object. The attributes share the names of the fields.<br>
`print(cls_name, msg_name, payload.lat, payload.lng)`

Bitfields are also returned as namedtuples and can be accessed the same way.<br>
`print(payload.flags.channel)`

Repeated Blocks are returned as a list of blocks, the fields within each block are also named tuples. All of the repeated blocks in the predefined messages are name `RB`.<br>
```
for i in range(len(payload.RB)):
  print(payload.RB[i].gnssId, payload.RB[i].flags.health)
```

The best way to look at what fields are available is where the fields are defined. However, if you want to inspect on the fly you can either `help(payload)` and look at the attributes, or use the named tuple protected method `payload._asdict()` which will return an ordered dict of all of the attributes.


## Examples
For full examples see the examples directory. 

## TODO's
Want to contribute? Please feel free to submit issues or pull requests. 
Nothing in this package is very complicated, please have a crack and help me to improve this.

- Add the ability to pack messages into packets for two way communications
- Add more and better tests
- Add Field type RU1_3
- Add async support
