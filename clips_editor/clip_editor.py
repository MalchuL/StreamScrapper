from PyQt5 import QtWidgets, uic

import sys

from PyQt5.QtWidgets import QListWidgetItem

from clips_editor.widgets.list_items.video_item import VideoItem
from clips_editor.widgets.video_widgets.video_widget import VideoWindow


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('clips_editor/ui/clip_editor.ui', self)

        for i in range(12):
            self.videoList.addItem(VideoItem( 'Item '+str(i)))

        VideoWindow(self)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()