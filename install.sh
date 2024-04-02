#!/bin/bash

# Exit script on error
set -e

# Define variables
PROJECT_DIR="/qmxStatus"
PROJECT_USER="qmxUser"
SERVICE_NAME="qmxStatus.service"
APP_MODULE="app:app" # Replace 'your_flask_app:app' with your actual app module and Flask instance
CRON_JOB="@hourly cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python $PROJECT_DIR/scraper.py"

# Ensure running as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Install virtualenv globally
pip install virtualenv

# Create a new system user for the application (without home directory)
useradd --system --no-create-home $PROJECT_USER || true

# Change ownership of the project directory
chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR

# Navigate to the project directory
cd $PROJECT_DIR

# Create a Python virtual environment using virtualenv and activate it
virtualenv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install gunicorn flask requests beautifulsoup4

# Deactivate the virtual environment
deactivate

# Create a systemd service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
echo "[Unit]
Description=Gunicorn instance to serve my Flask app
After=network.target

[Service]
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/qmxStatus.sock $APP_MODULE

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE

# Reload systemd to apply new service file, enable and start the service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

# Setup Nginx as a reverse proxy
apt update
apt install nginx -y
NGINX_CONF="/etc/nginx/sites-available/$SERVICE_NAME"
echo "server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://unix:$PROJECT_DIR/qmxStatus.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}" > $NGINX_CONF
ln -s $NGINX_CONF /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Setup cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Installation completed successfully."
