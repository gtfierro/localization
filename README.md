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

##Tcpdump customization
Obviously, the routers don't have much RAM, but we still want to squeeze as many packets as we can out of them. I'm still working on a way to try to get tcpdump to clear the kernel buffer so that it doesn't start to drop packets after it has been
running for awhile, but I've found some ways to try to pare down the amount of data it feels it has to store, so we can at least run tcpdump for longer than before. Run tcpdump with the following flags on the routers. 

~~tcpdump -tt -l -e -s80 -i wlan0~~

UPDATE: due to the benchmarks done below, the following command seems to work much much better:
```
tcpdump -tt -w - -U -s80 -e -i wlan0 -y IEEE802_11_RADIO -F /root/router-filter
```

The ```-w - -U``` options take the place of the previous ```-l``` option, and seem to handle the output of text much more robustly, so that stdout doesn't muck everything up. The ```-s80``` is important because it limits the packet capture size to 80 bytes, which is enough for us to get out the BSSID and SA (source address) from the packet from the 802.11 radiotap header, which is what contains everything about signal strength.
Make sure you apply the following patch to tcpdump before you compile (see later section on how to cross compile tcpdump with custom patches for OpenWrt). The patch fixes up the printing of the radiotap header (which is why we specify the ```-e``` flag to tcpdump)
so that we can see exactly what field and what units we are dealing with. Also make sure that router-filter (from the repo) is in the root directory.

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

##How to cross compile tcpdump for OpenWrt
First, get the OpenWrt source

```
svn co  svn://svn.openwrt.org/openwrt/trunk/
```

Now ```cd``` into the trunk, and make sure to update the package feeds.

```
cd trunk
scripts/feeds update
scripts/update-package-md5sum package
make package/symlinks
```

Now you can configure the kernel for compilation. Run ```make menuconfig``` to get the build configuration menu. Make sure you specify the correct Target System (the G300NH2 and AG300H use AR71xx), and
be sure to specify the "Build the OpenWrt Image Builder," "Build the OpenWrt SDK," and "Build the OpenWrt based Toolchain" options. *Especially* make sure you select the SDK one. If you forget the others,
it may or may not work, so if it doesn't work, rebuild the kernel with those other options selected. Finally, after you're all done, run ```make```.

Okay, now that that has completed correctly (don't worry, you're not going to have to wait for the full kernel install each time), you can compile tcpdump! From the trunk directory (I'll be treating this as the ```PWD``` from now on),
copy your patch files (at least the two above) to ```./package/tcpdump/patches/```. Make sure that each patch is prepended with a 3 digit number. The actual number doesn't matter as long as it is 3 digits (0-padding for single and double
digit numbers) and it's not the same number as another prefix in the same directory. Now, from the trunk directory, run ```make V=99 package/tcpdump/{clean,prepare,compile}```. Hopefully this compiles correctly. If it did, then you'll find
an .ipk file at ```./build_dir/target-mips_r2_uClibc-0.9.33.2/OpenWrt-ImageBuilder-ar71xx_generic-for-Linux-i686/packages/tcpdump_4.2.1-1_ar71xx.ipk```. You can scp that ipk file to your various routers and run ```opkg install tcpdump_4.2.1-1_ar71xx.ipk```
to install the new binary!

#Benchmarks
All benchmarks run for 20 minutes on router 128.32.156.64, running custom build of tcpdump w/ built-in filter
 
```
tcpdump -tt -l -e -i wlan0 -s80 -y IEEE802_11_RADIO                                                 
 received: 1233115                                                                                   
 captured: 544811 (44.18%)
 dropped:  673710 (54.63%)
 
tcpdump -tt -l -e -i wlan0 -s80 -y IEEE802_11_RADIO -B40000 #increase buffer attempt                
 received: 3329535
 captured: 1180546 (33.46%)                                                                          
 dropped:  1956534 (58.76%)
     
tcpdump -tt -s80 -e -w - -U -i wlan0 #piped output                                                  
 received: 557045                                                                                    
 captured: 557038 (99.99%)
 dropped:  0
 
tcpdump -tt -e -i wlan0 -w - -U -s80 -y IEEE802_11_RADIO
 received: 2038849
 captured: 2038845 (99.99%)
 dropped: 0

tcpdump -tt -e -i wlan0 -w - -U -s80 -y IEEE802_11_RADIO #with print search optimization
 received: 885752
 captured: 885737 (99.99%)
 dropped: 0
```