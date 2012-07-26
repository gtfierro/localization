while [ 1 ] ; do sleep 1 ; /usr/sbin/iw wlan0 set channel 1 ; sleep 1 ; /usr/sbin/iw wlan0 set channel 6 ; sleep 1 ; /usr/sbin/iw wlan0 set channel 11 ; done
