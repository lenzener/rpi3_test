#!/bin/sh
sudo /usr/local/nginx/sbin/nginx

gst-launch-1.0 -v v4l2src ! 'video/x-raw, width=640, height=480, framerate=30/1' ! queue ! videoconvert ! omxh264enc !  h264parse ! flvmux ! rtmpsink location='rtmp://192.168.5.92/live/camera live=1'

# or
#avconv -f video4linux2 -r 24 -i /dev/video0 -f flv rtmp://192.168.5.92/live/camera

sudo /usr/local/nginx/sbin/nginx -s stop
