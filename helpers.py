import os
import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session
from datetime import timedelta
from functools import wraps

# Base price for buildings, it's multiplied by level for upgrading.
building_prices = {"mine": 10000, "ox_gen": 8500, "pow_plant": 9200}

# Base time for buildings, it's multiplied by level for upgrading.
building_times = {"mine": 2, "ox_gen": 1, "pow_plant": 1}


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def error(message, code=400):
    # Default error 400 - Bad Request
    """Render message as an error to user."""
    return render_template("error.html", code=code, message=message), code

def building_name(b_type):
    """Takes b_type as input and returns b_name"""
    if b_type == "mine":
        return "Mine"
    elif b_type == "pow_plant":
        return "Power Plant"
    elif b_type == "ox_gen":
        return "Oxygen Generator"
    else:
        return "N\A"

def building_price(b_type, level = 1):
    """Takes b_type and b_lvl as input and returns price of building"""
    for building_type, price in building_prices.items():
        if b_type == building_type:
            return price * level
    return "ERROR"

def building_time(b_type, level = 1):
    """Takes b_type and b_lvl as input and returns time of building"""
    for building_type, time in building_times.items():
        if b_type == building_type:
            return time * level
    return "ERROR"
 
# src="https://stackoverflow.com/questions/34134971/python-format-timedelta-greater-than-24-hours-for-display-only-containing-hours"
class my_timedelta(timedelta):
    """This function transfors time into HHMMSS format, allowing hour value to go over 24."""
    def __str__(self):
        seconds = self.total_seconds()
        str = '%d:%02d:%02d' % (seconds / 3600, seconds / 60 % 60, seconds % 60)
        return (str)

# This function takes as input HHMMSS format and returns seconds.
# src="https://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python"
def get_sec(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)