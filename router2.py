import fingerprint
r=fingerprint.RSSIReader(10,log_dest='router1.db',server='128.32.156.131',opsys='linux')
r.start_sampling(number=700)
