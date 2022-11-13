import keyboard

from PyQt5.QtWidgets import (QWidget,
                             QInputDialog,
                             QFileDialog,
                             QMessageBox)

from PyQt5.QtCore import pyqtSignal, Qt
from design.py.macros_add import Ui_Form


class AddWidget(QWidget, Ui_Form):
    login_data = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Добавить макрос')
        self.setWindowModality(Qt.ApplicationModal)
        self.reset()
        self.btn()

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
