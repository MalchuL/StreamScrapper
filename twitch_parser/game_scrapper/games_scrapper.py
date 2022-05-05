import time
from pprint import pprint
import logging
from twitchAPI.twitch import Twitch

from twitch_parser.utils.conditions import KeyValueComparator
from twitch_parser.utils.structures import empty_list_to_none


class GamesScrapper:
    PAGINATION_MAXIMUM = 100

    def __init__(self, twitch_api: Twitch):
        self.twitch_api = twitch_api

    def get_games(self, game_names):
        if not game_names:
            return None
        while True:
            try:
                games = self.twitch_api.get_games(names=list(game_names))['data']
                break
            except KeyError as e:
                logging.exception('possibly rate possibly reached rate limit, waiting for reset')
                time.sleep(30)

        return games

    def get_game_ids(self, game_names):
        if not game_names:
            return None
        return [str(game['id']) for game in self.get_games(game_names)]



