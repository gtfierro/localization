import fingerprint
r=fingerprint.RSSIReader(10,log_dest='mac.db')
r.start_sampling(number=50)
