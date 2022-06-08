import json
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pprint import pprint
from typing import Iterable

import numpy as np
import ujson
from tqdm import tqdm
from twitchAPI import Twitch, AuthScope

from twitch_parser.clip_downloader.clip_downloader import TwitchDownloader
from twitch_parser.clips_scrapper.top_clip_parser import TopClipScrapper
from twitch_parser.config.config_parser import get_yaml_config
from twitch_parser.streams_scrapper.active_streams_scrapper import ActiveStreamsScrapper
from dateutil import parser as date_parser
import schedule
import logging

from twitch_parser.utils.conditions import KeyValueComparator

logging.basicConfig(level=logging.INFO)

def get_mongodb():
    from pymongo import MongoClient
    import pymongo

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    return client

CLIPS_BY_USER_PAGINATION = 10
num_workers = 5

# This is added so that many files can reuse the function get_database()

def process_channel(channel):
    if isinstance(channel["viewer_count"], (Iterable)) and not isinstance(channel["viewer_count"], str):
        channel["viewer_count"] = math.floor(np.median(channel["viewer_count"]))
    return channel

def parse_excluded_channels(excluded_channels):
    channels = []
    for name in excluded_channels:
        channels.append(name.lower())
    return channels

def filter_channels(channels, excluded_channels):
    resuls_channels = []
    for channel in channels:
        if channel["user_login"].lower() not in excluded_channels and channel["user_name"].lower() not in excluded_channels:
            resuls_channels.append(channel)
        else:
            print(f'Exclude channel: {channel["user_login"]}')
    return resuls_channels

def parse_included_channels(included_channels):
    included_channels = list(map(str, included_channels))
    return included_channels


if __name__ == "__main__":

    user_secrets = get_yaml_config('user_secrets.yaml')
    twitch = Twitch(user_secrets.app_id, user_secrets.app_secret, target_app_auth_scope=[AuthScope.USER_READ_FOLLOWS])

    config = get_yaml_config('stream_db/clips_settings.yaml')
    pprint(config)

    # Get the database
    mongodb = get_mongodb()
    mongo_params = config.mongo_settings
    dbname = mongodb[mongo_params.db_name]
    collection = dbname[mongo_params.collection_name]

    pipeline = [{"$group": {"_id": "$user_name",
                            "user_id": {"$first": "$user_id"},
                            "user_login": {"$first": "$user_login"},
                            "user_name": {"$first": "$user_name"},
                            "viewer_count": {"$push": "$viewer_count"}}}]
    channels = list(collection.aggregate(pipeline))
    channel_filter = KeyValueComparator(config.channels_condition)
    channels = list(map(process_channel, channels)) # Apply some changes for processing
    channels = [channel for channel in channels if channel_filter.check_condition(channel)]

    included_channels = parse_included_channels(config.included_channels)
    print('Included channels is', included_channels)
    excluded_channels = parse_excluded_channels(config.excluded_channels)
    channels = filter_channels(channels, excluded_channels)


    excluded_clips = []
    if config.excluded_clips is not None:
        for excluded_path in map(str, config.excluded_clips):
            with open(excluded_path, 'r') as f:
                clips = ujson.load(f)
            excluded_clips.extend([clip['id'] for clip in clips])

    clips_parser = TopClipScrapper(twitch, config.clips_scrapper)
    downloader = TwitchDownloader()

    os.makedirs(config.general_settings.output_folder, exist_ok=True)
    with open(os.path.join(config.general_settings.output_folder, "channels_data.json"), "w") as channels_data:
        json.dump(channels, channels_data, indent=4, sort_keys=True)
    clips = []


    for channel_id in tqdm(tuple(range(0, len(channels), CLIPS_BY_USER_PAGINATION))):
        channels_subset = [channel for channel in
                           channels[channel_id:channel_id + CLIPS_BY_USER_PAGINATION]]
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            partials = (partial(clips_parser.get_clips, [channel['user_id']], ignore_filter=(channel["user_login"].lower() in included_channels or channel["user_name"].lower() in included_channels)) for channel in channels_subset)
            futures = [executor.submit(fn) for fn in partials]
        for user_clips in futures:
            clips.extend(user_clips.result())
        logging.info(f'Clips count is {len(clips)}')
    logging.info(f'Clips count is {len(clips)}')
    logging.info(f'Start downloading')

    with open(os.path.join(config.general_settings.output_folder, "conc_clips_data.json"), "w") as clips_data:
        json.dump(clips, clips_data, indent=4, sort_keys=True)
    clips_was_excluded = []
    output_clips = []
    for clip in tqdm(clips):
        if clip['id'] in excluded_clips:
            clips_was_excluded.append(clip["id"])
            logging.info(f'Skip clip with {clip["id"]} id')
            continue
        try:
            out_path = downloader.download(clip['id'], os.path.join(config.general_settings.output_folder, clip['broadcaster_name']))
            if out_path is not None:
                clip['out_path'] = out_path
                output_clips.append(clip)
        except Exception as e:
            print(e)
    with open(os.path.join(config.general_settings.output_folder, "dumped_clips_data.json"), "w") as clips_data:
        json.dump(clips, clips_data, indent=4, sort_keys=True)

    print(clips_was_excluded)
    print(f'excluded_clips {len(excluded_clips)}, clips was excluded {len(clips_was_excluded)}')
