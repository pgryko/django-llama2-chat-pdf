#!/bin/bash

# Update the package list
apt update

# Install Apache2
apt install -y apache2

# Install Docker
apt install -y docker.io

# Start Docker
systemctl start docker

# Enable Docker
systemctl enable docker

# Install Certbot (Let's Encrypt)
apt install -y software-properties-common
add-apt-repository ppa:certbot/certbot
apt update
apt install -y certbot python3-certbot-apache

# Generate the SSL certificate
certbot --apache --non-interactive --agree-tos --email piotr.gryko@gmail.com --domains chat.devalogic.co.uk

# Update Apache Configuration to enable ProxyPass for Django running on localhost:8000
echo "
<VirtualHost *:80>
  ServerName chat.devalogic.co.uk
  Redirect / https://chat.devalogic.co.uk/
</VirtualHost>

<VirtualHost *:443>
  ServerName chat.devalogic.co.uk

  SSLEngine On
  SSLCertificateFile /etc/letsencrypt/live/chat.devalogic.co.uk/fullchain.pem
  SSLCertificateKeyFile /etc/letsencrypt/live/chat.devalogic.co.uk/privkey.pem

  ProxyPreserveHost On
  ProxyPass / http://localhost:8000/
  ProxyPassReverse / http://localhost:8000/
</VirtualHost>
" > /etc/apache2/sites-available/chat-devalogic.co.uk.conf

# Enable the site and necessary modules
a2ensite chat-devalogic.co.uk
a2enmod proxy
a2enmod proxy_http
a2enmod ssl

# Reload Apache to apply changes
systemctl reload apache2
