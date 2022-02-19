import os.path

import twitchdl
from twitchdl import utils
from twitchdl.commands.download import download, _video_target_filename, _clip_target_filename
from twitchdl import twitch
from twitchdl.exceptions import ConsoleError


class TwitchDownloader:
    def __init__(self, quality='source'):
        self.quality = quality
    class TwitchDLArgs:
        start = None
        end = None
        overwrite = True
        max_workers = 1
        no_join = True
        keep = False
        quality = None
        format = 'mkv'
        output = "{date}_{id}_{channel_login}_{title_slug}.{format}"
        video = None


    # video can be url, clip_id, video_id
    def get_output_filename(self, video, output_folder=None):
        args = self._create_args(video)
        if output_folder is not None:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            args.output = os.path.join(output_folder, args.output)
        video_id = utils.parse_video_identifier(video)
        if video_id:
            return _video_target_filename(video, args)

        clip_slug = utils.parse_clip_identifier(args.video)
        if clip_slug:
            clip = twitch.get_clip(clip_slug)
            return _clip_target_filename(clip, args)

    def _create_args(self, video):
        args = TwitchDownloader.TwitchDLArgs()
        args.quality = self.quality
        args.video = video
        return args

    # To download clip, pass id like 'CautiousArtisticParrotCorgiDerp-toHVnDwBtUjP0zdd', not video_id like '1270400144'
    def download(self, video_id, output_folder=None):
        args = self._create_args(video_id)
        if output_folder is not None:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            args.output = os.path.join(output_folder, args.output)
        try:
            download(args)
        except ConsoleError as e:
            if video_id in str(e) and 'not found' in str(e):
                return None
            else:
                raise
        return self.get_output_filename(video_id, output_folder=output_folder)

if __name__ == '__main__':
    downloader = TwitchDownloader()
    downloader.download('ScaryUnsightlyWhaleArgieB8-T4QOSrE4kVBpT6z2', 'output')
