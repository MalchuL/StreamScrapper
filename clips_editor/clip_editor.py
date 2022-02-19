import os.path

import ujson
from PyQt5 import QtWidgets, uic

import sys

from PyQt5.QtCore import QDir, Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QListWidgetItem, QAction, QFileDialog, QShortcut

from clips_editor.widgets.list_items.video_item import VideoItem
from clips_editor.widgets.list_widgets.thumb_list_widget import ThumbListWidget
from clips_editor.widgets.video_widgets.video_widget import VideoWidget


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('clips_editor/ui/clip_editor.ui', self)
        self.generate_menu_bar()

        self.clipsList: ThumbListWidget
        self.clipWidget: VideoWidget
        #self.clipsList.
        # Code from https://gist.github.com/Orizzu/e47393efe37c9e4846f7c23f2b10c4a7
        self.clipsList.currentItemChanged.connect(self.on_clip_click)



        # Arrows
        QShortcut(Qt.Key_Up, self, self.prev_video)
        QShortcut(Qt.Key_Down, self, self.next_video)


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
        self.clipWidget.open_video(item.mp4)
        print(item.clip_name)

    def generate_menu_bar(self):
        load_act = QAction('&Open Clips Json...', self)
        load_act.setShortcut('Ctrl+O')
        load_act.setStatusTip('Loads to UI clips json which generates with additional output field')
        load_act.triggered.connect(self.load_clips_json)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(load_act)

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