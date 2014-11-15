#!/usr/bin/env python3

import connectionStuff as cs

#testURL = input("What's the test site (maybe try http://checkip.dyndns.com/)? ")
testURL = "https://check.torproject.org"
with cs.noRedirectOpener.open(testURL) as f:
	dat = f.read()
	#print(dat)
	if b"Congratulations" in dat:
		print("Tor is working according to check.torproject.org")
	else:
		print("Tor doesn't seem to be working properly")

#print("See if that address is a tor exit node (google \"address\" exit node)")
