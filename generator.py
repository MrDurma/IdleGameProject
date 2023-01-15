import os
import requests
import urllib.parse
import threading
import sqlite3

import time
from threading import Lock
from datetime import datetime, timedelta

lock= Lock()

# Key value pairs that contain buiding type and index.
index = {"Empty": 0, "mine": 0.6, "ox_gen": 0.4, "pow_plant": 0.5}
# Configure application to use SQLite database
data = sqlite3.connect('data.db', check_same_thread=False)
# https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
data.row_factory = sqlite3.Row
db = data.cursor()

def building_income():
    """ Generates income every 5 seconds for every building built in 
        buildings.db based on their type and level.
        Busy buildings do not generate income. """
    threading.Timer(5.0, building_income).start()
    lock.acquire(True)
    db.execute("SELECT * FROM buildings WHERE is_busy=0")
    lock.release()
    lock.acquire(True)
    buildings = db.fetchall()
    lock.release()
    for building in buildings:
        for b_type, i in index.items():
            if building["b_type"] == "Empty":
                break
            else:
                lock.acquire(True)
                db.execute("UPDATE users SET money = money + ? WHERE user_id = ?",
                          ((i * building["b_lvl"]), building["user_id"]))
                data.commit()
                lock.release()

def update_busy_status():
    """ This function is checking every 5 seconds if building status 
        should be changed from busy to not busy(1 or 0)"""
    threading.Timer(5.0, update_busy_status).start()
    lock.acquire(True)
    db.execute("SELECT * FROM buildings WHERE is_busy=1")
    buildings = db.fetchall()
    lock.release()
    for building in buildings:
        time = datetime.strptime(building["busy_until"], '%Y-%m-%d %H:%M:%S')

        # If time until building is completed is 15 seconds or less
        if  time < (datetime.now() + timedelta(seconds = 15)):
            lock.acquire(True)

            # Changing building is_busy value to 0 (False)
            db.execute("UPDATE buildings SET is_busy=0 WHERE b_id=?", (building["b_id"] ,))
            data.commit()
            lock.release()

            # If building was being upgraded, changing b_lvl value
            if building["status"] == "Upgrading":
                lock.acquire(True)
                db.execute("UPDATE buildings SET b_lvl=b_lvl+1 WHERE b_id=?", (building["b_id"] ,))
                data.commit()
                lock.release()

            # Changing building status to none
            lock.acquire(True)
            db.execute("UPDATE buildings SET status='' WHERE b_id=?", (building["b_id"], ))
            data.commit()
            lock.release()
