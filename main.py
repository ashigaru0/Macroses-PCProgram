import sys
import keyboard
import sqlite3
import subprocess

import add_window

from PyQt5.QtWidgets import (QApplication,
                             QMainWindow,
                             QTableWidgetItem,
                             QMessageBox)
from design.py.macros import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.modified = {}
        self.TITLES = {0: 'name', 1: 'combination', 2: 'file_name', 3: 'url_file'}
        self.add_combination()
        self.btn()

    def btn(self):
        self.add_btn.clicked.connect(self.add_macros)
        self.del_btn.clicked.connect(self.del_macros)
        self.change_btn.clicked.connect(self.change_macros)
        self.macros_table.itemChanged.connect(self.item_changed)
        self.macros_table.doubleClicked.connect(self.item_double_clicked)

    def add_macros(self):
        self.Window = add_window.AddWidget()
        self.Window.show()
        self.Window.login_data[list].connect(self.add_to_database)

    def del_macros(self):
        pass

    def change_macros(self):
        if self.modified:
            con = sqlite3.connect('macros_db.sqlite')
            cur = con.cursor()

            for id in self.modified.keys():
                que = "UPDATE macros SET\n"
                que += f"{self.TITLES[self.modified[id][1]]} = '{self.modified[id][0]}'\n"
                que += f'WHERE id = {id}'
                print(que)
                cur.execute(que)

            con.commit()
            con.close()
            self.modified.clear()
            self.table_update()

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
        data = cur.execute("""SELECT name, combination, file_name, url_file FROM macros""").fetchall()
        con.close()

        self.macros_table.setRowCount(0)
        for i, row in enumerate(data):
            self.macros_table.setRowCount(self.macros_table.rowCount() + 1)
            for j, elem in enumerate(row):
                self.macros_table.setItem(i, j, QTableWidgetItem(elem))

    def item_double_clicked(self, item):
        if item.column() == 1:
            hotkey = self.add_comb()
            self.modified[item.row() + 1] = [hotkey, item.column()]
            self.macros_table.cha

    def item_changed(self, item):
        self.modified[item.row() + 1] = [item.text(), item.column()]

    def add_comb(self):
        self.message('Нажмите комбинацию клавишь')
        hotkey = keyboard.read_hotkey(suppress=False)
        self.message('Готово')
        return hotkey

    def add_url(self):
        url = QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Все файлы (*)')[0]
        self.output[1] = url
        self.url_btn.setText(url)

    def message(self, text):
        message = QMessageBox()
        message.setWindowTitle("Сообщение")
        message.setText(text)
        message.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
