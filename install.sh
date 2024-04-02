#!/bin/bash

# Exit script on error
set -e

# Define variables
OLD_PROJECT_DIR="/root/qmxStatus"
NEW_PROJECT_DIR="/opt/qmxStatus"
PROJECT_USER="qmxUser"
SERVICE_NAME="qmxStatus"
APP_MODULE="app:app"
CRON_JOB="@hourly cd $NEW_PROJECT_DIR && $NEW_PROJECT_DIR/venv/bin/python $NEW_PROJECT_DIR/scraper.py"

# Automatically retrieve the server's public IP address
SERVER_IP=$(curl -s http://checkip.amazonaws.com)

# Ensure running as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Install virtualenv globally
pip install virtualenv

# Create a new system user for the application (without home directory)
useradd --system --no-create-home $PROJECT_USER || true

# Move the project directory
mv $OLD_PROJECT_DIR $NEW_PROJECT_DIR

# Change ownership of the new project directory
chown -R $PROJECT_USER:$PROJECT_USER $NEW_PROJECT_DIR

# Navigate to the new project directory
cd $NEW_PROJECT_DIR

# Create a Python virtual environment using virtualenv and activate it
virtualenv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install gunicorn flask requests beautifulsoup4 numpy scipy scikit-learn

# Initialize the database by running init_db.py
python $NEW_PROJECT_DIR/init_db.py

# Run the scraper script immediately after installation
python $NEW_PROJECT_DIR/scraper.py

# Deactivate the virtual environment
deactivate

# Create a systemd service file for Gunicorn
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
echo "[Unit]
Description=Gunicorn instance to serve my Flask app
After=network.target

[Service]
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$NEW_PROJECT_DIR
ExecStart=$NEW_PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$NEW_PROJECT_DIR/$SERVICE_NAME.sock $APP_MODULE

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE

# Reload systemd to apply new service file, enable and start the service
systemctl daemon-reload
systemctl enable $SERVICE_NAME.service
systemctl start $SERVICE_NAME.service

# Setup Nginx as a reverse proxy
apt update
apt install nginx -y
NGINX_CONF="/etc/nginx/sites-available/$SERVICE_NAME"
echo "server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://unix:$NEW_PROJECT_DIR/$SERVICE_NAME.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}" > $NGINX_CONF

# Ensure no faulty symlink exists and create a correct symlink
rm -f /etc/nginx/sites-enabled/$SERVICE_NAME
ln -s $NGINX_CONF /etc/nginx/sites-enabled/

# Test Nginx configuration and reload if successful
nginx -t && systemctl reload nginx

# Setup UFW firewall
ufw allow 80
ufw --force enable

# Setup cron job for qmxUser
CRON_JOB="@hourly cd $NEW_PROJECT_DIR && $NEW_PROJECT_DIR/venv/bin/python $NEW_PROJECT_DIR/scraper.py >> $NEW_PROJECT_DIR/cron.log 2>&1"
(crontab -u $PROJECT_USER -l 2>/dev/null; echo "$CRON_JOB") | crontab -u $PROJECT_USER -

echo "Installation completed successfully."
