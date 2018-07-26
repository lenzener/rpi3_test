#!/usr/bin/env python
import time
import serial
import threading
import logging
import socket
import fcntl
import struct
import sys

exit_flag = False

class Send:
    def __init__(self, Baudrate=9600, Device='/dev/ttyS0'):
        self.baudrate = Baudrate
        self.device = Device
        
        self.ser = serial.Serial(self.device, self.baudrate, timeout=1)

    def close(self):
        self.ser.close()

    def SendData(self, data):
        self.ser.write(data)


    def myRange(self, x, a, b, c, d):
        return (float(x-a))/(b-a)*(d-c) + c

    def SetSpeed(self, id, speed):
        s = self.myRange(speed, 0, 100, 1, 255)
        print(s)
        str = '55%02x%02x' % (id, s)
        print('set spped %d' % speed)
        hex_str = str.decode("hex")
        print(str)
        self.ser.write(hex_str)
        self.close()

def UdpThreaded(fn, callback_func):
    def wrapper(*args, **kwargs):
        def do_callback():
            callback_func(fn(args, dwargs))

        thread = Thread(target=do_callback)
        thread.start()
        return thread
    return wrapper

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class UdpServer:
    listen_port = 8765
    remote_port = 9090
    key_word = 'find'

    @threaded
    def Run(self):
        print("start udp server\n")
        host=get_ip_address('eth0')
        ip = '.'.join(host.split(".")[:-1:]) + '.255'
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # log.info("Listening on udp %s:%s" % (host, port))
        print("Listening on udp %s:%s" % (ip, self.listen_port))
        s.bind((ip, self.listen_port))
        while True:
            (data, addr) = s.recvfrom(128*1024)
            print('udp')
            if check(data):
                s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_client.connect((addr[0], self.remote_port))
                # s_client.send(host)
                s_client.send(IPData().ToString())
                s_client.close()

def check(data):
    data_hex = list(bytearray(data))   
    if 0xFA == data_hex[0] and 0xED == data_hex[-1]:
        length = len(data_hex)
        sum = 0
        for i in range(1, length-2):
            sum += data_hex[i]

        return True
    
    return False

def CreateSum(data):
    sum = 0
    for i in range(1,len(data) - 2):
        sum += data[i]

    return sum

def FillSum(data):
    sum = CreateSum(data)
    data[len(data)-2] = sum % 255

class IPData(object):
    def ToString(self):
        host=get_ip_address('eth0')
        # ip_as_bytes = bytes(map(int, host.split('.')))
        ip_as_bytes = socket.inet_aton(host)
        data = b'\xFA\x02\x04' + ip_as_bytes  + b'\x00\xED'
        data_as_bytearray = bytearray(data)
        FillSum(data_as_bytearray)
        return data_as_bytearray

class TcpServer:
    listen_port = 9090

    def parse(self):
        data_hex = list(bytearray(self.data)) 
        if 0x01 == data_hex[1]: # set speed
            valid_len = data_hex[2]
            id = data_hex[3]
            angle = data_hex[4]
            print("send %d : %d" , (id, angle))
            Send().SetSpeed(id, angle)
    
    @threaded
    def Run(self):
        print("start tcp server\n")

        host=get_ip_address('eth0')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (host, self.listen_port)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)

        sock.listen(1)

        while True:
            # Wait for a connection
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()

            try:
                print >>sys.stderr, 'connection from', client_address

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(256)
                    print >>sys.stderr, 'received "%s" %d ' % (data, len(data))
                    if data:
                        print >>sys.stderr, 'sending data back to the client'
                        # connection.sendall(data)
                        # FA 01 02 01 5A 5E ED        
                        # data_hex = list(bytearray(data))   
                        if check(data):
                            print('get pack')
                            self.data = data
                            self.parse()
                        
                    else:
                        print >>sys.stderr, 'no more data from', client_address
                        break
                    
            finally:
                # Clean up the connection
                connection.close()

def main():
    UdpServer().Run()
    TcpServer().Run()
    while True:
        time.sleep(3)

    print("end main")
    # Send().SetSpeed(0)

if __name__ == '__main__':
    main()
    # IPData().ToString()
