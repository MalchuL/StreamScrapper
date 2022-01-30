from pprint import pprint
import logging
from twitchAPI.twitch import Twitch

from twitch_parser.utils.conditions import parse_condition, KeyValueComparator
from twitch_parser.utils.structures import empty_list_to_none


class Scrapper:
    PAGINATION_MAXIMUM = 100

    def __init__(self, twitch_api: Twitch, scrapper_config):
        self.scrapper_config = scrapper_config
        self.stream_filter = KeyValueComparator(scrapper_config.conditions)
        self.max_stream_count = self.scrapper_config.max_stream_count
        self.twitch_api = twitch_api


    def get_game_ids(self, game_names):
        games = self.twitch_api.get_games(names=list(game_names))['data']
        return [game['id'] for game in games]

    def get_aviable_streams(self):
        current_viewers = 0
        twitch_api = self.twitch_api

        if self.scrapper_config.language is None:
            languages = None
        else:
            languages = empty_list_to_none(list(self.scrapper_config.language))

        if self.scrapper_config.game_names is None:
            game_names = None
        else:
            game_names = empty_list_to_none(self.get_game_ids(self.scrapper_config.game_names))
        cursor = None
        streams = []

        logging.debug(
            f'Try to fetch streams with params game_id={game_names}, language={languages}, first={self.PAGINATION_MAXIMUM}')

        while len(streams) < self.max_stream_count:

            part_streams = twitch_api.get_streams(after=cursor, game_id=game_names, language=languages,
                                                  first=self.PAGINATION_MAXIMUM)
            streams.extend(part_streams['data'])
            if 'cursor' in part_streams['pagination']:
                cursor = part_streams['pagination']['cursor']
            else:
                if len(streams) == 0:
                    raise RuntimeError(f'Cannot fetch any stream, data was returned={part_streams}')
                else:
                    break
            logging.debug(f'fetched {len(streams)} streams, streams with {part_streams["data"][0]}')
        return streams

    def get_filtered_streams(self, streams=None):
        if streams is None:
            streams = self.get_aviable_streams()
        filtered_streams = []
        for stream in streams:
            if self.stream_filter.check_condition(stream):
                filtered_streams.append(stream)

        return filtered_streams

