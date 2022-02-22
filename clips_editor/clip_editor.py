import os.path

import ujson
from PyQt5 import QtWidgets, uic, QtMultimedia

import sys

from PyQt5.QtCore import QDir, Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QListWidgetItem, QAction, QFileDialog, QShortcut, QCheckBox, QSlider
from PyQt5 import QtCore

from clips_editor.widgets.list_items.video_item import VideoItem
from clips_editor.widgets.list_widgets.thumb_list_widget import ThumbListWidget
from clips_editor.widgets.range_slider.range_slider import QRangeSlider
from clips_editor.widgets.video_widgets.video_widget import VideoWidget


DEFAULT_CLIPS = '/home/malchul/work/streams/stream_parser/twitch_clips_new/dumped_clips_data.json'

class MainWindow(QtWidgets.QMainWindow):

    ON_RANGE_CHANGE_OFFSET = 2 # Seconds to move video after clip range changed

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('clips_editor/ui/clip_editor.ui', self)
        self.generate_menu_bar()

        self.clipsList: ThumbListWidget  # List with clips, ALL INFO HOLDS HERE
        self.clipWidget: VideoWidget  # Widget which holds current video
        self.keepClip: QCheckBox  # Checkbox which keep current video
        self.volumeSlider: QSlider
        self.rangeSlider: QRangeSlider
        # Code from https://gist.github.com/Orizzu/e47393efe37c9e4846f7c23f2b10c4a7
        self.clipsList.currentItemChanged.connect(self.on_clip_click)
        self.keepClip.stateChanged.connect(self.keep_clip_check)
        self.volumeSlider.valueChanged.connect(self.set_volume)

        self.rangeSlider.startValueChanged.connect(self.start_cut_changed)
        self.rangeSlider.endValueChanged.connect(self.end_cut_changed)

        self.player = self.clipWidget.video_player
        self.player.positionChanged.connect(self.on_video_time_position_changed)
        self.player.setNotifyInterval(10) # Calls positionChanged each 10 ms
        self.clipWidget.button_play.clicked.disconnect()  # Disconnect base player button signals
        self.clipWidget.button_play.clicked.connect(self.play_video)

        # Arrows
        QShortcut(Qt.Key_Up, self, self.prev_video)
        QShortcut(Qt.Key_Down, self, self.next_video)
        QShortcut(Qt.Key_Space, self, self.play_video)
        QShortcut(Qt.Key_Return, self, lambda: self.keepClip.setChecked(True))


        # Todo fix this
        self._default_clips_path = DEFAULT_CLIPS
        if DEFAULT_CLIPS is not None:
            self.load_clips_json()
            self._default_clips_path = None


        self._video_pos = 0

    def start_cut_changed(self, value):
        item = self.clipsList.currentItem()
        if item is not None:
            item.clip.start_cut = value
            self.start_play(item.clip.start_cut)

    def end_cut_changed(self, value):
        item = self.clipsList.currentItem()
        if item is not None:
            item.clip.end_cut = value
            self.start_play(item.clip.end_cut - self.ON_RANGE_CHANGE_OFFSET)

    def start_play(self, play_at):
        """
            path: path of video
            start: time in ms from where the playback starts
            end: time in ms where playback ends
        """
        self.player.stop()
        self.player.setPosition(play_at * 1000)
        self.player.play()

    def play_video(self):
        """ Slot function:
        The slot function for the 'play' button.
        If the video player is currently paused, then play the video;
        otherwise, pause the video.
        """

        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            item = self.clipsList.currentItem()
            if item is None:
                return
            if self._video_pos < item.clip.start_cut * 1000 or self._video_pos > item.clip.end_cut * 1000 or self.player.state() == QMediaPlayer.StoppedState:
                self.player.setPosition(item.clip.start_cut * 1000)
            self.player.play()


    @QtCore.pyqtSlot('qint64')
    def on_video_time_position_changed(self, position):
        self._video_pos = position
        item = self.clipsList.currentItem()
        if item is None:
            return
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            if position / 1000 > item.clip.end_cut:
                self.player.stop()
            self.videoTime.setText(f'Time: {position / 1000}')

    def set_volume(self, value):
        # Set volume in item
        if self.clipsList.currentItem() is not None:
            self.clipsList.currentItem().clip.volume = value / 100
        self.clipWidget.set_volume(value)



    def keep_clip_check(self, state):
        if self.clipsList.currentItem() is not None:
            self.clipsList.currentItem().keep_video(self.keepClip.isChecked())
        self.keepClip: QCheckBox
        palette = self.keepClip.palette()

        if self.keepClip.isChecked():
            color = QColor(0, 255, 0)
        else:
            color = QColor(255, 0, 0)
        palette.setColor(QPalette.Active, QPalette.Base, color)
        self.keepClip.setPalette(palette)

    def prev_video(self):
        if self.clipsList.count() > 0:
            current_index = self.clipsList.currentIndex().row()
            new_index = current_index - 1
            if new_index < 0:
                new_index = self.clipsList.count() - 1
            self.clipsList.setCurrentRow(new_index)

    def next_video(self):
        if self.clipsList.count() > 0:
            current_index = self.clipsList.currentIndex().row()
            new_index = (current_index + 1) % self.clipsList.count()
            self.clipsList.setCurrentRow(new_index)


    def on_clip_click(self, item: VideoItem, old_item=None):
        self.update_video_editor(item)
        self.update_global_info()

    def update_global_info(self):
        self.clipsCountLabel.setText(f'Clips: {self.clipsList.currentIndex().row() + 1}/{self.clipsList.count()}')

    def update_video_editor(self, item: VideoItem):
        if item is not None:
            self.clipWidget.open_video(item.clip.filename)
            self.volumeSlider.setValue(item.clip.volume * 100)
            self.durationLabel.setText(f'Duration: {item.clip.vid_duration}')
            self.keepClip.setChecked(item.clip.isUsed)

            # Draw slider values

            # We should disconnect end value changed because it would be called
            self.rangeSlider.endValueChanged.disconnect()

            self.rangeSlider.setMin(0)
            self.rangeSlider.setMax(item.clip.vid_duration)
            self.rangeSlider.setStart(item.clip.start_cut)
            self.rangeSlider.setEnd(item.clip.end_cut)
            self.rangeSlider.setDrawValues(True)
            self.rangeSlider.update()
            # Connect it back
            self.rangeSlider.endValueChanged.connect(self.end_cut_changed)

            # Keep video
            self.keepClip: QCheckBox
            palette = self.keepClip.palette()

            if self.keepClip.isChecked():
                color = QColor(0, 255, 0)
            else:
                color = QColor(255, 0, 0)
            palette.setColor(QPalette.Active, QPalette.Base, color)
            self.keepClip.setPalette(palette)



    def generate_menu_bar(self):
        load_act = QAction('&Open Clips Json...', self)
        load_act.setShortcut('Ctrl+O')
        load_act.setStatusTip('Loads to UI clips json which generates with additional output field')
        load_act.triggered.connect(self.load_clips_json)

        clear_act = QAction('&Clear List', self)
        clear_act.setShortcut('Ctrl+L')
        clear_act.setStatusTip('Clears list of clips')
        clear_act.triggered.connect(self.clipsList.clear)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(load_act)
        fileMenu.addAction(clear_act)

    # def save_preds_to_file(self):
    #     self.clipsList: ThumbListWidget
    #     for item in self.clipsList.i

    def load_clips_json(self):
        print('Try to open json file')
        path = self._default_clips_path
        if path is None:
            json_path, _ = QFileDialog.getOpenFileName(self, "Open Clips Json",
                                                        QDir.currentPath(), options=QFileDialog.DontUseNativeDialog)
        else:
            json_path = path
        print(f'Opens {json_path} path')
        if json_path is None or json_path == '' or json_path==False :
            return
        base_folder = os.path.abspath(os.curdir) #os.path.dirname(json_path)
        self.baseFolderEdit.setText(base_folder)
        with open(json_path, 'r') as f:
            json_clips = ujson.load(f)

        for clip in json_clips:
            if 'out_path' in clip: # Not all videos can be download
                clip_name = clip['broadcaster_name'] + '/' + clip['title']
                video_item = VideoItem(text=clip_name, id=clip['id'], streamer_name=clip['broadcaster_name'],
                                       clip_title=clip['title'],
                                       filename=os.path.join(base_folder, clip['out_path']),
                                       vid_duration=clip['duration'])
                self.clipsList.addItem(video_item)



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()