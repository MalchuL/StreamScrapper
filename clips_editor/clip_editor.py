import os.path

import ujson
from PyQt5 import QtWidgets, uic

import sys

from PyQt5.QtCore import QDir, Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QListWidgetItem, QAction, QFileDialog, QShortcut, QCheckBox, QSlider

from clips_editor.widgets.list_items.video_item import VideoItem
from clips_editor.widgets.list_widgets.thumb_list_widget import ThumbListWidget
from clips_editor.widgets.range_slider.range_slider import QRangeSlider
from clips_editor.widgets.video_widgets.video_widget import VideoWidget


class MainWindow(QtWidgets.QMainWindow):

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

        # Arrows
        QShortcut(Qt.Key_Up, self, self.prev_video)
        QShortcut(Qt.Key_Down, self, self.next_video)

    def start_cut_changed(self, value):
        if self.clipsList.currentItem() is not None:
            self.clipsList.currentItem().start_cut = value

    def end_cut_changed(self, value):
        if self.clipsList.currentItem() is not None:
            self.clipsList.currentItem().end_cut = value

    def set_volume(self, value):
        # Set volume in item
        if self.clipsList.currentItem() is not None:
            self.clipsList.currentItem().volume = value / 100
        self.clipWidget.set_volume(value)



    def keep_clip_check(self, state):
        #print(state, self.keepClip.isChecked())
        if self.clipsList.currentItem() is not None:
            self.clipsList.currentItem().keep_video(self.keepClip.isChecked())

    def prev_video(self):
        current_index = self.clipsList.currentIndex().row()
        new_index = current_index - 1
        if new_index < 0:
            new_index = self.clipsList.count() - 1
        self.clipsList.setCurrentRow(new_index)

    def next_video(self):
        current_index = self.clipsList.currentIndex().row()
        new_index = (current_index + 1) % self.clipsList.count()
        print(new_index)
        self.clipsList.setCurrentRow(new_index)


    def on_clip_click(self, item: VideoItem, old_item=None):
        self.update_video_editor(item)
        self.update_global_info()

    def update_global_info(self):
        self.clipsCountLabel.setText(f'Clips: {self.clipsList.currentIndex().row() + 1}/{self.clipsList.count()}')

    def update_video_editor(self, item: VideoItem):
        if item is not None:
            self.clipWidget.open_video(item.mp4)
            self.volumeSlider.setValue(item.volume * 100)
            self.durationLabel.setText(f'Duration: {item.vid_duration}')
            self.keepClip.setChecked(item.isUsed)



            # Draw slider values
            self.rangeSlider.setMin(0)
            self.rangeSlider.setMax(item.vid_duration)
            self.rangeSlider.setStart(item.start_cut)
            self.rangeSlider.setEnd(item.end_cut)
            self.rangeSlider.setDrawValues(True)
            self.rangeSlider.update()



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

    def load_clips_json(self):
        print('Try to open json file')
        json_path, _ = QFileDialog.getOpenFileName(self, "Open Clips Json",
                                                    QDir.currentPath(), options=QFileDialog.DontUseNativeDialog)
        base_folder = os.path.abspath(os.curdir) #os.path.dirname(json_path)
        self.baseFolderEdit.setText(base_folder)
        with open(json_path, 'r') as f:
            json_clips = ujson.load(f)

        for clip in json_clips:
            clip_name = clip['broadcaster_name'] + '/' + clip['title']
            video_item = VideoItem(text=clip_name, id=clip['id'], streamer_name=clip['broadcaster_name'],
                                             clip_title=clip['title'],
                                             mp4name=os.path.join(base_folder, clip['out_path']),
                                             vid_duration=clip['duration'])
            self.clipsList.addItem(video_item)



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()