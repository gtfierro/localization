To set up a computer to run the localization piece, do the following


1. Run the redis server with the default settings
    
    ```
    redis-server
    ```


2. Run the flask web-server to see Anthony's pretty interface (and to see where everything is)

    (from localization/mapdemo)
    
    ```
    python app.py
    ```

3. Prepare your configuration file for your network. This is a text file containing two types of entries.
   
    ```
    bssid <mac-address>   #identifies the BSSID for one of the routers on your network. This assists in filtering
        -- or --
    router <mac-address> <ip-address> <x-coord> <y-coord> #mac address, ip address and x-coord,y-coord for a router
                                                          #with relation to the floor map

    ```

4. Run the localization script!

    ```
    python geo.py <path-to-configuration-file>
    ```

5. Start adding client mac addresses via some redis client (details coming soon), or by waiting for Andrew's arp-thing
   to take care of this automagically


6. Visit localhost:8000 to see where everything is



## To Configure OpenWRT routers 

Firstly, make sure they have libpcap and tcpdump installed! The .ipk files for those are included in this repository, so you can 
install them by copying them over to the router, and then running

```
opkg install libpcap_1.1.1-2_ar71xx.ipk
opkg install tcpdump_4.2.1-1_ar71xx.ipk
```

Then, we want to disable the firewall so we can use SSH:

```
/etc/init.d/firewall stop
/etc/init.d/firewall disable
reboot
```

Then you should be good to go!


## Redis Store

Brief rundown of what we have in the redis db.

### Sets

`macs`: list of all mac addresses we are attempting to localize. Populated by [arp_process.py](https://github.com/gtfierro/localization/blob/master/occupancy/router/arp_process.py)

### Hashes

`macip`: hash of key: mac address, value: ip address. Items are never deleted from this hash

`ipmac`: hash of key: ip address, value: mac address. Items are never deleted from this hash

`client_location`: hash of key: mac address, value: json string with keys of ['x','y','ip']. At each timestep, the hash from mac address to json-string only exists if we received data (packets) from that mac address. If a previously seen mac address does not have any data for a given timestep, we remove the hash for that address.