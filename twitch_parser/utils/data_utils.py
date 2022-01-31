from datetime import datetime, timezone, timedelta

import iso8601
import rfc3339


def get_now():
    local_time = datetime.now(timezone.utc).astimezone()
    return local_time

def add_time(time, days=0, seconds=0, microseconds=0,
                milliseconds=0, minutes=0, hours=0, weeks=0):
    return time + timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)

def subsctract_time(time, days=0, seconds=0, microseconds=0,
                milliseconds=0, minutes=0, hours=0, weeks=0):
    return time - timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)

def parse_data(data_str):
    return datetime.strptime(data_str, '%d/%m/%y %H:%M:%S').astimezone(timezone.utc)

def get_date_object(date_string):
  return iso8601.parse_date(date_string)

def parse_rfc3339(string):
    return rfc3339.rfc3339(get_date_object(string))


if __name__ == '__main__':
    now = get_now()
    print(now)
    print(add_time(now, weeks=1, days=9))