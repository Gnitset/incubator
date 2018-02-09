#! /usr/bin/env python

import argparse
import BaseHTTPServer
import cgi
import os
import sys
import yaml

import ActiveDirectory

class WebUIRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self, msg=None, username="", domain=None):
		prev_domain = domain
		del domain
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write("""<html><head><title>AD password change</title></head><body>
<h2>AD password change</h2>""")
		if msg:
			self.wfile.write("""<h3 style="color: red">%s</h3>""" % msg)
		self.wfile.write("""<form method=post><fieldset>
<p><label for=username>Username</label><input type=text name=username value="%s"></p>
<p><label for=domain>Select domain</label><select name=domain>""" % username)
		if not prev_domain:
			self.wfile.write("""<option value="" selected disabled hidden>Select domain</option>""")
		else:
			self.wfile.write("""<option value="" disabled hidden>Select domain</option>""")
		for domain in self.config["domains"]:
			if domain != prev_domain:
				self.wfile.write("""<option value="%s">%s</option>""" % (domain, domain))
			else:
				self.wfile.write("""<option value="%s" selected>%s</option>""" % (domain, domain))
		self.wfile.write("""</select></p>
<p><label for=old_password>Current password</label><input type=password name=old_password autocomplete=off></p>
<p><label for=new_password1>New password</label><input type=password name=new_password1 autocomplete=off></p>
<p><label for=new_password2>Repeat new password</label><input type=password name=new_password2 autocomplete=off></p>
<p><input type=submit value="Change Password"></p>
</fieldset>
</form>
</body></html>""")

	def do_POST(self):
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader("content-type"))
			if ctype == "multipart/form-data":
				self._postvars = cgi.parse_multipart(self.rfile, pdict)
			elif ctype == "application/x-www-form-urlencoded":
				length = int(self.headers.getheader("content-length"))
				self._postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
			else:
				self._postvars = {}
			for field in ("username", "domain", "old_password", "new_password1", "new_password2"):
				if not (self._postvars.has_key(field) and len(self._postvars[field]) == 1 and len(self._postvars[field][0]) > 0):
					return self.do_GET(msg="Not all fields filled out", username=self._postvars.get("username",[None])[0], domain=self._postvars.get("domain",[None])[0])
			if self._postvars["new_password1"][0] != self._postvars["new_password2"][0]:
				return self.do_GET(msg="Passwords don't match", username=self._postvars.get("username",[None])[0], domain=self._postvars.get("domain",[None])[0])
			domain = self._postvars["domain"][0]
			if domain not in config["domains"]:
				print "Domain not configured", domain
				return self.do_GET(msg="Domain not configured", username=self._postvars["username"][0])
			ad = ActiveDirectory.ActiveDirectory(config["domains"][domain]["server"], domain)
			ad.bind(self._postvars["username"][0], self._postvars["old_password"][0])
			ad.change_password(self._postvars["old_password"][0], self._postvars["new_password1"][0])
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write("""<html><head><title>AD password change</title></head><body><h2>Password for %s in domain %s changed successfully.</h2></body></html>""" %
				(self._postvars["username"][0], domain)
			)
		except ActiveDirectory.ldap.SERVER_DOWN:
			self.send_response(500)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write("""<html><head><title>AD password change</title></head><body><h2>%s</h2></body></html>""" %
				"LDAP Server down"
			)
		except ActiveDirectory.ldap.INVALID_CREDENTIALS:
			return self.do_GET(msg="Authentication failed. Wrong password?", username=self._postvars["username"][0], domain=domain)
		except ActiveDirectory.ldap.CONSTRAINT_VIOLATION:
			self.send_response(500)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write("""<html><head><title>AD password change</title></head><body><h2>%s</h2></body></html>""" %
				"CONSTRAINT_VIOLATION: You are not allowed to change your password. Please contact support."
			)
		except:
			self.send_response(500)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write("""<html><head><title>AD password change</title></head><body><h2>Something failed, look in the logs.</h2></body></html>""")
			print sys.exc_info()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Web interface to change AD passwords")
	parser.add_argument("-c", dest="config", default="config.yml")
	parser.add_argument("-p", dest="port", default=8000, type=int)
	args = parser.parse_args()

	config = yaml.load(file(args.config))
	WebUIRequestHandler.config = config

	print "Listening on *:%s" % args.port
	httpd = BaseHTTPServer.HTTPServer(("", args.port), WebUIRequestHandler)
	httpd.serve_forever()
