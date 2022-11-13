import sys
import keyboard
import sqlite3
import subprocess

import add_window

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from design.py.macros import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('data/icon.png'))
        self.modified = []
        self.TITLES = {0: 'name', 1: 'combination', 2: 'file_name', 4: 'url_file', 3: 'working'}
        self.tray()
        self.setFixedSize(self.size())
        self.add_combination()
        self.btn()

    def btn(self):
        self.add_btn.clicked.connect(self.add_macros)
        self.del_btn.clicked.connect(self.deact_act_macros)
        self.change_btn.clicked.connect(self.change_macros)
        self.macros_table.itemChanged.connect(self.item_changed)
        self.macros_table.doubleClicked.connect(self.item_double_clicked)

    def add_macros(self):
        self.Window = add_window.AddWidget()
        self.Window.setWindowIcon(QIcon('data/icon.png'))
        self.Window.show()
        self.Window.login_data[list].connect(self.add_to_database)

    def deact_act_macros(self):
        row = self.macros_table.currentRow()
        if row != -1:
            text = self.macros_table.item(row, 3).text()
            value = None
            if text == 'Активирован':
                value = 'Деактивирован'
            elif text == 'Деактивирован':
                value = 'Активирован'
            self.macros_table.setItem(row, 3, QTableWidgetItem(value))

    def change_macros(self):
        if self.modified:
            con = sqlite3.connect('macros_db.sqlite')
            cur = con.cursor()

            data = cur.execute("""SELECT combination FROM macros""").fetchall()
            for hotkey in data:
                keyboard.remove_hotkey(hotkey[0])

            for change in self.modified:
                que = "UPDATE macros SET\n"
                que += f"{self.TITLES[change[1]]} = '{change[2]}'\n"
                que += f'WHERE id = {change[0]}'
                cur.execute(que)

            con.commit()
            con.close()
            self.add_combination()
            self.table_update()
            self.modified = []
            self.message('Готово')

    def add_to_database(self, data):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()

        okey = []
        macroses = cur.execute("""SELECT name, combination, url_file FROM macros""").fetchall()
        for macros in macroses:
            for item in data:
                if item in macros:
                    okey.append(False)
                else:
                    okey.append(True)

        if all(okey):
            cur.execute("""INSERT INTO macros(name, combination, file_name, url_file, working) VALUES(?, ?, ?, ?, ?)""",
                        (data[0], data[2], data[1].split('/')[-1], data[1], 'Активирован'))
        else:
            self.message('Макрос с такими же значениями уже существует')

        con.commit()
        con.close()

        self.add_combination()

    def add_combination(self):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()
        data = cur.execute("""SELECT combination, url_file FROM macros""").fetchall()
        con.close()

        for hotkey, url in data:
            keyboard.add_hotkey(hotkey, lambda x=url: self.open_file(x))

        self.table_update()

    def open_file(self, url):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()
        data = cur.execute("""SELECT working FROM macros
                              WHERE url_file = ?""", (url,)).fetchone()
        con.close()

        if data[0] == 'Активирован':
            subprocess.call(url, shell=True)

    def table_update(self):
        con = sqlite3.connect('macros_db.sqlite')
        cur = con.cursor()
        data = cur.execute("""SELECT name, combination, file_name, working, url_file FROM macros""").fetchall()
        con.close()

        self.macros_table.setRowCount(0)
        for i, row in enumerate(data):
            self.macros_table.setRowCount(self.macros_table.rowCount() + 1)
            for j, elem in enumerate(row):
                item = QTableWidgetItem(elem)
                if j > 0:
                    item.setFlags(Qt.ItemIsEnabled)
                self.macros_table.setItem(i, j, item)

    def item_double_clicked(self, item):
        if item.column() == 1:
            hotkey = self.add_comb()
            item_hotkey = QTableWidgetItem(hotkey)
            item_hotkey.setFlags(Qt.ItemIsEnabled)
            self.macros_table.setItem(item.row(), item.column(), item_hotkey)
        elif item.column() == 4:
            url = self.add_url()
            if url:
                item_file = QTableWidgetItem(url.split('/')[-1])
                item_url = QTableWidgetItem(url)
                item_url.setFlags(Qt.ItemIsEnabled)
                item_file.setFlags(Qt.ItemIsEnabled)
                self.macros_table.setItem(item.row(), item.column() - 1, item_file)
                self.macros_table.setItem(item.row(), item.column(), item_url)

    def item_changed(self, item):
        self.modified.append([item.row() + 1, item.column(), item.text()])

    def add_comb(self):
        self.message('Нажмите комбинацию клавишь')
        hotkey = keyboard.read_hotkey(suppress=False)
        self.message('Готово')
        return hotkey

    def add_url(self):
        return QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Все файлы (*)')[0]

    def message(self, text):
        message = QMessageBox()
        message.setWindowTitle("Сообщение")
        message.setText(text)
        message.exec_()

    def tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('data/icon.png'))

        show_action = QAction("Показать", self)
        quit_action = QAction("Выход", self)
        hide_action = QAction("Свернуть", self)

        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(QApplication.quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        if self.tray_cb.isChecked():
            event.ignore()
            self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
