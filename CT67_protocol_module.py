import json
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import struct  # 导入这个模块可以完成 hex格式数据来拼凑出bytes的数据来

json_str = """{
    "map":[
        {"n":1,"param1":"机组号","button":"心跳查询"},
        {"n":2,"param1":"机组号","param2":"仓道口","button":"租借"},
        {"n":2,"param1":"机组号","param2":"仓道口","button":"运维出仓"},
        {"n":2,"param1":"机组号","param2":"仓道口","button":"强制出仓"},
        {"n":1,"param1":"机组号","button":"重启设备"}
    ]
}"""


def protocol_fuction(ui_uart_obj, index, line_edits):
    if index == 0:  # 心跳查询
        ui_uart_obj.send_uart_data(1,line_edits[0].text().encode())
    elif index == 1:  # 租借
        pass
    elif index == 2:  # 运维出仓
        pass
    elif index == 3:  # 强制出仓
        pass
    elif index == 4:  # 重启设备
        pass

