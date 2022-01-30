from pprint import pprint
import logging
from twitchAPI.twitch import Twitch

from twitch_parser.utils.conditions import KeyValueComparator
from twitch_parser.utils.numeric_utils import value_or_inf
from twitch_parser.utils.structures import empty_list_to_none


class ChannelsScrapper:
    PAGINATION_MAXIMUM = 100

    def __init__(self, twitch_api: Twitch, scrapper_config):
        self.scrapper_config = scrapper_config
        self.channel_filter = KeyValueComparator(scrapper_config.conditions)
        self.max_channels_count = value_or_inf(self.scrapper_config.max_channels_count)
        self.twitch_api = twitch_api

    def get_available_channels(self, ids):
        twitch_api = self.twitch_api
        channels = []
        for id in range(0, len(ids), self.PAGINATION_MAXIMUM):
            sub_ids = list(ids[id: id + self.PAGINATION_MAXIMUM])
            users = twitch_api.get_users(user_ids=sub_ids)['data']
            logging.debug(f'get user from ids {users}')
            channels.extend(users)

        return channels


    def get_channels_from_streams(self, streams=[]):
        user_ids = [stream['user_id'] for stream in streams]
        channels = self.get_available_channels(user_ids)

        # Log unfinded channels
        channels_user_ids = [channel['id'] for channel in channels]
        excluded_channels = set(user_ids).difference(set(channels_user_ids))
        if excluded_channels:
            logging.info(f'{excluded_channels} was not founded')
            excluded_names = []
            for channel in channels:
                if channel['user_id'] in excluded_channels:
                    excluded_names.append(channel['user_name'])
            logging.info(f'{excluded_names} was not founded, please find this channels manualy')

        # Filter channels
        filtered_channels = []
        for channel in channels:
            if self.channel_filter.check_condition(channel):
                filtered_channels.append(channel)

        return filtered_channels

