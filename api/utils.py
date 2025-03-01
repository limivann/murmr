import textwrap
import datetime
import pytz
import numpy as np

def get_now(timezone="Asia/Singapore"):
  timezone = pytz.timezone('Asia/Singapore')
  now = datetime.datetime.now(timezone)
  return now

def get_today_str():
  now = get_now()
  today = now.date()
  return today


def dedent(text):
  return textwrap.dedent(text).strip()


def convert_to_int(obj):
    if isinstance(obj, dict):
        return {key: convert_to_int(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_int(item) for item in obj]
    elif isinstance(obj, np.int64):
        return int(obj)
    return obj