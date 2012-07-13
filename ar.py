import router
r= router.Router('128.32.156.64','asdf')
r2=router.Router('128.32.156.67','asdf')

a = router.RouterList(r,r2)

a.uname()
a.kill_tcpdump()
a.set_channel('wlan0',1)
#a.run_tcpdump('wlan0','f8:0c:f3:1d:16:49')
