from datetime import datetime

import pytest

from clips_editor.widgets.list_items.video_item import Clip
from twitch_parser.config.config_parser import get_yaml_config
from twitch_parser.utils.conditions import parse_condition
from twitch_parser.utils.data_utils import parse_rfc3339, get_date_object, get_now
from video_generator.subtitle_generator.twitch_data import TwitchData


def test_datetime_converter():
    from twitchAPI.twitch import Twitch, AuthScope
    user_secrets = get_yaml_config('../user_secrets.yaml')
    twitch = Twitch(user_secrets.app_id, user_secrets.app_secret, target_app_auth_scope=[AuthScope.USER_READ_FOLLOWS])
    twitch_data = TwitchData(twitch)
    clip = Clip(154681811, 'eva_leie', None, None, None)
    twitch_data.generate_streamer_subtitle(clip, 'test.png')