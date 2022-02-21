import time
from pprint import pprint

from twitchAPI import Twitch, AuthScope

from twitch_parser.config.config_parser import get_yaml_config
from twitch_parser.streams_scrapper.active_streams_scrapper import ActiveStreamsScrapper
from dateutil import parser as date_parser
import schedule
import logging
logging.basicConfig(level=logging.INFO)

def get_mongodb():
    from pymongo import MongoClient
    import pymongo

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    return client


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":

    user_secrets = get_yaml_config('user_secrets.yaml')
    twitch = Twitch(user_secrets.app_id, user_secrets.app_secret, target_app_auth_scope=[AuthScope.USER_READ_FOLLOWS])

    config = get_yaml_config('stream_db/scrapper_settings.yaml')
    pprint(config)

    # Get the database
    mongodb = get_mongodb()
    mongo_params = config.mongo_settings
    dbname = mongodb[mongo_params.db_name]
    collection_name = dbname[mongo_params.collection_name]

    scrapper = ActiveStreamsScrapper(twitch, config.active_streams_scrapper)


    def scrap_and_insert_to_mongo_job():
        logging.info('Start scrapping streams')
        streams = scrapper.get_filtered_streams()


        for stream in streams:
            if mongo_params.primary_key:
                stream['_id'] = stream[mongo_params.primary_key]
            stream['started_at'] = date_parser.parse(stream['started_at'])
        collection_name.insert_many(streams)

    # First run
    scrap_and_insert_to_mongo_job()

    schedule.every(config.scheduler.run_every_minutes).minutes.do(scrap_and_insert_to_mongo_job)
    while True:
        schedule.run_pending()
        logging.info(f'Wait for scrapping {config.scheduler.sleep_time_in_seconds} seconds')
        time.sleep(config.scheduler.sleep_time_in_seconds)
