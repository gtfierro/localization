#Localization tools

##Router Setup
As far as we've tested (which hasn't been extremely extensive, but whatever), this setup should work on both the single and double radio routers we've been working with (Buffalo WZR-HP-G300NH2 and Buffalo WZR-HP-AG300H).
We are using OpenWrt ATTITUDE ADJUSTMENT (Bleeding Edge, r32603); there's no custom build of the kernel yet, though that will probably be coming sometime soon.

Currently, we are only monitoring AirBears traffic (due to the fact that the single radio G300NH2 routers can only monitor the 2.x GHz range), which is restricted to channels 1, 6, and 11. To configure the
requisite interfaces on the Buffalo routers, run the following commands

```
/usr/sbin/iw dev wlan0 del
/usr/sbin/iw phy phy0 interface add wlan0 type monitor
/usr/sbin/iw dev wlan0 set txpower fixed 0
/usr/sbin/iw dev wlan0 set channel 1     # or 6 or 11, it doesn't matter
/sbin/ifconfig wlan0 up
```

To ensure that we are capturing as much traffic as possible, we tell the router to rapidly cycle through channels. There is most likely a better and less-hacky way of accomplishing this task, but our current setup uses the following script:

```
echo "while [ 1 ] ; do sleep 1 ; /usr/sbin/iw wlan0 set channel 1 ; sleep 1 ; /usr/sbin/iw wlan0 set channel 6 ; sleep 1 ; /usr/sbin/iw wlan0 set channel 11 ; done" > cycle.sh
```

Now you can just run ```sh cycle.sh &``` on the router to have it cycle between the valid AirBears channels every second. You can stop the script with ```killall sh```.

###Tcpdump customization
Obviously, the routers don't have much RAM, but we still want to squeeze as many packets as we can out of them. I'm still working on a way to try to get tcpdump to clear the kernel buffer so that it doesn't start to drop packets after it has been
running for awhile, but I've found some ways to try to pare down the amount of data it feels it has to store, so we can at least run tcpdump for longer than before. Run tcpdump with the following flags on the routers. 

```
tcpdump -tt -l -e -s80 -i wlan0
```

The ```-s80``` is important because it limits the packet capture size to 80 bytes, which is enough for us to get out the BSSID and SA (source address) from the packet from the 802.11 radiotap header, which is what contains everything about signal strength.
Make sure you apply the following patch to tcpdump before you compile (see later section on how to cross compile tcpdump with custom patches for OpenWrt). The patch fixes up the printing of the radiotap header (which is why we specify the ```-e``` flag to tcpdump)
so that we can see exactly what field and what units we are dealing with.

```
--- a/print-802_11.c	
+++ b/print-802_11.c	
@@ -2033,16 +2033,16 @@
 			printf("%2.1f Mb/s ", .5*u.u8);
 		break;
 	case IEEE80211_RADIOTAP_DBM_ANTSIGNAL:
-		printf("%ddB signal ", u.i8);
+		printf("%ddBM antsignal ", u.i8);
 		break;
 	case IEEE80211_RADIOTAP_DBM_ANTNOISE:
-		printf("%ddB noise ", u.i8);
+		printf("%ddBM antnoise ", u.i8);
 		break;
 	case IEEE80211_RADIOTAP_DB_ANTSIGNAL:
-		printf("%ddB signal ", u.u8);
+		printf("%ddB antsignal ", u.u8);
 		break;
 	case IEEE80211_RADIOTAP_DB_ANTNOISE:
-		printf("%ddB noise ", u.u8);
+		printf("%ddB antnoise ", u.u8);
 		break;
 	case IEEE80211_RADIOTAP_LOCK_QUALITY:
 		printf("%u sq ", u.u16);
```

This next patch hardcodes a default filter into the tcpdump binary, so that if an alternative filter is not specified (with the ```-F <file>``` flag or by otherwise just appending it to the end
of the tcpdump command), the binary will automatically filter out all packets coming *from* the Cisco routers visible from the 4th floor and returns only packets going *to* one of those routers.

```
--- a/tcpdump.c
+++ b/tcpdump.c
@@ -1241,10 +1241,12 @@
 			warning("%s", ebuf);
 		}
 	}
-	if (infile)
-		cmdbuf = read_infile(infile);
-	else
-		cmdbuf = copy_argv(&argv[optind]);
+  if (infile)
+      cmdbuf = read_infile(infile);
+  else if (0 == (cmdbuf = copy_argv(&argv[optind])))
+      cmdbuf = copy_argv(&argv[optind]);
+  else
+      cmdbuf = "ether src not 00:24:14:31:f8:af and ether src not 00:24:14:31:f8:ae and ether src not 00:24:14:31:f6:e4 and ether src not 00:24:14:31:f6:e0 and ether src not 00:24:14:31:f6:e3 and ether src not 00:24:14:31:f9:43 and ether src not 00:24:14:31:f6:e1 and ether src not 00:24:14:31:f6:e2 and ether src not 00:24:14:31:f9:41 and ether src not 00:24:14:31:f9:42 and ether src not 00:24:14:31:f9:44 and ether src not 00:24:14:31:f9:40 and ether src not 00:24:14:31:eb:b3 and ether src not 00:24:14:31:eb:b1 and ether src not 00:24:14:31:eb:b2 and ether src not 00:24:14:31:eb:b0 and ether src not 00:24:14:31:f8:a3 and ether src not 00:24:14:31:f8:a1 and ether src not 00:24:14:31:f8:a2 and ether src not 00:24:14:31:f8:a4 and ether src not 00:24:14:31:f8:a0 and ether src not 00:24:14:31:e6:23 and ether src not 00:24:14:31:f2:e2 and ether src not 00:24:14:31:f2:e4 and ether src not 00:24:14:31:e6:21 and ether src not 00:24:14:31:e6:22 and ether src not 00:24:14:31:e6:24 and ether src not 00:24:14:31:e6:20 and ether src not 00:24:14:31:f6:ee and ether src not 00:24:14:31:f6:ef and ether src not 00:24:14:31:f9:4e and ether src not 00:24:14:31:f9:4f and ether src not 00:24:14:31:eb:be and ether src not 00:24:14:31:eb:bf and ether src not 00:24:14:31:e6:2e and ether src not 00:24:14:31:e6:2f and (ether dst 00:24:14:31:f8:af  or ether dst 00:24:14:31:f8:ae  or ether dst 00:24:14:31:f6:e4  or ether dst 00:24:14:31:f6:e0  or ether dst 00:24:14:31:f6:e3  or ether dst 00:24:14:31:f9:43  or ether dst 00:24:14:31:f6:e1  or ether dst 00:24:14:31:f6:e2  or ether dst 00:24:14:31:f9:41  or ether dst 00:24:14:31:f9:42  or ether dst 00:24:14:31:f9:44  or ether dst 00:24:14:31:f9:40  or ether dst 00:24:14:31:eb:b3  or ether dst 00:24:14:31:eb:b1  or ether dst 00:24:14:31:eb:b2  or ether dst 00:24:14:31:eb:b0  or ether dst 00:24:14:31:f8:a3  or ether dst 00:24:14:31:f8:a1  or ether dst 00:24:14:31:f8:a2  or ether dst 00:24:14:31:f8:a4  or ether dst 00:24:14:31:f8:a0  or ether dst 00:24:14:31:e6:23  or ether dst 00:24:14:31:f2:e2  or ether dst 00:24:14:31:f2:e4  or ether dst 00:24:14:31:e6:21  or ether dst 00:24:14:31:e6:22  or ether dst 00:24:14:31:e6:24  or ether dst 00:24:14:31:e6:20  or ether dst 00:24:14:31:f6:ee  or ether dst 00:24:14:31:f6:ef  or ether dst 00:24:14:31:f9:4e  or ether dst 00:24:14:31:f9:4f  or ether dst 00:24:14:31:eb:be  or ether dst 00:24:14:31:eb:bf  or ether dst 00:24:14:31:e6:2e  or ether dst 00:24:14:31:e6:2f)";
 
 	if (pcap_compile(pd, &fcode, cmdbuf, Oflag, netmask) < 0)
 		error("%s", pcap_geterr(pd));
```

###How to cross compile tcpdump for OpenWrt
Coming soon...
