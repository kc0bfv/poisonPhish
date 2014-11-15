# This section here sets up the socks proxy connection
# TODO: allow non-default TOR settings like port and IP
import socket
import socks
def create_connection(address, timeout=None, source_address=None):
	sock = socks.socksocket()
	try:
		sock.connect(address)
	except ConnectionRefusedError:
		raise ConnectionRefusedError("Could not connect to TOR proxy")
	return sock

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
socket.socket = socks.socksocket
socket.create_connection = create_connection


# By importing this later on, the proxy settings take hold
import urllib.request, urllib.error


class NoRedirection(urllib.request.HTTPErrorProcessor):
	def http_response(self, request, response):
		return response
	
	https_response = http_response

# This will be an object with a .open function that won't get redirected
noRedirectOpener = urllib.request.build_opener(NoRedirection)


# Map the errors we need later to something easier to use
Socks5Error = socks.Socks5Error
URLError = urllib.error.URLError
