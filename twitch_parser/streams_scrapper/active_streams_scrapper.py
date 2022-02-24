from pprint import pprint
import logging
from twitchAPI.twitch import Twitch

from twitch_parser.game_scrapper.games_scrapper import GamesScrapper
from twitch_parser.utils.conditions import KeyValueComparator
from twitch_parser.utils.data_utils import get_now, get_date_object
from twitch_parser.utils.numeric_utils import value_or_inf
from twitch_parser.utils.structures import empty_list_to_none


class ActiveStreamsScrapper:
    PAGINATION_MAXIMUM = 100

    def __init__(self, twitch_api: Twitch, scrapper_config):
        self.scrapper_config = scrapper_config
        self.stream_filter = KeyValueComparator(scrapper_config.conditions)
        self.max_stream_count = value_or_inf(self.scrapper_config.max_stream_count)
        self.twitch_api = twitch_api
        self.game_scrapper = GamesScrapper(self.twitch_api)

    def get_game_ids(self, game_names):
        return self.game_scrapper.get_game_ids(game_names)

    def get_available_streams(self):
        twitch_api = self.twitch_api

        if self.scrapper_config.language is None:
            languages = None
        else:
            languages = empty_list_to_none(list(self.scrapper_config.language))

        if self.scrapper_config.game_names is None:
            game_names = None
        else:
            game_names = empty_list_to_none(self.get_game_ids(self.scrapper_config.game_names))

        streams = []

        logging.debug(
            f'Try to fetch streams with params game_id={game_names}, language={languages}, first={self.PAGINATION_MAXIMUM}')
        for game_name in game_names:
            cursor = None
            while len(streams) < self.max_stream_count:

                part_streams = twitch_api.get_streams(after=cursor, game_id=[game_name], language=languages,
                                                      first=self.PAGINATION_MAXIMUM)

                # Add duration field
                start_time = get_now()
                for part_stream in part_streams['data']:
                    stream_duration = start_time - get_date_object(part_stream['started_at'])
                    duration_minutes = stream_duration.seconds / 60
                    part_stream['duration_minutes'] = duration_minutes

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
            streams = self.get_available_streams()
        filtered_streams = []
        for stream in streams:
            if self.stream_filter.check_condition(stream):
                filtered_streams.append(stream)

        return filtered_streams

