import sys

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidgetItem, QApplication

from clips_editor.widgets.list_widgets.thumb_list_widget import ThumbListWidget


class Dialog_01(QMainWindow):
    def __init__(self):
        super(QMainWindow,self).__init__()
        self.listItems={}

        myQWidget = QWidget()
        myBoxLayout = QVBoxLayout()
        myQWidget.setLayout(myBoxLayout)
        self.setCentralWidget(myQWidget)

        self.listWidgetB = ThumbListWidget(self)
        self.listWidgetA = ThumbListWidget(self)
        for i in range(12):
            self.listWidgetA.addItem(QListWidgetItem( 'Item '+str(i)))
        myBoxLayout.addWidget(self.listWidgetA)


        myBoxLayout.addWidget(self.listWidgetB)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog_1 = Dialog_01()
    dialog_1.show()
    dialog_1.resize(480,320)
    sys.exit(app.exec())