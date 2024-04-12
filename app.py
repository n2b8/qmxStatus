from flask import Flask, render_template, Response, make_response
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)

def set_csp_header(csp_value):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            resp.headers['Content-Security-Policy'] = csp_value
            return resp
        return decorated_function
    return decorator

csp_policy = "frame-ancestors 'self' http://jakemccaig.com, https://www.qrz.com/"

def get_latest_position():
    '''Fetch the latest position and the timestamp from the database.'''
    conn = sqlite3.connect('order_tracking.db')
    c = conn.cursor()
    c.execute("SELECT position, date_checked FROM order_tracking ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        position, last_checked = row
        # Calculate how long it has been since the last check
        last_checked_date = datetime.strptime(last_checked, '%Y-%m-%d %H:%M:%S')
        delta = datetime.now() - last_checked_date
        hours_since_last_checked = delta.total_seconds() / 3600
        return position, round(hours_since_last_checked, 2)
    return None, None

def get_time_since_last_position_change(current_position):
    '''Fetch the timestamp of the last position change from the database.'''
    conn = sqlite3.connect('order_tracking.db')
    c = conn.cursor()
    # Query to find the most recent different position
    c.execute("""
        SELECT date_checked FROM order_tracking
        WHERE position != ?
        ORDER BY id DESC
        LIMIT 1
    """, (current_position,))
    row = c.fetchone()
    conn.close()
    if row:
        last_change_date_str = row[0]
        last_change_date = datetime.strptime(last_change_date_str, '%Y-%m-%d %H:%M:%S')
        delta = datetime.now() - last_change_date
        hours_since_last_change = delta.total_seconds() / 3600
        return round(hours_since_last_change, 2)
    return None

@app.route('/')
@set_csp_header(csp_policy)
def home():
    current_position, _ = get_latest_position()  # Fetches the latest position and timestamp

    hours_since_change = None
    if current_position is not None:
        hours_since_change = get_time_since_last_position_change(current_position)

    # Fetch all dates and positions for the graph
    conn = sqlite3.connect('order_tracking.db')
    c = conn.cursor()
    c.execute("SELECT date_checked, position FROM order_tracking ORDER BY date_checked")
    data = c.fetchall()
    all_dates = [row[0] for row in data]
    all_positions = [row[1] for row in data]

    # Fetch the predicted completion date
    c.execute("SELECT predict_complete FROM order_tracking ORDER BY id DESC LIMIT 1")
    prediction_row = c.fetchone()
    predict_complete = prediction_row[0] if prediction_row else "Prediction not available"

    conn.close()

    return render_template('index.html', position=current_position, all_dates=all_dates, all_positions=all_positions, hours_since_checked=hours_since_change, predict_complete=predict_complete)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
