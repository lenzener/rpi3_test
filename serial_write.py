#!/usr/bin/env python
import time
import serial

#ser = serial.Serial(
#	port = '/dev/ttyS0',
#	baudrate = 9600,
	#parity = serial.PARITY_NONE,
	#stopbits = serial.STOPBITS_ONE,
	#bytesize = serial.EIGHTBITS,
	#timeout = 1
#)
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
print ser.isOpen()

counter = 0
i = 0x30

str = "550150"
hex = str.decode("hex")
stop_str = "550101"

while counter < 3:
	#ser.write('Write counter: %d \n' % (counter))
	print('.')
	#ser.write(bytes([0x55, 0x01, i]))
	ser.write(hex)
	time.sleep(1)
	counter += 1

hex = stop_str.decode("hex")
ser.write(hex)

ser.close()