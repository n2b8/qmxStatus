#!/usr/bin/env python3

from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

database_file_path = '/opt/qmxStatus/order_tracking.db'

def get_current_datetime():
    # Returns current datetime as a datetime object
    return datetime.now()

def fetch_most_recent_row():
    try:
        conn = sqlite3.connect(database_file_path)
        c = conn.cursor()
        c.execute("SELECT position, date_checked FROM order_tracking ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
    finally:
        conn.close()
    if row:
        position, datetime_str = row
        return position, datetime_str  # Return the datetime string directly
    return None, None

def update_or_insert_position(position):
    current_datetime = get_current_datetime()
    current_date_str = current_datetime.strftime('%Y-%m-%d')

    try:
        conn = sqlite3.connect(database_file_path)
        c = conn.cursor()

        # Check if an entry exists for this date regardless of the position
        c.execute("SELECT COUNT(*) FROM order_tracking WHERE date(date_checked) = ?", (current_date_str,))
        count = c.fetchone()[0]

        if count == 0:
            # No entry for this date, so insert a new row
            current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT INTO order_tracking (position, date_checked) VALUES (?, ?)", (position, current_datetime_str))
        else:
            # An entry for this date exists, check if the position is the same
            c.execute("SELECT position FROM order_tracking WHERE date(date_checked) = ?", (current_date_str,))
            existing_position = c.fetchone()[0]
            if existing_position != position:
                # The position for today has changed, update the row
                current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
                c.execute("UPDATE order_tracking SET position = ?, date_checked = ? WHERE date(date_checked) = ?", (position, current_datetime_str, current_date_str))
            else:
                # The position for today is the same, do nothing or log this information
                print("The position for today has not changed.")

        conn.commit()
    finally:
        conn.close()


def fetch_order_position(order_number):
    url = "https://qrp-labs.com/qcxmini/assembled.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')  # Assuming there's only one table

    for row in table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        if cols and cols[1].text.strip() == str(order_number):
            return cols[0].text.strip()  # Position
    return None

def update_prediction(database_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    # Fetch positions and dates from the database
    c.execute('SELECT position, date_checked FROM order_tracking WHERE date_checked IS NOT NULL')
    data = c.fetchall()

    # Ensure there's enough data for regression
    if len(data) < 2:
        print("Not enough data points for regression.")
        conn.close()
        return

    # Prepare data for regression
    X = np.array([i for i in range(len(data))]).reshape(-1, 1)  # Independent variable: index
    y = np.array([row[0] for row in data])  # Dependent variable: position

    # Perform linear regression
    model = LinearRegression().fit(X, y)

    # Attempt to predict when position will be zero
    try:
        zero_position_day = np.max(np.roots([model.coef_[0], model.intercept_]))
    except:
        print("Unable to compute a prediction.")
        predict_complete = "Unable to compute yet"
    else:
        if zero_position_day < 0:
            print("Prediction not feasible with current data.")
            predict_complete = "Unable to compute yet"
        else:
            # Calculate the predicted completion date
            start_date = datetime.strptime(data[0][1], '%Y-%m-%d %H:%M:%S')
            predict_date = start_date + timedelta(days=zero_position_day)
            predict_complete = predict_date.strftime('%m-%d-%Y')

    # Update the most recent row in the database
    c.execute('UPDATE order_tracking SET predict_complete = ? ORDER BY id DESC LIMIT 1', (predict_complete,))
    conn.commit()

    # Close the database connection
    conn.close()


def main():
    position = fetch_order_position(84805)
    if position is not None:
        update_or_insert_position(position)
        update_prediction(database_file_path)
    else:
        print("Position not found.")

if __name__ == "__main__":
    main()
