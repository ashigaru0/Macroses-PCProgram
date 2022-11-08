import sys
import keyboard
import sqlite3
import os

import add_window

from PyQt5.QtWidgets import (QApplication,
                             QMainWindow)
from design.py.macros import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.add_combination()
        self.btn()

    def btn(self):
        self.add_btn.clicked.connect(self.add_macros)

    def add_macros(self):
        self.add = add_window.AddWidget()
        self.add.show()
        self.add.login_data[list].connect(self.add_to_database)

    def del_macros(self, data):
        pass

    def change_macros(self):
        pass

    def add_to_database(self, data):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()

        cur.execute("""INSERT INTO macros(name, combination, file_name, url_file) VALUES(?, ?, ?, ?)""",
                    (data[0], data[2], os.path.basename(r'{}'.format(data[1])), data[1]))
        con.commit()
        con.close()

    def add_combination(self):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()

        data = cur.execute("""SELECT combination, url_file FROM macros""").fetchall()
        for hotkey, url in data:
            keyboard.add_hotkey(hotkey, lambda x=url: os.startfile(x))

        con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
