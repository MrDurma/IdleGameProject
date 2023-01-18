import os
import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session
from datetime import timedelta
from functools import wraps

# Base price for buildings, it's multiplied by level for upgrading.
building_prices = {"mine": 10000, "ox_gen": 8500, "pow_plant": 9200, "farm": 2000}

# Base time for buildings, it's multiplied by level for upgrading.
building_times = {"mine": 2, "ox_gen": 1, "pow_plant": 1, "farm": 0.2}


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
    """Render message as an error to user."""
    # Default error 400 - Bad Request
    return render_template("error.html", code=code, message=message), code

def building_name(b_type):
    """Takes b_type as input and returns b_name"""
    if b_type == "mine":
        return "Mine"
    elif b_type == "pow_plant":
        return "Power Plant"
    elif b_type == "ox_gen":
        return "Oxygen Generator"
    elif b_type == "farm":
        return "Farm"
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
    