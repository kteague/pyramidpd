Passport Date web application
=============================

So you want to hack on this web app?

Getting Started
---------------

- Get node.js (v0.12.7+): https://nodejs.org/

- Install ember:
  # npm install -g ember-cli
  # npm install -g phantomjs2
  
- (optional) Install watchman: https://facebook.github.io/watchman/docs/install.html
  
- To install Python packages and set-up: ./bin/python setup.py develop

- Install a PostgreSQL database and set the DSN in development.ini

- To initialize database: ./bin/initialize_pd_db development.ini

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


- To serve it all up!

 $ pg_ctl start
 $ ember serve
 $ pserve development.ini


Have fun, kids!
