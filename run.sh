#!/bin/bash
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
cd /home/pi/sound-effects
source env/bin/activate
python3 player.py
deactivate