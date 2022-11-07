import sys
import keyboard
import sqlite3
import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication,
                             QMainWindow,
                             QWidget,
                             QInputDialog,
                             QFileDialog,
                             QMessageBox)
from design.py.macros import Ui_MainWindow
from design.py.macros_add import Ui_Form


class AddWidget(QWidget, Ui_Form):
    login_data = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.reset()
        self.btn()

    def abcd(self):
        pass

    def btn(self):
        self.name_btn.clicked.connect(self.add_name)
        self.url_btn.clicked.connect(self.add_url)
        self.comb_btn.clicked.connect(self.add_comb)

        self.reset_btn.clicked.connect(self.reset)
        self.done_btn.clicked.connect(self.done)
        self.cancel_btn.clicked.connect(self.cancel)

    def add_name(self):
        name, ok_pressed = QInputDialog.getText(self, 'Название', 'Укажите название макроса')
        if ok_pressed:
            self.output[0] = name
            self.name_btn.setText(name)

    def add_url(self):
        url = QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Все файлы (*)')[0]
        self.output[1] = url
        self.url_btn.setText(url)

    def add_comb(self):
        self.message('Нажмите комбинацию клавишь')
        hotkey = keyboard.read_hotkey(suppress=False)
        self.output[2] = hotkey
        self.comb_btn.setText(hotkey)
        self.message('Готово')

    def reset(self):
        self.output = ['', '', '']
        self.comb_btn.setText("Указать комбинацию клавишь")
        self.name_btn.setText("Указать название макроса")
        self.url_btn.setText("Указать ссылку на файл")

    def done(self):
        if all(self.output):
            self.login_data.emit(self.output)
            self.close()
        else:
            self.message('Указаны не все пункты')

    def cancel(self):
        self.close()

    def message(self, text):
        message = QMessageBox()
        message.setWindowTitle("Сообщение")
        message.setText(text)
        message.exec_()


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
        self.add = AddWidget()
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
