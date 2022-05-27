from clips_editor.widgets.list_items.video_item import Clip
from twitch_parser.channels_scapper.channels_scrapper import ChannelsScrapper
from video_generator.title_generator.render_html import render_text
from video_generator.title_generator.text_styles.twitch_subtitle_style import TwitchSubtitleStyle


class TwitchData():
    def __init__(self, twitch_api):
        self.twitch_api = twitch_api
        self.channel_scrapper = ChannelsScrapper(self.twitch_api)
    '''
    Returns raw link with http/https prefix
    '''
    def get_raw_link(self, clip: Clip):
        return f'https://www.twitch.tv/{clip.streamer_name}'

    '''
    Returns readabke link to describe streamer
    '''
    def get_simple_link(self, clip: Clip):
        return f'twitch.tv/{clip.streamer_name}'

    '''
        Generate image with streamer simple link
    '''
    def generate_streamer_subtitle(self, clip, out_path='out.png'):
        try:
            user_data = self.channel_scrapper.get_channels_by_logins([clip.streamer_name.lower()])[0]
            profile_link = user_data['profile_image_url']
        except IndexError as e:
            print(f'User {clip.streamer_name} may be banned')
            return None
        render_text(text=self.get_simple_link(clip),
                    width=0,
                    out_path=out_path,
                    style=TwitchSubtitleStyle(),
                    css_kwargs={'user_profile_link': profile_link})
        return out_path
