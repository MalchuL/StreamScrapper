import os.path

from twitchdl.commands.download import download



class TwitchDownloader:
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

    # To download clip, pass id like 'CautiousArtisticParrotCorgiDerp-toHVnDwBtUjP0zdd', not video_id like '1270400144'
    def download(self, video_id, output_folder=None, quality='source'):
        args = TwitchDownloader.TwitchDLArgs()
        args.quality = quality
        args.video = video_id
        if output_folder is not None:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            args.output = os.path.join(output_folder, args.output)
        download(args)


if __name__ == '__main__':
    downloader = TwitchDownloader()
    downloader.download('ScaryUnsightlyWhaleArgieB8-T4QOSrE4kVBpT6z2', 'output')
