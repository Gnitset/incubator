AD Password change/reminder
===========================

A small with a web interface to change passwords in Active Directory.
And a script to cron to send out email reminders before password expires.

To change password in AD over ldap requires encrypted ldaps.
If you dont have a working certificate on your server you can run `SelfSignedCert.ps1` to create a self signed one.

The only dependencies are `python2.7` and `python-ldap`.
