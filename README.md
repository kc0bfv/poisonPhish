Alright!  So you wanna help some phishers out?  Same here.  First install tor and get it running (run "tor" and it'll start up a socks proxy that this software connects to on port 9050).  Then run "./poisonPhish.py" and enter the URL the phishing links sent you to - the one with the username and password page.  The software will scrape it for the username/password elements, let you select which fields you want to fish, then every 30 seconds insert .5 Mb of random characters into those fields and send it off.  Fun, eh?

That data will get dumped to the phisher's file or sent to their email address.  They'll get to learn exactly what your random number generator is spitting out...  I'm sure that's what they were really interested in.

Also - if you're worried about whether TOR is working, I included testTor.py as a way to test it out...  It tests both url-getting methods I used, but both outputs should be the same.


SocksiPy was created by Dan Haim, for Python2.  I did some initial 2-3 conversion, and had to change a lot of stuff in addition to the 2-3 changes.  There are things in there that I didn't change properly (URLs with ports in them, for example, seem to be broken).