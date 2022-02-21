import logging

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.types import AuthScope
from pprint import pprint

from twitch_parser.dumping_pipeline.download_latest_clips import TwitchDownloader, LatestClipsDownloader

logging.basicConfig(level=logging.DEBUG)
from twitch_parser.config.config_parser import get_yaml_config

if __name__ == '__main__':
    from twitchAPI.twitch import Twitch, AuthScope

    user_secrets = get_yaml_config('user_secrets.yaml')
    twitch = Twitch(user_secrets.app_id, user_secrets.app_secret, target_app_auth_scope=[AuthScope.USER_READ_FOLLOWS])


    config = get_yaml_config('twitch_downloader/parser_settings.yaml')
    pprint(config)

    scrapper = LatestClipsDownloader(twitch, config, output_folder='twitch_clips_new')
    scrapper.get_clips()
