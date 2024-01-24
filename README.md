### Issues with running the script at startup
The script execution as wrapped in a bash script:
```
#!/bin/bash
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
cd /home/pi/sound-effects
source env/bin/activate
python3 player.py
deactivate
```
This command was succesfully called from a ssh session, and the script executed as expected: audio played and the ligths flickered in synchronisation.
However, there were several issues with making this script execute at startup.
It seems like not all combinations of users executions enabled the script to access the audio drive in order to play sounds.

For example running the command `/home/pi/sound-effects/run.sh` worked, while applying `sudo` to it didn't.
SInce some of the automatica
sudo -E -u pi /home/pi/sound-effects/run.sh  



# Auto-startup
Install the `startup` command to run at the system boot;

Use `crontab -e` to edit the cron tasks.
Add this at the end:
```
@reboot /bin/bash /home/pi/sound-effects/startup.sh  > /home/pi/sound-effects/startup.log 2>&1
```

