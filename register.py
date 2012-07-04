import sys
import urllib2
url = 'http://green.millennium.berkeley.edu:8081/reg/%s' % sys.argv[1]
print url
f = urllib2.urlopen(url)
