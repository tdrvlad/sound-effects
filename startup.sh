#!/bin/bash
echo Started Execution
sleep 30
echo Running Script

export HOME=/home/pi
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
/usr/bin/ssh pi@localhost /home/pi/sound-effects/run.sh
