import xively
import datetime
import sys
import time
import xml.etree.ElementTree as etree

XIVELY_API_KEY = "oZANSQsy5C7Bcjf76ARtNDoYV6uBqPKAUUERb9tsphVRZpv5"

XIVELY_FEED_ID = 1937304417
DEBUG = True

api = xively.XivelyAPIClient(XIVELY_API_KEY)
feed = api.feeds.get(XIVELY_FEED_ID)

my_data = []

import serial, sys, time, commands, re


device = None
#device = '/dev/tty.usbserial-A7006wXd'
baud = 9600

if not device:
    #devicelist = commands.getoutput("ls /dev/tty.usbmodem*")
    devicelist = commands.getoutput("ls /dev/ttyACM*")     # this works on Linux
    #devicelist = commands.getoutput("ls /dev/tty.usb*")     # this works on Teensy
    if devicelist[0] == '/': device = devicelist
    if not device: 
        print "Fatal: Can't find usb serial device."
        sys.exit(0);
    else:
        print "GOT IT %s"% devicelist

#serialport = serial.Serial(device, baud, timeout=0)
serialport = serial.Serial(
    port=device,
    baudrate=baud,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

#c = fdpexpect.fdspawn(serialport.fd)
#c.logfile_read = sys.stdout

types = { 0: 'pressure', 1: 'one-wire-temperature', 
2: 'tmpr-humid', '2-1': 'temperature', '2-2': 'humidity', 3: 'light' }

# while True:
try: 
    for x in xrange(1,5):
        cmd = serialport.readline().strip()
        print "===== %s" % cmd
        m = re.findall(r"NODE: (\d+) TYPE: (\d+) VALUE: \[([^\[\]]*)\]", cmd)
        print m
        for x in m:
            feed_type_id = int(x[1])
            feed_type = types.get(feed_type_id)
            print "FEED TYPE ID = %s" % feed_type_id
            print "FEED TYPE    = %s" % feed_type
            node_id = x[0]
            now = datetime.datetime.utcnow()
            if feed_type_id == 2:
                print "TYPE ===== 2 ====="
                val = x[2].split(":")
                print "\tTEMPERATURE: %s HUMIDITY %s" %(val[0], val[1])
                my_data.append(xively.Datastream(id='humidity-'+node_id, current_value=val[1]))
                my_data.append(xively.Datastream(id='temperature-'+node_id, current_value=val[0]))
                # update_datastream(feed=feed, channel = 'temperature-'+node_id, sensor_data = val[0])
                # update_datastream(feed=feed, channel = 'humidity-'+node_id, sensor_data = val[1])
            else:
                print "TYPE ===== %s =====" %feed_type 
                print "\ttype: %10s node: %s" %(feed_type, x[0])
                my_data.append(xively.Datastream(id=feed_type+"-"+node_id, current_value=x[2], at=now))
                # update_datastream(feed=feed, channel = feed_type, sensor_data = x[2])
                
        print "===" * 20
        print "======= DATA ======"
        print my_data
        feed.datastreams = my_data
        print feed.update()
        my_data = []
        # feed.datastreams = [
        #     xively.Datastream(id='tmpr', current_value=10, at=now),
        #     xively.Datastream(id='watts', current_value=20, at=now),
        # ]
        time.sleep(4)
except Exception:
    print "ERRROR"

serialport.close()
print "DONE"


