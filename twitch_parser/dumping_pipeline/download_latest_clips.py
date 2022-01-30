import json
import logging
import os.path

from twitchAPI import Twitch

from twitch_parser.channels_scapper.channels_scrapper import ChannelsScrapper
from twitch_parser.clip_downloader.clip_downloader import TwitchDownloader
from twitch_parser.clips_scrapper.top_clip_parser import TopClipScrapper
from twitch_parser.streams_scrapper.active_streams_scrapper import ActiveStreamsScrapper


class LatestClipsDownloader:
    def __init__(self, twitch_api: Twitch, pipeline_config, output_folder='clips_output', pagination=10):
        self.pagination = pagination
        self.output_folder = output_folder
        self.streams_parser = ActiveStreamsScrapper(twitch_api, pipeline_config.active_streams_scrapper)
        self.channels_parser = ChannelsScrapper(twitch_api, pipeline_config.chanels_scrapper)
        self.clips_parser = TopClipScrapper(twitch_api, pipeline_config.clips_scrapper)
        self.downloader = TwitchDownloader()

    def get_clips(self):
        logging.info('Start collecting streams')
        streams = self.streams_parser.get_filtered_streams()
        assert len(streams) > 0
        with open(os.path.join(self.output_folder, "streams_data.json"), "w") as streams_data:
            json.dump(streams, streams_data, indent=4, sort_keys=True)
        logging.info(f'Finish collecting streams, actual size {len(streams)}')

        logging.info('Start collecting channels by streams')
        # Todo avoid using next scrapper, we can extract whole info from streams
        channels = self.channels_parser.get_channels_from_streams(streams)
        logging.info(f'Finish collecting channels, actual size {len(channels)}, len of streams is {len(streams)}')
        assert len(channels) > 0
        with open(os.path.join(self.output_folder, "channels_data.json"), "w") as channels_data:
            json.dump(channels, channels_data, indent=4, sort_keys=True)

        # In twitch we have some bugs with clips downloading I recommend pass single broadcaster
        logging.info('Start collecting clips by channels')
        clips = []
        for channel_id in range(0, len(channels), self.pagination):
            channels_subset = [channel['id'] for channel in channels[channel_id:channel_id+self.pagination]]
            clips.extend(self.clips_parser.get_clips(broadcaster_ids=channels_subset))
            logging.info(f'Clips count is {len(clips)}')
        logging.info(f'Clips count is {len(clips)}')
        logging.info(f'Start downloading')
        with open(os.path.join(self.output_folder, "conc_clips_data.json"), "w") as clips_data:
            json.dump(clips, clips_data, indent=4, sort_keys=True)
        for clip in clips:
            try:
                self.downloader.download(clip['id'], self.output_folder)
            except Exception as e:
                print(e)


