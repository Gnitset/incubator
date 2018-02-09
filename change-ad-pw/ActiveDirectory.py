#! /usr/bin/env python2.7

import datetime
import ldap

class ActiveDirectory(object):
	def __init__(self, server, domain):
		self.domain = domain
		self._connected = False
		self._ldap = ldap.initialize(server)
		self._ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
		self._ldap.set_option(ldap.OPT_X_TLS_NEWCTX, 0)

	def bind(self, username, password):
		self.username = username
		self._ldap.simple_bind_s("%s@%s" % (self.username, self.domain), password)
		self._connected = True

	def _encode_password(self, password):
		return ("\"%s\"" % password).encode("utf-16-le")

	def _find_user(self, username="*"):
		base = ",".join(map(lambda s: "DC="+s, self.domain.split(".")))
		return self._ldap.search_s(base, ldap.SCOPE_SUBTREE,
			"(&(objectCategory=person)(objectClass=user)(sAMAccountName=%s))" % username)

	def win32_to_unix_epoch(self, win32_timestamp):
		ticks_per_sec = 10000000.0
		seconds_between_the_epochs = 11644473600.0
		return ( win32_timestamp / ticks_per_sec ) - seconds_between_the_epochs

	def change_password(self, old_password, new_password):
		if not self._connected:
			raise Exception("Not connected")
		from_password = self._encode_password(old_password)
		to_password = self._encode_password(new_password)
		search_result = filter(lambda r: r[0] != None, self._find_user(self.username))
		if len(search_result) != 1:
			raise Exception("Wrong amount of search results: %s" % search_result)
		user_dn = search_result[0][0]
		self._ldap.modify_s(user_dn, [(ldap.MOD_DELETE, "unicodePwd", from_password),
		                              (ldap.MOD_ADD, "unicodePwd", to_password)])

	def get_users_with_expired_passwords(self, max_days=90, days_left=0):
		assert self._connected
		now = datetime.datetime.now()
		expiry_interval = datetime.timedelta(days=max_days)
		days_left_interval = datetime.timedelta(days=days_left)
		ret = dict()
		for user in self._find_user("*"):
			if user[0] == None: continue
			userAccountControl = int(user[1]["userAccountControl"][0])
			if userAccountControl & 0x2: # ACCOUNTDISABLE
				continue
			if userAccountControl & 0x20: # PASSWD_NOTREQD (Must change at next logon)
				continue
			if userAccountControl & 0x40: # PASSWD_CANT_CHANGE
				continue
			if userAccountControl & 0x10000: # DONT_EXPIRE_PASSWORD
				continue
			password_last_change_ts = self.win32_to_unix_epoch(float(user[1]["pwdLastSet"][0]))
			password_last_change = datetime.datetime.fromtimestamp(password_last_change_ts)
			if ( password_last_change + expiry_interval ) < ( now + days_left_interval ):
				ret[user[0]] = user[1]
				ret[user[0]]["daysToExpiry"] = (password_last_change + expiry_interval - now)
		return ret
