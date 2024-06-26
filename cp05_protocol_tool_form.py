from PyQt5.QtCore import pyqtSignal

from cp05_protocol_tool import Ui_Form
from PyQt5 import QtWidgets
import json
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox

from CT67_protocol_module import CT67_protocol_module


class cp05_protocol_tool_form(QtWidgets.QWidget,Ui_Form) :

    def __init__(self, ui_obj, protocol):
        super(cp05_protocol_tool_form, self).__init__()
        self.setupUi(self)

        # self.json_str = protocol.json_str
        self.protocol = CT67_protocol_module(ui_obj)  # CT67 协议模块

        ui_obj.protocol_output_data_signal.connect(self.protocol.protocol_uart_rec_process)  # 绑定 串口发送信号到CT67的接收协议模块去处理该数据
        # self.ui_obj = ui_obj # 为了提供串口发送接口给该线程

        self.line_edit_map = []

        json_obj = json.loads(self.protocol.json_str)

        if not self.validate_json(json_obj):
            QMessageBox.critical(None, "Error", "Invalid JSON data")
            return

        self.create_gui(json_obj)

    def create_gui(self, json_obj):
        # global line_edit_map
        # line_edit_map = {}

        # app = QApplication([])
        # self.widget = QWidget()
        # self.layout = QGridLayout()

        for i, obj in enumerate(json_obj["map"]):
            line_edit_list = []
            for j in range(obj["n"]):
                self.gridLayout.addWidget(QLabel(obj[f"param{j + 1}"]), i, j * 2)
                line_edit = QLineEdit()
                self.gridLayout.addWidget(line_edit, i, j * 2 + 1)
                line_edit_list.append(line_edit)

            button = QPushButton(obj["button"])
            self.gridLayout.addWidget(button, i, obj["n"] * 2)

            # self.line_edit_map[obj["button"]] = line_edit_list
            self.line_edit_map.append(line_edit_list)

            # button.clicked.connect(lambda checked, text=obj["button"]: self.callback(text))
            button.clicked.connect(lambda checked, index=i: self.callback(index))

        # self.widget.setLayout(self.layout)
        # self.widget.show()


    def validate_json(self, json_obj):
        if "map" not in json_obj:
            return False
        for obj in json_obj["map"]:
            if "n" not in obj or "button" not in obj :
                return False
            for i in range(1, obj["n"] + 1):
                if f"param{i}" not in obj:
                    return False
        return True

    def callback(self, index):
        # global line_edit_map
        line_edits = self.line_edit_map[index]


        for line_edit in line_edits:
            print(line_edit.text())

        self.protocol.protocol_fuction(index, line_edits)



    