from pprint import pprint
import logging
from twitchAPI.twitch import Twitch

from twitch_parser.game_scrapper.games_scrapper import GamesScrapper
from twitch_parser.utils.conditions import KeyValueComparator
from twitch_parser.utils.data_utils import get_now, subsctract_time, parse_data
from twitch_parser.utils.numeric_utils import value_or_inf
from twitch_parser.utils.structures import empty_list_to_none


class TopClipScrapper:
    PAGINATION_MAXIMUM = 20

    def __init__(self, twitch_api: Twitch, scrapper_config):
        self.scrapper_config = scrapper_config
        self.twitch_api = twitch_api
        self.game_scrapper = GamesScrapper(self.twitch_api)
        self.clip_filter = KeyValueComparator(scrapper_config.conditions)
        self.game_names = self.scrapper_config.game_names
        self.max_clips_count = value_or_inf(self.scrapper_config.max_clips_count)

        self.start_time = get_now() if self.scrapper_config.start in ['now', None, 0] else parse_data(self.scrapper_config.start)
        self.end_time = subsctract_time(self.start_time, self.scrapper_config.before_days)

    def get_clips(self, broadcaster_ids=None):
        if broadcaster_ids is not None:
            broadcaster_ids = list(broadcaster_ids)
        twitch_api = self.twitch_api
        if self.game_names is None:
            game_ids = None
        else:
            game_ids = empty_list_to_none(self.game_scrapper.get_game_ids(self.game_names))
        logging.debug(f'Search for game ids={game_ids} and broadcaster={broadcaster_ids}')
        clips = []
        cursor = None
        while len(clips) < self.max_clips_count:
            if broadcaster_ids is not None:
                input_game_ids = None
            else:
                input_game_ids = game_ids
            part_clips = twitch_api.get_clips(after=cursor, game_id=input_game_ids, broadcaster_id=broadcaster_ids, first=self.PAGINATION_MAXIMUM, started_at=self.end_time, ended_at=self.start_time)

            part_clips_data = part_clips['data']
            if game_ids and broadcaster_ids is not None:
                part_clips_data = []
                for clip in part_clips['data']:
                    if str(clip['game_id']) in game_ids:
                        part_clips_data.append(clip)

            clips.extend(part_clips_data)

            if 'cursor' in part_clips['pagination']:
                cursor = part_clips['pagination']['cursor']

            else:
                if len(clips) == 0:
                    logging.error(f'No clips was founded for broadcaster {broadcaster_ids}')
                break
            logging.debug(f'fetched {len(clips)} clips, clips with {part_clips["data"][0]}')

        filtered_clips = []
        for clip in clips:
            if self.clip_filter.check_condition(clip):
                filtered_clips.append(clip)
        return filtered_clips

