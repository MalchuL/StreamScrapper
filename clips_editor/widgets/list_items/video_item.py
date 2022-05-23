from PyQt5.QtCore import QSize, Qt

from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QPushButton, QListWidgetItem


DEFAULT_SUBS_ALIGNMENT = 1
DEFAULT_TITLE_ALIGNMENT = 0

class Clip:
    def __init__(self, id, streamer_name, clip_title, filename, vid_duration, views_count=0, clip_json=None):

        self.id = id
        self.streamer_name = streamer_name
        self.filename = filename
        self.clip_name = clip_title
        self.views_count = views_count
        self.vid_duration = vid_duration
        self.upload = False
        self.isIntro = False
        self.isOutro = False
        self.isInterval = False
        self.isUsed = False
        self.apply_sr = False
        self.save_to_next = False
        self.volume = 1
        # Getting duration of video clips to trim a percentage of the beginning off
        self.start_cut = 0
        self.end_cut = self.vid_duration
        self.subs_alignment = DEFAULT_SUBS_ALIGNMENT
        self.title_alignment = DEFAULT_TITLE_ALIGNMENT
        if clip_json is None:
            clip_json = {'title': ''}
        self.title = clip_json["title"]

        #clip_json example
        """    
        {
            "broadcaster_id": "46308104",
            "broadcaster_name": "Froggee",
            "created_at": "2022-01-23T12:08:07Z",
            "creator_id": "403772639",
            "creator_name": "l_tsanka",
            "duration": 10.5,
            "embed_url": "https://clips.twitch.tv/embed?clip=DrabBusyAmazonOMGScoots-c-uopLn8xYNzSJbp",
            "game_id": "509658",
            "id": "DrabBusyAmazonOMGScoots-c-uopLn8xYNzSJbp",
            "language": "ru",
            "thumbnail_url": "https://clips-media-assets2.twitch.tv/AT-cm%7CvrkLPnPrqKS5_MWDc0iW6Q-preview-480x272.jpg",
            "title": "\u0442\u0438\u043f\u0438\u0447\u043d\u044b\u0439 \u0441\u0442\u0440\u0438\u043c\u0435\u0440 \u0442\u0432\u0438\u0447\u0430",
            "url": "https://clips.twitch.tv/DrabBusyAmazonOMGScoots-c-uopLn8xYNzSJbp",
            "video_id": "",
            "view_count": 20
        }
        """
        self.clip_json = clip_json

    def __str__(self):
        return str(self.__dict__)

class VideoItem(QListWidgetItem):
    def __init__(self, text, clip, parent=None):
        super(VideoItem, self).__init__(text, parent)

        self.clip = clip

        self.keep_video(self.clip.isUsed)
        self.keep_to_next_video(self.clip.save_to_next)


    def keep_video(self, keep):
        self.clip.isUsed = keep
        if keep:
            self.setForeground(Qt.green)
        else:
            self.setForeground(Qt.red)

    def keep_to_next_video(self, keep):
        self.clip.save_to_next = keep
        if keep:
            if not self.clip.isUsed:
                self.setForeground(Qt.blue)
        else:
            if not self.clip.isUsed:
                self.setForeground(Qt.red)
