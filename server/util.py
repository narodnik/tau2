import os, random, time
from datetime import date, datetime

def config_path():
    home = os.environ['HOME']
    # Deliberately non-cross platform
    return f"{home}/.config/tau"

def safe_open(filename, perm):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    return open(filename, perm)

# returns MMYY format
def current_month():
    today = date.today()
    return today.strftime("%d%y")

