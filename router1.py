import fingerprint
r=fingerprint.RSSIReader(10,log_dest='zone4.db',server='128.32.156.45',opsys='linux')
r.start(number=100)
