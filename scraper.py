#!/usr/bin/env python3

from datetime import datetime
import requests
from bs4 import BeautifulSoup
import sqlite3

def get_current_datetime():
    # Returns current datetime as a datetime object
    return datetime.now()

def fetch_most_recent_row():
    try:
        conn = sqlite3.connect('order_tracking.db')
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
    most_recent_position, most_recent_datetime_str = fetch_most_recent_row()

    try:
        conn = sqlite3.connect('order_tracking.db')
        c = conn.cursor()

        current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        if most_recent_datetime_str:
            most_recent_datetime = datetime.strptime(most_recent_datetime_str, '%Y-%m-%d %H:%M:%S')

            if most_recent_datetime.date() == current_datetime.date():
                # Update the row if the date is the same but the position has changed
                c.execute("UPDATE order_tracking SET position = ?, date_checked = ? WHERE date_checked = ?", (position, current_datetime_str, most_recent_datetime_str))
            else:
                # Insert a new row if the date has changed
                c.execute("INSERT INTO order_tracking (position, date_checked) VALUES (?, ?)", (position, current_datetime_str))
        else:
            # If the table is empty, insert the first row
            c.execute("INSERT INTO order_tracking (position, date_checked) VALUES (?, ?)", (position, current_datetime_str))
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

def main():
    position = fetch_order_position(84805)
    if position is not None:
        update_or_insert_position(position)
    else:
        print("Position not found.")

if __name__ == "__main__":
    main()
