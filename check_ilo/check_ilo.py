#! /usr/bin/env python

import argparse
import ssl
import sys
import urllib2
import xml.etree.ElementTree

class iLO(object):
	def __init__(self, host, user_pass, ssl_context = ssl._create_default_https_context):
		self.host = host
		self.user_pass = user_pass
		self.ssl_context = ssl_context

class iLO3(iLO):
	_request = """<RIBCL VERSION="2.21">
<LOGIN USER_LOGIN="%s" PASSWORD="%s">
<SERVER_INFO MODE="read">
<GET_EMBEDDED_HEALTH />
</SERVER_INFO>
</LOGIN>
</RIBCL>"""

	def fetch(self):
		text_request = self._request % self.user_pass
		request = urllib2.Request("https://%s/ribcl" % self.host, text_request)
		response = urllib2.urlopen(request, context=self.ssl_context())
		self._response = response.read().split("<?xml version=\"1.0\"?>")
		ilo.dom = [xml.etree.ElementTree.fromstring(data) for data in ilo._response if "GET_EMBEDDED_HEALTH_DATA" in data][0]

class iLO4(iLO):
	def fetch(self):
		pass

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Check HW health via ilo")
	parser.add_argument("-H", dest="host", required=True, help="host to check")
	parser.add_argument("-k", dest="ssl_verify", default=True, action="store_false", help="verify ssl-certificate")
	parser.add_argument("-u", dest="user", required=True, help="username")
	parser.add_argument("-p", dest="password", required=True, help="username")
	parser.add_argument("-3", dest="ilo3", default=False, action="store_true", help="access iLO3")
	args = parser.parse_args()
	if len(sys.argv) < 1:
		parser.print_help()
		sys.exit(1)

	if args.ssl_verify:
		ssl_context = ssl._create_default_https_context
	else:
		ssl_context = ssl._create_unverified_context

	if args.ilo3:
		iLO = iLO3
	else:
		iLO = iLO4

	ilo = iLO(args.host, (args.user, args.password), ssl_context)

	ilo.fetch()
	for Z in ilo._response:
		print Z

	for temp in ilo.dom.findall("GET_EMBEDDED_HEALTH_DATA/TEMPERATURE/TEMP"):
		location = temp.find("LOCATION")
		status = temp.find("STATUS")
		print location.attrib['VALUE'], status.attrib['VALUE']
