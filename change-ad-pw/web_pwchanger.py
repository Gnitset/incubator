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
		self.wfile.write("""<html><head><title>AD password change</title><link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">
<style>*, ::after, ::before {box-sizing: border-box;} body {font-family: 'Lato', sans-serif;} h2 {text-align:center} .box {margin:10px 20px} .box__border {border-radius:10px; padding: 20px;}
.form__control {display: block; width: 100%; padding: .375rem .75rem; font-size: 1rem; line-height: 1.5; color: #495057;
background-color: #fff; background-clip: padding-box; border: 1px solid #ced4da; border-radius: .25rem; transition: border-color .15s ease-in-out,box-shadow .15s ease-in-out;}
.form__control:focus {color: #495057; background-color: #fff; border-color: #80bdff; outline: 0; box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);} .row {display: flex; flex-wrap: wrap}
.col {flex: 0 1 50%; padding:5px;} .btn { color: #fff; background-color: #007bff; border-color: #007bff; display: inline-block; font-weight: 400; text-align: center; white-space: nowrap; vertical-align: middle; user-select: none; border: 1px solid transparent;
padding: .375rem .75rem; font-size: 1rem; line-height: 1.5; border-radius: .25rem; transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;}
.btn:hover {color: #fff; background-color: #0069d9; border-color: #0062cc; text-decoration: none;}
.form__select {display: inline-block; width: 100%; height: calc(2.25rem + 2px); padding: .375rem 1.75rem .375rem .75rem; line-height: 1.5; color: #495057; vertical-align: middle;
background-size: 8px 10px; border: 1px solid #ced4da; border-radius: .25rem; appearance: none;}
.form__select:focus {border-color: #80bdff; outline: 0; box-shadow: inset 0 1px 2px rgba(0,0,0,.075), 0 0 5px rgba(128,189,255,.5);}
.alert {margin: 1rem 20px 0 20px; color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; position: relative; padding: .75rem 1.25rem; margin-bottom: 1rem; border: 1px solid transparent; border-radius: .25rem;}
select {margin: 0; font-family: inherit; font-size: inherit; line-height: inherit;}
</style></head><body>
<h2>AD password change</h2>""")
		if msg:
			self.wfile.write("""<div class="alert" role="alert">%s</div>""" % msg)
		self.wfile.write("""<form class="box" method=post><fieldset class="box__border">
<div class="row">
	<div class="col"><input class="form__control" type=text name=username value="%s" placeholder="Username"></div>
	<div class="col"><input class="form__control" type=password name=old_password autocomplete=off placeholder="Current password"></div>
</div>
<div class="row">
	<div class="col"><input class="form__control" type=password name=new_password1 autocomplete=off placeholder="New password"></div>
	<div class="col"><input class="form__control" type=password name=new_password2 autocomplete=off placeholder="Repeat new password"></div>
</div>
<div class="row">
	<div class="col"><select class="form__select" name=domain>""" % username)
		if not prev_domain:
			self.wfile.write("""<option value="" selected disabled hidden>Select domain</option>""")
		else:
			self.wfile.write("""<option value="" disabled hidden>Select domain</option>""")
		for domain in self.config["domains"]:
			if domain != prev_domain:
				self.wfile.write("""<option value="%s">%s</option>""" % (domain, domain))
			else:
				self.wfile.write("""<option value="%s" selected>%s</option>""" % (domain, domain))
		self.wfile.write("""</select></div>
		<div class="col"><input class="form__control btn" type=submit value="Change Password"></div>
</div>
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
