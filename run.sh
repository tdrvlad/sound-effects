#!/bin/bash
sleep 30
cd /home/pi/sound-effects
source env/bin/activate
python3 player.py
deactivate