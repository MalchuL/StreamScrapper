import time
from pprint import pprint
import logging

from dataclasses import dataclass
from twitchAPI.twitch import Twitch

from twitch_parser.utils.conditions import KeyValueComparator
from twitch_parser.utils.numeric_utils import value_or_inf
from twitch_parser.utils.structures import empty_list_to_none

@dataclass
class MockConfig:
    conditions: dict = None
    max_channels_count: int = None

class ChannelsScrapper:
    PAGINATION_MAXIMUM = 100

    def __init__(self, twitch_api: Twitch, scrapper_config=None):
        if scrapper_config is None:
            scrapper_config = MockConfig(conditions=None, max_channels_count=None)
        self.scrapper_config = scrapper_config
        self.channel_filter = KeyValueComparator(scrapper_config.conditions)
        self.max_channels_count = value_or_inf(self.scrapper_config.max_channels_count)
        self.twitch_api = twitch_api

    def _get_available_channels(self, ids):
        twitch_api = self.twitch_api
        channels = []
        for id in range(0, len(ids), self.PAGINATION_MAXIMUM):
            while True:
                try:
                    sub_ids = list(ids[id: id + self.PAGINATION_MAXIMUM])
                    users = twitch_api.get_users(user_ids=sub_ids)['data']
                    logging.debug(f'get user from ids {users}')
                    channels.extend(users)
                    break
                except KeyError as e:
                    logging.exception('possibly rate possibly reached rate limit, waiting for reset')
                    time.sleep(30)

        return channels

    def _get_channels_by_logins(self, logins):
        twitch_api = self.twitch_api
        channels = []

        for id in range(0, len(logins), self.PAGINATION_MAXIMUM):
            while True:
                try:
                    sub_logins = list(logins[id: id + self.PAGINATION_MAXIMUM])
                    users = twitch_api.get_users(logins=sub_logins)['data']
                    logging.debug(f'get user from ids {users}')
                    channels.extend(users)
                    break
                except KeyError as e:
                    logging.exception('possibly rate possibly reached rate limit, waiting for reset')
                    time.sleep(30)

        return channels



    def get_channels_by_ids(self, user_ids):
        channels = self._get_available_channels(user_ids)

        # Log unfinded channels
        channels_user_ids = [str(channel['id']) for channel in channels]
        excluded_channels = set(map(str, user_ids)).difference(set(channels_user_ids))
        if excluded_channels:
            logging.info(f'{excluded_channels} was not founded')
            excluded_names = []
            for channel in channels:
                if channel['id'] in excluded_channels:
                    excluded_names.append(channel['user_name'])
            logging.info(f'{excluded_names} was not founded, please find this channels manualy')

        # Filter channels
        filtered_channels = []
        for channel in channels:
            if self.channel_filter.check_condition(channel):
                filtered_channels.append(channel)

        return filtered_channels

    def get_channels_by_logins(self, logins):
        channels = self._get_channels_by_logins(logins)
        user_ids = [channel['id'] for channel in channels]
        return self.get_channels_by_ids(user_ids)

    def get_channels_from_streams(self, streams=[]):
        user_ids = [stream['user_id'] for stream in streams]
        return self.get_channels_by_ids(user_ids)

