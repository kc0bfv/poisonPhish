#!/usr/bin/env python3

import time
import argparse
import itertools

# connectionStuff will setup the Tor proxy and import urllib...
import connectionStuff as cs
# htmlParser handles all the parsing
from htmlParser import PhishForms

# Parse any arguments
parser = argparse.ArgumentParser(description="Mess with phishers")
parser.add_argument("-b", "--bytes", type=int, default=524288,
		help="The number of bytes to put in each text and password field")
parser.add_argument("-s", "--sendFreq", type=int, default=30,
		help="The number of seconds to wait between each send attempt")
parser.add_argument("-ne", "--no-email", action="store_const", const=True,
		default=False, help="Don't make inputs look like email addresses")

args = parser.parse_args()


phishURL = input("What's the phishing site? ")

# Grab the site's HTML and parse it
pf = PhishForms(phishURL)
try:
	with cs.noRedirectOpener.open(phishURL) as f:
		dat = f.read()
		#print(dat[0:40]) # Can help with debugging
		pf.feed(dat.decode("ascii")) # This does all the HTML parsing
	pf.finishPageParsing()
except cs.URLError as e:
	print("ERROR:", e.reason)
	exit(1)
except cs.Socks5Error as e:
	print("ERROR: Proxy error:", str(e))
	exit(2)
except ValueError as e:
	print("ERROR:", e)
	exit(3)




###### Start the UI stuff for selecting what to inject ######
forms = pf.forms
enumForms = list(enumerate(forms))

# Select the form to inject
formNumber = -1
while formNumber not in range(len(enumForms)):
	print("Which form is the phisher using?")
	for (index, form) in enumForms:
		print(index, ". ", form)
		print("\n\n")

	try:
		formNumber = int(input("Form number: "))
	except ValueError:
		formNumber = -1

form = forms[formNumber]
injectFields = list()

# Select the text field to inject
textFieldNum = -1
while textFieldNum not in range(len(form.textFields)+1):
	print("Form number ", formNumber, "! Which text field do you want to mess with?")
	for (index, field) in enumerate(form.textFields):
		print(index, ". ", field)

	print(len(form.textFields),". No Text Field")

	try:
		textFieldNum = int(input("Field number: "))
	except ValueError:
		formNumber = -1

try:
	injectFields.append(form.textFields[textFieldNum])
except IndexError:
	pass # Anything down here should indicate "no text field desired"

# Select the password field to inject
passwordFieldNum = -1
while passwordFieldNum not in range(len(form.passwordFields)+1):
	print("Form number ", formNumber, "! Which password field do you want to mess with?")
	for (index, field) in enumerate(form.passwordFields):
		print(index, ". ", field)

	print(len(form.passwordFields),". No Password Field")

	try:
		passwordFieldNum = int(input("Field number: "))
	except ValueError:
		formNumber = -1

try:
	injectFields.append(form.passwordFields[passwordFieldNum])
except IndexError:
	pass # Anything down here should indicate "no password field desired"




###### This stuff builds the data to send and sends it ######

# Setup the url opener parameters
url = form.absAction
if form.postOrGet == "get":
	url += "?" + form.buildData(injectFields, args.bytes, not args.no_email)
	data = None
else:
	data = bytes(form.buildData(injectFields, args.bytes, not args.no_email),
			"ascii")

try:
	for sendIter in itertools.count(0):
		print("Sending Iteration Number:", sendIter)

		try:
			with cs.noRedirectOpener.open(url, data) as f:
					retval = f.read()
		except Exception as e:
			print("  ERROR:", e)
		else:
			if len(data) < 2048:
				print("  Sent", len(data), "B")
			else: 
				print("  Sent", round(len(data)/1024), "KB")
			print("  Returned", len(retval), "bytes (redirections usually return 0)")
			print("  Sleeping", args.sendFreq, "seconds")

		time.sleep(args.sendFreq)
except KeyboardInterrupt:
	pass # Just allow the program to quit on ctrl+c without python barf
