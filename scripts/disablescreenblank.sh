#!/bin/bash

screen=${1:-0}

# wait for the display manager service to start and attach to screen
sleep 15

/usr/bin/xset -display :$screen s off          # deactivate screen saver
/usr/bin/xset -display :$screen -dpms          # disable DPMS
/usr/bin/xset -display :$screen s noblank      # disable screen blanking
