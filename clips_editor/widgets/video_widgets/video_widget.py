# -*- coding: utf-8 -*-
"""
@author: GitHub@Oscarshu0719
https://github.com/Oscarshu0719/video-editor/blob/master/main.py
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QAction, QComboBox, QFileDialog, QHBoxLayout,
                             QLabel, QMainWindow, QPushButton, QShortcut,
                             QSlider, QStyle, QVBoxLayout, QWidget)
import sys



class VideoWidget(QWidget):
    """ Class:
    Video player window.
    """

    # Main window size.
    WIN_SIZE = [800, 600]

    def __init__(self, parent=None):
        """ Function:
        Setup user interface of Video player window.
        """

        super(VideoWidget, self).__init__(parent)
        self.setWindowTitle("Video player")
        self.resize(VideoWidget.WIN_SIZE[0], VideoWidget.WIN_SIZE[1])
        self.setWindowIcon(
            self.style().standardIcon(QStyle.SP_DriveDVDIcon))

        self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.record_start_time = None
        self.record_end_time = None
        self.video_name = ""

        self.widget_video = QVideoWidget()


        self.button_play = QPushButton()
        self.button_play.setEnabled(False)
        self.button_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.button_play.clicked.connect(self.play_video)

        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.setRange(0, 0)
        self.video_slider.sliderMoved.connect(self.set_position)
        self.video_duration = 0

        # Button 'Open'.
        self.button_open = QPushButton('Open')
        self.button_open.clicked.connect(self.open_video)


        # Widget.
        self.widget_window = QWidget(self)

        self.statusbar = QtWidgets.QStatusBar(self)

        self.layout_operation = QHBoxLayout()
        self.layout_operation.setContentsMargins(0, 0, 0, 0)

        self.layout_operation.addWidget(self.statusbar)
        self.layout_operation.addWidget(self.button_open)

        self.layout_record = QHBoxLayout()
        self.layout_record.setContentsMargins(0, 0, 0, 0)

        # Widget layout.
        self.layout_widget = QHBoxLayout()
        self.layout_widget.setContentsMargins(0, 0, 0, 0)
        self.layout_widget.addWidget(self.button_play)
        self.layout_widget.addWidget(self.video_slider)

        self.layout_window = QVBoxLayout()
        self.layout_window.addWidget(self.widget_video)
        self.layout_window.addLayout(self.layout_record)
        self.layout_window.addLayout(self.layout_operation)
        self.layout_window.addLayout(self.layout_widget)

        # Window layout.
        self.setLayout(self.layout_window)

        self.video_player.setVideoOutput(self.widget_video)
        self.video_player.stateChanged.connect(self.media_state_changed)
        self.video_player.positionChanged.connect(self.position_changed)
        self.video_player.durationChanged.connect(self.duration_changed)
        self.video_player.error.connect(self.error_control)

        #QShortcut(Qt.Key_Up, self, self.arrow_up)
        #QShortcut(Qt.Key_Down, self, self.arrow_down)
        QShortcut(Qt.Key_Left, self, self.arrow_left_event)
        QShortcut(Qt.Key_Right, self, self.arrow_right_event)
        QShortcut(Qt.Key_Space, self, self.play_video)

    def arrow_up(self):
        if self.video_player.state() != QMediaPlayer.StoppedState:
            self.video_player.setVolume(min(self.video_player.volume() + 10, 100))

    def arrow_down(self):
        if self.video_player.state() != QMediaPlayer.StoppedState:
            self.video_player.setVolume(max(self.video_player.volume() - 10, 0))

    def arrow_left_event(self):
        """ Slot function:
        Action after the key 'arrow left' is pressed.
        Fast-forward to 10 seconds later.
        """

        self.set_position(self.video_slider.value() - 10 * 1000)

    def arrow_right_event(self):
        """ Slot function:
        Action after the key 'arrow right' is pressed.
        Go back to 10 seconds ago.
        """

        self.set_position(self.video_slider.value() + 10 * 1000)

    def mousePressEvent(self, event):
        """ Slot function:
        The starting position of the slider is 50.
        Note: This function still can't not accurately move the slider to the
        clicked position.
        """

        slider_start_pos = self.video_slider.geometry().topLeft().x()
        if 42 <= self.height() - event.pos().y() <= 62:
            position = self.video_slider.minimum() + (
                        event.pos().x() - slider_start_pos) / self.video_slider.width() * self.video_duration
            if position != self.video_slider.sliderPosition():
                self.set_position(position)

    def open_video(self, path=None):
        """ Slot function:
        Open a video from the file system.
        """
        if path is None:
            video_name, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                                                        QDir.homePath(), options=QFileDialog.DontUseNativeDialog)
        else:
            video_name = path
        self.video_name = video_name
        print(self.video_name)
        if self.video_name != '':

            self.video_player.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.video_name)))
            self.button_play.setEnabled(True)
            self.video_player.play()
            print(self.video_name)
            index = self.video_name.rfind('/')
            self.statusbar.showMessage(
                "Info: Playing the video '" + self.video_name[(index + 1):]
                + "' ...")

    def play_video(self):
        """ Slot function:
        The slot function for the 'play' button.
        If the video player is currently paused, then play the video;
        otherwise, pause the video.
        """

        if self.video_player.state() == QMediaPlayer.PlayingState:
            self.video_player.pause()
        else:
            self.video_player.play()

    def media_state_changed(self, state):
        """ Slot function:
        If the playing state changes, change the icon for the 'play' button.
        If the video player is currently playing, change the icon to 'pause';
        otherwise, change the icon to 'play'.
        """

        if self.video_player.state() == QMediaPlayer.PlayingState:
            self.button_play.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.button_play.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        """ Slot function:
        Change the position of the slider.
        """

        self.video_slider.setValue(position)

    def duration_changed(self, duration):
        """ Slot function:
        If the duration of the video changed, change the range of the slider.
        This slot function is called after opening a video.
        """

        self.video_slider.setRange(0, duration)
        self.video_duration = duration
        self.record_start_time = 0
        self.record_end_time = 0

    def set_position(self, position):
        """ Slot function:
        Change the progress of the video.
        """

        self.video_player.setPosition(position)

    def error_control(self):
        """ Slot function:
        If an error occurs while opening the video, this slot function is
        called.
        """

        self.button_play.setEnabled(False)
        self.statusbar.showMessage(
            "Error: An error occurs while opening the video.")

    def _check_duration(self):
        if self.video_name == "":
            self.statusbar.showMessage(
                "Error: Please open a video first.")
        elif self.record_start_time == self.record_end_time:
            self.statusbar.showMessage(
                "Error: Duration can NOT be 0.")
        elif self.record_start_time > self.record_end_time:
            self.statusbar.showMessage(
                "Error: The start time should be earlier than the end time.")
        else:
            return True

        return False





if __name__ == '__main__':
    """
    app = QApplication(sys.argv) will go wrong.
    """
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    player = VideoWidget()
    player.show()

    """
    sys.exit(app.exec_()) will go wrong.
    """
    app.exec_()