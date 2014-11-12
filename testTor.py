#!/usr/bin/env python3

import socket
import socks
def create_connection(address, timeout=None, source_address=None):
	sock = socks.socksocket()
	sock.connect(address)
	return sock
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
socket.socket = socks.socksocket
socket.create_connection = create_connection

import urllib.request
from urllib.parse import urlencode

testURL = input("What's the test site (maybe try http://checkip.dyndns.com/)? ")
print("Method 1")
with urllib.request.urlopen(testURL) as f:
	dat = f.read()
	print(dat)

print("See if that address is a tor exit node (google \"address\" exit node)")

class NoRedirection(urllib.request.HTTPErrorProcessor):
	def http_response(self, request, response):
		return response
	
	https_response = http_response

opener = urllib.request.build_opener(NoRedirection)

print("Method 2")
with opener.open(testURL) as f:
	dat = f.read()
	print(dat)

print("See if that address is a tor exit node (google \"address\" exit node)")
