# Wordclock Server
This component of the iot-ledmatrix framework runs on the
device you want to control, communicating with the LEDs via an
Arduino

## Local Testing
An example to run the code in local testing mode with a GUI:
```shell script
python3 main.py --errors-to-console --name=test-server --width=10 --height=10 --disable-arduino-connection --start-script=_Wordclock --enable-gui
```

## Deployment
This is an example for deploying the host on an RPi

### /etc/rc.local for autostart
```bash!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

/bin/bash /home/pi/start_wakeuplight.sh

exit 0
```

### start_wakeuplight.sh in home
```bash
#!/bin/bash

# wait for internet connection to be able to pull updates
STATE="error";

while [  $STATE == "error" ]; do
    # do a ping and check that its not a default message or change to grep for something else
    STATE=$(ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && echo ok || echo error)
    
    # sleep for 2 seconds; try again
    sleep 2
done

/usr/bin/git -C /home/pi/iot-ledmatrix pull >> /home/pi/git_pull_log
/usr/bin/python3 /home/pi/iot-ledmatrix/host/main.py --start-script=_WakeUpLight --name="My WUPLight" --disable-discovery --width=10 --height=6 --logfile=/home/pi/matrix.log --keepalive >> /home/pi/output_matrix.log
```


### /etc/avahi/services/ledmatrix.service
This configures the discovery of the matrix, since we've set `--disable-discovery` above and this is the way
most compatible with android right now. Also notices how the names is xxx:<width>:<height> because service resolution
doesn't properly work in android, so we're embedding this info in the name.

```xml
<?xml version="1.0" standalone='no'?><!--*-nxml-*-->
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">

<service-group>
  <name replace-wildcards="no">My WUPLight:10:10</name>
  <service>
    <type>_iot-ledmatrix._tcp</type>
    <port>55124</port>
  </service>
</service-group>
```

This file must be readable by avahi, so do `sudo chown avahi:avahi ledmatrix.service`.