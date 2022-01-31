from datetime import datetime

import pytest

from twitch_parser.utils.conditions import parse_condition
from twitch_parser.utils.data_utils import parse_rfc3339, get_date_object, get_now


def test_datetime_converter():
    #date_string = "2022-01-31T18:39:47Z" # "2022-01-31T18:29:00Z"
    date_string = "2022-01-31T14:59:22Z" # "2022-01-31T18:29:00Z"
    now_data = '2022-01-31 18:39:47.685288+03:00'
   # now_date
    date =  get_date_object(now_data ) - get_date_object(date_string)
    assert date.seconds/60 > 40 and date.seconds/60 < 50
    print(str(date.seconds/60))
