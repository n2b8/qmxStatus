# KF0BDW's QMX Position Tracker

## Overview

I recently ordered a QMX 5w multi-band/multi-mode transceiver from QRP-Labs. Due to life, I didn't have time to asseble the unit myself so I ordered the factory assembled kit along with a GPS module/board that is currently out of stock. To my understanding, the wait time is in the realm of 6-8 months. The backend of this program will scrape QRP-Labs' shipping status page watching for my order and updating the position in line into a SQLite3 database. The front end is a Flask application which tracks and displays the position of an order over time. The application updates the position data hourly using a scheduled script.

## Features

- **Data Scraping:** Automatically scrapes the web for order position data.
- **Data Visualization:** Displays the order position history on a line graph.
- **Automatic Updates:** Uses cron jobs to periodically update the order position.

## Coming Soon

- **Forecasting:** Once I have a few datapoints to work with, I'll implement a regressor to attempt to predict when my unit will be completed.
- **Notifications:** I may implement Twilio to send me an SMS notification when my position in line changes. Not positive I'll do that yet.

## Getting Started

### Prerequisites

- Python 3
- Flask
- SQLite3
- Requests
- BeautifulSoup4

### Installation
**Be sure to install as root. Don't worry, the install script will create a new user and move into that user's profile before continuing.**

1. **Clone the repository** to your local machine.
    ```bash
    git clone https://github.com/n2b8/qmxStatus.git
    ```
2. **Navigate to the project directory.**
    ```bash
    cd qmxStatus
    ```
3. **Make the install script executable.**
    ```bash
    chmod +x install.sh
    ```
4. **Run the install script.** This script will set up the virtual environment, install necessary dependencies, configure the Nginx server, and set up the cron job for periodic scraping.
    ```bash
    ./install.sh
    ```

### Configuration

- The installation script handles most of the configuration automatically, including setting up the virtual environment, installing dependencies, and configuring Nginx with UFW to open port 80.
- **Update the Order Number:** To track a specific order number, you may need to update the `fetch_order_position` function in the `scraper.py` file with your desired order number.

    ```python
    position = fetch_order_position(YOUR_ORDER_NUMBER_HERE)
    ```
    Replace `YOUR_ORDER_NUMBER_HERE` with the actual order number you wish to track.

### Running the Application

After installation and configuration, your Flask application is set to run with Gunicorn and Nginx serving as a reverse proxy. The cron job for scraping is also scheduled to run hourly.

- **Accessing the Application:** Open a web browser and navigate to `http://<your-server-ip>` to view your application. Replace `<your-server-ip>` with the actual IP address of your server.

### Monitoring and Logs

- **Application Logs:** Check the application logs at `/path/to/qmxStatus/scraper.log` for output and errors from the scraping script.
- **Nginx Logs:** Nginx access and error logs can be found in `/var/log/nginx/access.log` and `/var/log/nginx/error.log`, respectively.
- **Cron Job Logs:** To verify the cron job execution, you can check the syslog with `grep CRON /var/log/syslog`.