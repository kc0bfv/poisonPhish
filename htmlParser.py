import random
import string

from collections import defaultdict
from html.parser import HTMLParser, HTMLParseError
from urllib.parse import urlencode

class Form():
	def __init__(self, pageURL):
		self.pageURL = pageURL # The URL the form comes from

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

	@property
	def absAction(self):
		# Build the absolute URL for the form's "action" - resolve relative URLs
		if self.action.startswith("http"):
			return self.action
		else:
			baseURL = self.pageURL[0:self.pageURL.rindex("/")]
			return baseURL + "/" + self.action

	def buildData(self, fieldsToInject, randInjectLen=524288, fakeEmail=True):
		# Build the data that this form sends in a GET or POST request
		def getShortRandStr():
				return getRandStr(random.randrange(10,15))
		def getLongRandStr(injectLen=None):
				return getRandStr(randInjectLen)
		def getRandStr(injectLen):
			return "".join(random.choice(string.ascii_uppercase +
				string.ascii_lowercase + string.digits)
				for _ in range(injectLen))

		suffix = ""
		if fakeEmail:
			suffix = "@" + getShortRandStr() + ".com"

		dataTuples = list()
		for (name, value) in self.hiddenFields.items():
			dataTuples.append((name, value))
		for name in self.textFields:
			if name in fieldsToInject:
				dataTuples.append((name, getLongRandStr()+suffix))
			else:
				dataTuples.append((name, getShortRandStr()+suffix))
		for name in self.passwordFields:
			if name in fieldsToInject:
				dataTuples.append((name, getLongRandStr()+suffix))
			else:
				dataTuples.append((name, getShortRandStr()+suffix))

		return urlencode(dataTuples)

class PhishForms(HTMLParser):
	def __init__(self, pageURL):
		self.pageURL = pageURL # The URL the html comes from

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
				self.currentForm = Form(self.pageURL)
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
	
	def finishPageParsing(self):
		# This function will wrap up page processing, gracefully handling cases where the HTML didn't include a closing form tag, or even where we didn't get some of the page
		# It's not needed for properly formatted, completely retrieved pages
		if self.currentForm is not None:
			self.forms.append(self.currentForm)
			self.currentForm = None
