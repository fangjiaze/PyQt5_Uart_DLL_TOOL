from cp05_protocol_tool import Ui_Form
from PyQt5 import QtWidgets
import json
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class cp05_protocol_tool_form(QtWidgets.QWidget,Ui_Form) :
    def __init__(self):
        super(cp05_protocol_tool_form, self).__init__()
        self.setupUi(self)

        self.json_str = """{
            "map":[
                {"n":2,"param1":"string1data1","param2":"string1data2","button":"ctr1","callback":"abc"},
                {"n":1,"param1":"string2data1","button":"ctr2","callback":"abc"},
                {"n":3,"param1":"string3data1","param2":"string3data2","param3":"string3data3","button":"ctr3","callback":"abc"}
            ]
        }"""

        self.line_edit_map = []

        json_obj = json.loads(self.json_str)

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
            if "n" not in obj or "button" not in obj or "callback" not in obj:
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