import sys
import keyboard
import sqlite3
import subprocess

import add_window

from PyQt5.QtWidgets import (QApplication,
                             QMainWindow,
                             QTableWidgetItem)
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
        self.Window = add_window.AddWidget()
        self.Window.show()
        self.Window.login_data[list].connect(self.add_to_database)

    def del_macros(self, data):
        pass

    def change_macros(self):
        pass

    def add_to_database(self, data):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()
        cur.execute("""INSERT INTO macros(name, combination, file_name, url_file) VALUES(?, ?, ?, ?)""",
                    (data[0], data[2], data[1].split('/')[-1], data[1]))
        con.commit()
        con.close()

        self.add_combination()

    def add_combination(self):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()
        data = cur.execute("""SELECT combination, url_file FROM macros""").fetchall()
        con.close()

        for hotkey, url in data:
            keyboard.add_hotkey(hotkey, lambda x=url: subprocess.call(x, shell=True))

        self.table_update()

    def table_update(self):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()
        data = cur.execute("""SELECT id, name, combination, file_name FROM macros""").fetchall()
        con.close()

        self.macros_table.setRowCount(0)
        for i, row in enumerate(data):
            self.macros_table.setRowCount(self.macros_table.rowCount() + 1)
            for j, elem in enumerate(row[1::]):
                self.macros_table.setItem(i, j, QTableWidgetItem(elem))
        self.macros_table.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
