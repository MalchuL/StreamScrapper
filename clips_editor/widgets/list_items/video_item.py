from PyQt5.QtCore import QSize, Qt

from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QPushButton, QListWidgetItem


class VideoItem(QListWidgetItem):
    def __init__(self, text, parent=None):
        super(VideoItem, self).__init__(text, parent)
        

