from ct67_update_firmware_tool import Ui_update_Form
from PyQt5 import QtWidgets
import json
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox




class ct67_update_firmware_tool_form(QtWidgets.QWidget,Ui_update_Form) :
    def __init__(self, ui_obj):
        super(ct67_update_firmware_tool_form, self).__init__()
        self.setupUi(self)
        self.ui_obj = ui_obj # 为了提供串口发送接口给该线程

