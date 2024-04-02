# Flask Position Tracker

## Overview

This Flask application tracks and displays the position of an order over time. It scrapes a specified webpage for the current position of an order number, stores this information in a SQLite database, and visualizes the position history on a line graph. The application updates the position data hourly using a scheduled script.

## Features

- **Data Scraping:** Automatically scrapes the web for order position data.
- **Data Visualization:** Displays the order position history on a line graph.
- **Automatic Updates:** Uses cron jobs to periodically update the order position.

## Getting Started

### Prerequisites

- Python 3
- Flask
- SQLite3
- Requests
- BeautifulSoup4

### Installation

1. **Clone the repository** to your local machine.
    ```bash
    git clone <repository-url>
    ```
2. **Navigate to the project directory** and create a virtual environment:
    ```bash
    cd <project-directory>
    python3 -m venv venv
    ```
3. **Activate the virtual environment:**
    - On Windows:
        ```cmd
        .\venv\Scripts\activate
        ```
    - On Unix or MacOS:
        ```bash
        source venv/bin/activate
        ```
4. **Install the required packages:**
    ```bash
    pip install flask requests beautifulsoup4 sqlite3
    ```
### Configuration

1. **Update the Order Number:** To track a specific order number, update the `fetch_order_position` function in the `scraper.py` file with your desired order number.

    ```python
    position = fetch_order_position(YOUR_ORDER_NUMBER_HERE)
    ```

    Replace `YOUR_ORDER_NUMBER_HERE` with the actual order number you wish to track.

2. **Crontab Setting for Periodic Scraping:** Schedule the scraper to run periodically using crontab. This example sets it to run every hour.

    Open your crontab file for editing:

    ```bash
    crontab -e
    ```

    Add the following line to execute the scraper script every hour. Make sure to adjust the path to where your `scraper.py` is located.

    ```cron
    0 * * * * /path/to/your/venv/bin/python /path/to/your/project/scraper.py
    ```

3. **Systemctl Setting for Flask App:** To ensure your Flask application starts at boot and restarts on failure, create a systemd service.

    Create a systemd service file for your Flask application:

    ```bash
    sudo nano /etc/systemd/system/yourapp.service
    ```

    Add the following configuration, adjusting paths and user information as necessary:

    ```ini
    [Unit]
    Description=Gunicorn instance to serve Flask Position Tracker
    After=network.target

    [Service]
    User=username
    Group=groupname
    WorkingDirectory=/path/to/your/project
    Environment="PATH=/path/to/your/venv/bin"
    ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

    [Install]
    WantedBy=multi-user.target
    ```

    Replace `username` and `groupname` with your user and group, and adjust the paths to match your project setup.

    After creating and saving the service file, enable and start the service:

    ```bash
    sudo systemctl enable yourapp.service
    sudo systemctl start yourapp.service
    ```

    Check the status to ensure it's running correctly:

    ```bash
    sudo systemctl status yourapp.service
    ```
### Running the Application

After configuring your application, you can run it using the following steps:

#### For Development:

- Activate your virtual environment if you haven't already:
    - On Windows:
        ```cmd
        .\venv\Scripts\activate
        ```
    - On Unix or MacOS:
        ```bash
        source venv/bin/activate
        ```
- Start the Flask application with:
    ```bash
    flask run --host=0.0.0.0 --port=5000
    ```
  This command runs the Flask development server, making the application accessible on `http://localhost:5000` or your machine's IP address on port 5000.

#### Setting Up Gunicorn for Production:

Before running the application in a production environment, you should set up Gunicorn to serve your Flask app. Gunicorn is a Python WSGI HTTP Server for UNIX, providing a robust way to deploy your Flask application.

1. **Install Gunicorn:**
    - Ensure your virtual environment is activated, and install Gunicorn using pip:
        ```bash
        pip install gunicorn
        ```

2. **Run Gunicorn:**
    - Navigate to your project directory, and start Gunicorn with:
        ```bash
        gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
        ```
      Replace `app:app` with your Flask app's module and application variable names if they're different. Adjust the number of workers based on your server's capacity and the expected workload.

3. **Create a Gunicorn systemd Service File (Optional but Recommended):**
    - For better management and to ensure your app starts on boot, you can create a systemd service for Gunicorn.
    - Create a new service file:
        ```bash
        sudo nano /etc/systemd/system/yourapp.service
        ```
    - Add the following configuration, adjusting paths, user, and group as necessary:
        ```ini
        [Unit]
        Description=Gunicorn instance to serve Flask Position Tracker
        After=network.target

        [Service]
        User=username
        Group=groupname
        WorkingDirectory=/path/to/your/project
        Environment="PATH=/path/to/your/venv/bin"
        ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

        [Install]
        WantedBy=multi-user.target
        ```
    - Enable and start the service:
        ```bash
        sudo systemctl enable yourapp.service
        sudo systemctl start yourapp.service
        ```

#### Accessing the Application:

- Open a web browser and navigate to `http://<your-server-ip>:5000` to view your application. Replace `<your-server-ip>` with the actual IP address of your server.

#### Monitoring and Logs:

- To monitor the application's activity or troubleshoot issues, you can check the logs for your Flask application and Gunicorn service:
    - Flask development server logs will display in the terminal where you started the `flask run` command.
    - For Gunicorn, check the systemd journal logs:
        ```bash
        sudo journalctl -u yourapp.service
        ```
      This command displays the logs for your Gunicorn service, which can help diagnose any issues or monitor access to your Flask application.
