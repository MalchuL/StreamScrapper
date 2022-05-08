import copy
import os.path
import pickle
import subprocess

import ujson
from PyQt5 import QtWidgets, uic, QtMultimedia

import sys

from PyQt5.QtCore import QDir, Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QListWidgetItem, QAction, QFileDialog, QShortcut, QCheckBox, QSlider
from PyQt5 import QtCore

from clips_editor.widgets.list_items.video_item import VideoItem, Clip, DEFAULT_SUBS_ALIGNMENT, DEFAULT_TITLE_ALIGNMENT
from clips_editor.widgets.list_widgets.thumb_list_widget import ThumbListWidget
from clips_editor.widgets.range_slider.range_slider import QRangeSlider
from clips_editor.widgets.video_widgets.video_widget import VideoWidget


DEFAULT_CLIPS = None

class MainWindow(QtWidgets.QMainWindow):

    ON_RANGE_CHANGE_OFFSET = 2 # Seconds to move video after clip range changed

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('clips_editor/ui/clip_editor.ui', self)
        self.centralwidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralwidget)
        self.generate_menu_bar()

        self.clipsList: ThumbListWidget  # List with clips, ALL INFO HOLDS HERE
        self.clipWidget: VideoWidget  # Widget which holds current video
        self.keepClip: QCheckBox  # Checkbox which keep current video
        self.volumeSlider: QSlider
        self.rangeSlider: QRangeSlider
        # Code from https://gist.github.com/Orizzu/e47393efe37c9e4846f7c23f2b10c4a7
        self.clipsList.currentItemChanged.connect(self.on_clip_click)
        self.keepClip.stateChanged.connect(self.keep_clip_check)
        self.keepOnNext.stateChanged.connect(self.keep_next_video_clip_check)
        self.volumeSlider.valueChanged.connect(self.set_volume)

        self.rangeSlider.startValueChanged.connect(self.start_cut_changed)
        self.rangeSlider.endValueChanged.connect(self.end_cut_changed)

        self.player = self.clipWidget.video_player
        self.player.positionChanged.connect(self.on_video_time_position_changed)
        self.player.setNotifyInterval(10) # Calls positionChanged each 10 ms
        self.clipWidget.button_play.clicked.disconnect()  # Disconnect base player button signals
        self.clipWidget.button_play.clicked.connect(self.play_video)

        self.deleteButton.clicked.connect(self.delete_current)

        self.clipWidget.button_open.clicked.disconnect()
        self.clipWidget.button_open.clicked.connect(self.open_video)

        # QButtonGroup with allignment for subtitles in numpad style
        for i, button in enumerate(self.subsAllignmenButtonGroup.buttons()):
            self.subsAllignmenButtonGroup.setId(button, i + 1)
        self.subsAllignmenButtonGroup.button(DEFAULT_SUBS_ALIGNMENT).setChecked(True)
        self.subsAllignmenButtonGroup.buttonClicked.connect(self.set_subtitle_alignment)

        # QButtonGroup with allignment for title in numpad style
        for i, button in enumerate(self.titleAllignmenButtonGroup.buttons()):
            self.titleAllignmenButtonGroup.setId(button, i + 1)
        self.titleAllignmenButtonGroup.button(DEFAULT_TITLE_ALIGNMENT).setChecked(True)
        self.titleAllignmenButtonGroup.buttonClicked.connect(self.set_title_alignment)

        self.titleTextEdit.textChanged.connect(self.save_title)

        # Arrows
        QShortcut(Qt.Key_Up, self, self.prev_video)
        QShortcut(Qt.Key_Down, self, self.next_video)
        QShortcut(Qt.Key_Space, self, self.play_video)
        QShortcut(Qt.Key_Return, self, lambda: self.keepClip.setChecked(True))
        QShortcut(Qt.Key_Delete, self, self.delete_current)


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

    def delete_current(self):
        if self.clipsList.count() > 0:
            current_index = self.clipsList.currentIndex().row()
            self.clipsList.takeItem(current_index)
            if self.clipsList.count() > 0:
                new_index = current_index if current_index < self.clipsList.count() else self.clipsList.count() - 1
                self.clipsList.setCurrentRow(new_index)
        self.update_final_duration()

    def set_subtitle_alignment(self, button):
        item = self.clipsList.currentItem()
        if item is None:
            return
        item.clip.subs_alignment = self.subsAllignmenButtonGroup.id(button)

    def set_title_alignment(self, button):
        item = self.clipsList.currentItem()
        if item is None:
            return
        item.clip.title_alignment = self.titleAllignmenButtonGroup.id(button)

    def save_title(self):
        item = self.clipsList.currentItem()
        if item is None:
            return
        item.clip.title = self.titleTextEdit.toPlainText()

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
            if self.keepClip.isChecked():
                self.keepOnNext.setChecked(False)
            self.clipsList.currentItem().keep_video(self.keepClip.isChecked())
        self.keepClip: QCheckBox
        palette = self.keepClip.palette()

        if self.keepClip.isChecked():
            color = QColor(0, 255, 0)
        else:
            color = QColor(255, 0, 0)
        palette.setColor(QPalette.Active, QPalette.Base, color)
        self.keepClip.setPalette(palette)

    def keep_next_video_clip_check(self, state):
        if self.clipsList.currentItem() is not None:
            if self.keepOnNext.isChecked():
                self.keepClip.setChecked(False)
            self.clipsList.currentItem().keep_to_next_video(self.keepOnNext.isChecked())

        self.keepOnNext: QCheckBox
        palette = self.keepOnNext.palette()

        if self.keepOnNext.isChecked():
            color = QColor(0, 255, 0)
        else:
            color = QColor(255, 0, 0)
        palette.setColor(QPalette.Active, QPalette.Base, color)
        self.keepOnNext.setPalette(palette)

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
        self.update_final_duration()

    def update_video_editor(self, item: VideoItem):
        if item is not None:
            self.clipWidget.open_video(item.clip.filename)
            self.volumeSlider.setValue(item.clip.volume * 100)
            self.durationLabel.setText(f'Duration: {item.clip.vid_duration}')
            if hasattr(item.clip, 'views_count'):
                self.viewerCount.setText(f'Views: {item.clip.views_count}')
            self.keepClip.setChecked(item.clip.isUsed)
            self.keepOnNext.setChecked(item.clip.save_to_next)

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

            # Keep video to next video
            self.keepOnNext: QCheckBox
            palette = self.keepOnNext.palette()

            if self.keepOnNext.isChecked():
                color = QColor(0, 255, 0)
            else:
                color = QColor(255, 0, 0)
            palette.setColor(QPalette.Active, QPalette.Base, color)
            self.keepOnNext.setPalette(palette)

            self.subsAllignmenButtonGroup.button(item.clip.subs_alignment).setChecked(True)
            self.titleAllignmenButtonGroup.button(item.clip.title_alignment).setChecked(True)
            self.titleTextEdit.setPlainText(item.clip.title)

    def open_video(self):
        clip_path, _ = QFileDialog.getOpenFileName(self, "Open Video",
                                                    QDir.currentPath(), options=QFileDialog.DontUseNativeDialog)
        print(clip_path)
        if not clip_path:
            return

        title = os.path.splitext(os.path.basename(clip_path))[0]
        clip_name = "MY_VIDEOS"+ '/' + title
        duration = self.duration_for_file(clip_path)

        clip = Clip(id=0, streamer_name="!!MY_VID!!",
             clip_title=title,
             filename=os.path.abspath(clip_path),
             vid_duration=duration)
        print(clip)
        video_item = VideoItem(text=clip_name, clip=clip)
        if self.clipsList.count() > 0:
            current_index = self.clipsList.currentIndex().row()
            self.clipsList.insertItem(current_index, video_item)
        else:
            self.clipsList.addItem(video_item)


    @staticmethod
    def duration_for_file(filename):
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", filename],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        return float(result.stdout)

    def update_final_duration(self):
        video_len = self.get_result_len()
        self.finalDurationLabel.setText(f'Final duration: {video_len / 60:0.2f}m')

    def get_result_len(self):
        result_len = 0
        for i in range(self.clipsList.count()):
            clip_data: Clip = self.clipsList.item(i).clip
            if clip_data.isUsed:
                result_len += clip_data.end_cut - clip_data.start_cut
        return result_len

    def generate_menu_bar(self):
        load_act = QAction('&Open Clips Json...', self)
        load_act.setShortcut('Ctrl+O')
        load_act.setStatusTip('Loads to UI clips json which generates with additional output field')
        load_act.triggered.connect(self.load_clips_json)

        clear_act = QAction('&Clear List', self)
        clear_act.setShortcut('Ctrl+L')
        clear_act.setStatusTip('Clears list of clips')
        clear_act.triggered.connect(self.clipsList.clear)

        save_next_video = QAction('&Save clips for next video', self)
        save_next_video.setStatusTip('Save clips for next to binary file')
        save_next_video.triggered.connect(self.save_clips_to_file_for_next_video)

        save_act = QAction('&Save editor clips', self)
        save_act.setShortcut('Ctrl+S')
        save_act.setStatusTip('Save clips to binary file')
        save_act.triggered.connect(self.save_clips_to_file)

        load_pickle_act = QAction('&Load editor clips', self)
        load_pickle_act.setStatusTip('Load clips from binary file')
        load_pickle_act.triggered.connect(self.load_clips_from_file)


        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(load_act)
        fileMenu.addAction(clear_act)
        fileMenu.addSeparator()
        fileMenu.addAction(save_next_video)
        fileMenu.addSeparator()
        fileMenu.addAction(save_act)
        fileMenu.addAction(load_pickle_act)

    def save_clips_to_file(self):
        self.clipsList: ThumbListWidget
        dumped_clips = []
        for i in range(self.clipsList.count()):
            clip_data = self.clipsList.item(i).clip
            dumped_clips.append(clip_data)

        name, _ = QFileDialog.getSaveFileName(self, 'Save File', 'editor_clips_videos.clps', options=QFileDialog.DontUseNativeDialog)
        if not name:
            return

        twitch_video = {'clips': dumped_clips}

        with open(name, "wb") as f:
            pickle.dump(twitch_video, f)
        print('Saved object')

    def save_clips_to_file_for_next_video(self):
        self.clipsList: ThumbListWidget
        dumped_clips = []
        for i in range(self.clipsList.count()):
            clip_data = self.clipsList.item(i).clip
            if clip_data.save_to_next:
                clip_data = copy.deepcopy(clip_data)
                clip_data.save_to_next = False
                clip_data.isUsed = False
                dumped_clips.append(clip_data)

        name, _ = QFileDialog.getSaveFileName(self, 'Save File', 'editor_clips_videos_for_next_video.clps', options=QFileDialog.DontUseNativeDialog)
        if not name:
            return

        twitch_video = {'clips': dumped_clips}

        with open(name, "wb") as f:
            pickle.dump(twitch_video, f)
        print('Saved object')

    def load_clips_from_file(self):
        clips_path, _ = QFileDialog.getOpenFileName(self, "Open Clips Json",
                                                   QDir.currentPath(), options=QFileDialog.DontUseNativeDialog)
        print(clips_path)
        if not clips_path:
            return
        with open(clips_path, "rb") as f:
            twitch_video = pickle.load(f)
        dumped_clips = twitch_video['clips']
        for clip in dumped_clips:
            clip_name = clip.streamer_name + '/' + clip.clip_name
            video_item = VideoItem(text=clip_name, clip=clip)
            self.clipsList.addItem(video_item)

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

        items = []
        for clip in json_clips:
            if 'out_path' in clip: # Not all videos can be download
                clip_name = clip['broadcaster_name'] + '/' + clip['title']
                clip = Clip(id=clip['id'], streamer_name=clip['broadcaster_name'],
                                       clip_title=clip['title'],
                                       filename=os.path.join(base_folder, clip['out_path']),
                                       vid_duration=clip['duration'],
                                       views_count=clip['view_count'],
                                       clip_json=clip)
                video_item = VideoItem(text=clip_name, clip=clip)
                items.append(video_item)
        items = sorted(items, key=lambda x: x.clip.clip_json['view_count'], reverse=True)
        for item in items:
            self.clipsList.addItem(item)



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()