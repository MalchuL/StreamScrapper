from PyQt5.QtCore import QSize, Qt

from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QPushButton, QListWidgetItem


class Clip:
    def __init__(self, id, streamer_name, clip_title, filename, vid_duration):
        self.id = id
        self.streamer_name = streamer_name
        self.filename = filename
        self.clip_name = clip_title
        self.vid_duration = vid_duration
        self.upload = False
        self.isIntro = False
        self.isOutro = False
        self.isInterval = False
        self.isUsed = False
        self.volume = 1
        # Getting duration of video clips to trim a percentage of the beginning off
        self.start_cut = 0
        self.end_cut = self.vid_duration

    def __str__(self):
        return str(self.__dict__)

class VideoItem(QListWidgetItem):
    def __init__(self, text, clip, parent=None):
        super(VideoItem, self).__init__(text, parent)

        self.clip = clip

        self.keep_video(self.clip.isUsed)


    def keep_video(self, keep):
        self.clip.isUsed = keep
        if keep:
            self.setForeground(Qt.green)
        else:
            self.setForeground(Qt.red)

