from cp05_protocol_tool import Ui_Form
from PyQt5 import QtWidgets


class cp05_protocol_tool_form(QtWidgets.QWidget,Ui_Form) :
    def __init__(self):
        super(cp05_protocol_tool_form, self).__init__()
        self.setupUi(self)