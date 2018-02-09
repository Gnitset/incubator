#! /usr/bin/env python27

import argparse
from email.mime.text import MIMEText
import smtplib
import yaml

import ActiveDirectory

error_log = list()

def mail_reminder(domain, name, email, days_left):
	global config, verbose, noop
	if verbose:
		print name, email, days_left
	if noop:
		return
	if not email:
		error_log.append((domain,name,days_left))
		return
	if days_left.days < 0:
		error_log.append((domain,name,email,days_left))
		return
	return
	msg = MIMEText("""Hi %s,

Your password in the %s domain expires in %s.
If you dont know how to fix this, please contact it-support.

Best regards
Your friendly Password Reminder""" % (name,domain,days_left))

	msg["Subject"] = "Password expiring - %s" % domain
	msg["From"] = "%s <%s>" % (config["mail"]["from_name"], config["mail"]["from_mail"])
	msg["To"] = "%s <%s>" % (name, email)

	s = smtplib.SMTP(config["mail"]["server"])
	s.sendmail(msg["From"], [msg["To"]], msg.as_string())
	s.quit()


if __name__ == "__main__":
	global config, verbose, noop
	parser = argparse.ArgumentParser(description="Send email reminders for expiring passwords in AD")
	parser.add_argument("-c", dest="config", default="config.yml")
	parser.add_argument("-d", dest="domains", nargs="+")
	parser.add_argument("-n", dest="noop", action="store_true")
	parser.add_argument("-v", dest="verbose", action="store_true")
	args = parser.parse_args()

	config = yaml.load(file(args.config))
	verbose, noop = args.verbose, args.noop
	if args.domains:
		for domain in config["domains"].keys():
			if domain not in args.domains:
				del config["domains"][domain]

	for domain, domain_info in config["domains"].iteritems():
		if verbose:
			print domain
		ad = ActiveDirectory.ActiveDirectory(domain_info["server"], domain)
		ad.bind(domain_info["user"], domain_info["password"])
		expired_users = ad.get_users_with_expired_passwords(domain_info["password_max_days"], domain_info["password_days_left"])
		for user, user_data in expired_users.iteritems():
			mail_reminder(domain, user_data["name"][0], user_data.get("mail",[None])[0], user_data["daysToExpiry"])

	msg = MIMEText("Hi\n\nThese failed while sending password reminders\n"+"\n".join(("'%s'" % "', '".join(map(str, e_msg)) for e_msg in error_log)))

	msg["Subject"] = "Password expiry reminder - failues"
	msg["From"] = "%s <%s>" % (config["mail"]["from_name"], config["mail"]["from_mail"])
	msg["To"] = "<%s>" % (config["mail"]["error_recipient"])

	s = smtplib.SMTP(config["mail"]["server"])
	s.sendmail(msg["From"], [msg["To"]], msg.as_string())
	s.quit()
