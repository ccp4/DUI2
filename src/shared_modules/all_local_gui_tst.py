import sys, os, time
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtUiTools

class my_one(QThread):
    def __init__(self, times_in = 3):
        super(my_one, self).__init__()
        self.times = times_in

    def run(self):
        print("times entered =", self.times)
        for rept in range(self.times):
            print("rep n", rept, " of ", self.times)
            time.sleep(1)


class MultiRunner(QObject):
    def __init__(self):
        super(MultiRunner, self).__init__()
        self.thread_lst = []

    def run_one_work(self):
        new_thread = my_one(len(self.thread_lst) + 1)
        new_thread.start()
        self.thread_lst.append(new_thread)


class MainImgViewObject(QObject):
    def __init__(self, parent = None):
        super(MainImgViewObject, self).__init__(parent)
        self.parent_app = parent

        self.ui_dir_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = self.ui_dir_path + os.sep + "tmp_gui.ui"
        self.window = QtUiTools.QUiLoader().load(ui_path)
        self.window.setWindowTitle("Test DUI2")

        print("inside QObject")
        self.m_run = MultiRunner()
        self.window.RunPushButton.clicked.connect(self.run_one_clicked)
        self.window.show()

    def run_one_clicked(self):
        print("run_one_clicked(MainImgViewObject)")
        self.m_run.run_one_work()


def main():
    app = QApplication(sys.argv)
    m_obj = MainImgViewObject(parent = app)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

