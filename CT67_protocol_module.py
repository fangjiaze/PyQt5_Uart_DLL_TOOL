import json
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import struct  # 导入这个模块可以完成 hex格式数据来拼凑出bytes的数据来

from lc_pylib import crc_16
from User_ErrorDialog import error_dialog_run

ct67_msg_n = 0
temp_ui_uart_obj = None

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
    global temp_ui_uart_obj
    temp_ui_uart_obj = ui_uart_obj
    if index == 0:  # 心跳查询
        ct67_detail_cmd(line_edits[0].text())
        # ui_uart_obj.send_uart_data(1,line_edits[0].text().encode())
    elif index == 1:  # 租借
        ct67_rent_cmd(line_edits[0].text(), line_edits[1].text())
    elif index == 2:  # 运维出仓
        ct67_yunwei_out_cmd(line_edits[0].text(), line_edits[1].text())
    elif index == 3:  # 强制出仓
        ct67_force_out_cmd(line_edits[0].text(), line_edits[1].text())
    elif index == 4:  # 重启设备
        ct67_reset_device_cmd(line_edits[0].text())


def ct67_sent_cmd(aims, cmd, bytes_data):
    global ct67_msg_n
    len1 = len(bytes_data)
    aformat = f'>HBBH{len1}sI'.format(len1)  # > 表示 大端輸入  , B 表示 unsigned char,  H 表示 unsigned short , I 表示 unsigned int , s 表示 string
    prefix_data = struct.pack(aformat, 0x5aa5, aims, cmd, len1 + 4, bytes_data, ct67_msg_n)
    ct67_msg_n += 1
    crc_data = crc_16(0xffff, prefix_data)

    len1 = len(prefix_data)
    aformat = f'>{len1}sH'.format(len1)
    all_data = struct.pack(aformat, prefix_data, crc_data)


    temp_ui_uart_obj.send_uart_data(1, all_data)

    # return prefix_data + crc_data


def ct67_detail_cmd(str_aims):
    # 判断str_aims是否是数字
    if str_aims.isdigit():
        aims = int(str_aims)
        ct67_sent_cmd(aims, 0x01, b'\x00\x00\x00\x00\x00\x00')
    else :
        error_dialog_run("机组号必须为数字")


def ct67_rent_cmd(str_aims, str_n):
    if str_aims.isdigit() and str_n.isdigit():
        aims = int(str_aims)
        n = int(str_n)
        bytes_data = struct.pack('>B10s', n, bytes(10))
        ct67_sent_cmd(aims, 0x02, bytes_data)


def ct67_yunwei_out_cmd(str_aims, str_n):
    if str_aims.isdigit() and str_n.isdigit():
        aims = int(str_aims)
        n = int(str_n)
        bytes_data = struct.pack('>BB10s', 0x00, n, bytes(10))  # 0子命令 运维出仓
        ct67_sent_cmd(aims, 0x03, bytes_data)

def ct67_force_out_cmd(str_aims, str_n):
    if str_aims.isdigit() and str_n.isdigit():
        aims = int(str_aims)
        n = int(str_n)
        bytes_data = struct.pack('>BB10s', 0x01, n, bytes(10))  # 1子命令 强制出仓
        ct67_sent_cmd(aims, 0x03, bytes_data)


def ct67_reset_device_cmd(str_aims):
    if str_aims.isdigit():
        aims = int(str_aims)
        bytes_data = struct.pack('>BB10s', 0x02, 0x00, bytes(10))  # 2子命令 重启设备
        ct67_sent_cmd(aims, 0x03, bytes_data)