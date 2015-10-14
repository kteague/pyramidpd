pyramidpd
=========

This is the back end to the Passport Date application. It consists of
a Pyramid Python 3 web application acting as a JSON API. There are also
files to manage the PostgreSQL database in this project. As well as notes
on setting up a reverse proxy and other deployment related bits.

You will need emberpd to serve the front end.


Getting Started
---------------

- Get some Python 3. Preferably Python 3.5.
  
- To install Python packages and set-up: python setup.py develop

- Install a PostgreSQL database and set the DSN in development.ini

- To initialize database: initialize_pd_db development.ini

- Set-up a ReverseProxy to deal with CORS issues.

  This is the configuration used to run behind Apache 2 on Mac OS X.
  Add this to /etc/apache2/httpd.conf

# Always set these headers.                                                                             Header always set Access-Control-Allow-Origin "*"
Header always set Access-Control-Allow-Methods "POST, GET, OPTIONS, DELETE, PUT"
Header always set Access-Control-Max-Age "1000"
Header always set Access-Control-Allow-Headers "x-requested-with, Content-Type, origin, authorization, accept, client-security-token"

# Added a rewrite to respond with a 200 SUCCESS on every OPTIONS request.                               RewriteEngine On
RewriteCond %{REQUEST_METHOD} OPTIONS
RewriteRule ^(.*)$ $1 [R=200,L]


# proxy config for Ember and Pyramid                                                                    <IfModule mod_proxy.c>
  ProxyRequests on
  ProxyPreserveHost on

  ProxyPass /api/1 http://0.0.0.0:6543/api/1
  ProxyPassReverse /api/1 http://0.0.0.0:6543/api/1

  ProxyPass / http://0.0.0.0:4200/
  ProxyPassReverse / http://0.0.0.0:4200/
</IfModule>


- Set-up a local mail rely to enable sign-up functionality. For Mac OS X edit /etc/postfix/main.cf
and add:

	relayhost=smtp.gmail.com:587
	# Enable SASL authentication in the Postfix SMTP client.                                            smtp_sasl_auth_enable=yes
	smtp_sasl_password_maps=hash:/etc/postfix/sasl_passwd
	smtp_sasl_security_options=noanonymous
	smtp_sasl_mechanism_filter=plain
	# Enable Transport Layer Security (TLS), i.e. SSL.                                                  smtp_use_tls=yes
	smtp_tls_security_level=encrypt
	tls_random_source=dev:/dev/urandom

 Then add an account to /etc/postfix/sasl_passwd:
 
	smtp.gmail.com:587 your_email@gmail.com:your_password

 Create the password file:
 
	postmap /etc/postfix/sasl_passwd

 Then start/restart postfix:
  
    postfix start
	postfix reload

 Test it and debug it:

	date | mail -s testing your_email@gmail.com
	tail -n 100 /var/log/mail.log


- To serve it all up!

 $ pg_ctl start
 $ ember serve
 $ pserve development.ini


Have fun, kids!
