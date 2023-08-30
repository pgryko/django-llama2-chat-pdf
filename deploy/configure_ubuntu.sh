#!/bin/bash

# Update the package list
apt update

# Install Apache2
apt install -y apache2

# Install Docker

apt install -y install ca-certificates curl gnupg

install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update

apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
systemctl start docker

# Enable Docker
systemctl enable docker

# Verify it works
docker run hello-world

# Install Certbot (Let's Encrypt)
apt install -y software-properties-common snapd
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

# Generate the SSL certificate
certbot --apache --non-interactive --agree-tos --email youremail.com --domains yourdomain.com

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
