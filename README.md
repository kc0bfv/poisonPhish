# Intro
Let's give some phishers the information they seek - a bunch of randomly generated usernames and passwords!  Better - let's do it over Tor so we'll just be an anonymous contributer to their project, and it'll be harder to stop our valuable contributions.   you want to fish, then every 30 seconds insert .5 Mb of random characters into those fields and send it off.  Fun, eh?

# Setup
Install [Tor](https://www.torproject.org/), then run "tor"

# Use
Run ./poisonPhish.py and follow the prompts.  Specify the webpage the phisher has the username/password prompts on.

# Optional
Run ./poisonPhish.py to see command line options.  By default we'll send .5 MB long usernames and passwords that look (a little) like (really big) email addresses.  It sends that large username/password pair every 30 seconds.  The command line options change those parameters.

# Goal
That data will get dumped to a file on the phisher's box, or sent to their email address.  They'll get to learn exactly what your random number generator is spitting out...  I'm sure that's what they were really interested in.

# Are You Sure Tor Is Working?
If you're worried about whether Tor is working run `testTor.py`.

# Thanks
This uses SocksiPy which was created by Dan Haim, for Python2.  I did some initial 2-3 conversion, and had to change a lot of stuff in addition to the 2-3 changes.  There are things in there that I didn't change properly (URLs with ports in them, for example, seem to be broken).

# TODO
Use PySocks instead of SocksiPy.  Maybe.
