import json

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, \
    QFileDialog, QProgressBar, QDialog, QVBoxLayout
import struct  # 导入这个模块可以完成 hex格式数据来拼凑出bytes的数据来

from lc_pylib import crc_16
from User_ErrorDialog import error_dialog_run
import time

ct67_msg_n = 0
temp_ui_uart_obj = None

json_str = """{
    "map":[
        {"n":1,"param1":"机组号","button":"心跳查询"},
        {"n":2,"param1":"机组号","param2":"仓道口","button":"租借"},
        {"n":2,"param1":"机组号","param2":"仓道口","button":"运维出仓"},
        {"n":2,"param1":"机组号","param2":"仓道口","button":"强制出仓"},
        {"n":1,"param1":"机组号","button":"重启设备"},
        {"n":1,"param1":"机组号","button":"固件更新"}
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
    elif index == 5:  # 重启设备
        ct67_update_firmware_cmd(line_edits[0].text())


def ct67_sent_cmd(aims, cmd, bytes_data):
    global ct67_msg_n
    len1 = len(bytes_data)
    aformat = f'>HBBH{len1}sI'.format(len1)  #  > 表示 大端輸入  , B 表示 unsigned char,  H 表示 unsigned short , I 表示 unsigned int , s 表示 string
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
        ct67_sent_cmd(aims, 0x04, bytes_data)

def ct67_force_out_cmd(str_aims, str_n):
    if str_aims.isdigit() and str_n.isdigit():
        aims = int(str_aims)
        n = int(str_n)
        bytes_data = struct.pack('>BB10s', 0x01, n, bytes(10))  # 1子命令 强制出仓
        ct67_sent_cmd(aims, 0x04, bytes_data)


def ct67_reset_device_cmd(str_aims):
    if str_aims.isdigit():
        aims = int(str_aims)
        bytes_data = struct.pack('>BB10s', 0x02, 0x00, bytes(10))  # 2子命令 重启设备
        ct67_sent_cmd(aims, 0x04, bytes_data)




def ct67_update_firmware_cmd(str_aims):
    file_dialog = ct67_FileDialog()
    file_dialog.show()
    loop = file_dialog.exec_loop
    loop.exec_()
    # file_path, _ = QFileDialog.getOpenFileName(temp_ui_uart_obj, 'Select File', '', 'Binary files (*.bin)')
    #
    # if file_path:
    #     with open(file_path, 'rb') as file:
    #         file_content = file.read()
    #         ct67_sendFile(file_content)


def ct67_sendFile(file_content):
    global temp_ui_uart_obj

    if temp_ui_uart_obj is None:
        return

    progress = QProgressBar(temp_ui_uart_obj)
    progress.setGeometry(50, 150, 200, 20)

    total_bytes = len(file_content)
    bytes_sent = 0

    while bytes_sent < total_bytes:
        time.sleep(0.1)
        bytes_sent += 1000 # Simulate sending 1000 bytes at a time
        progress_value = int((bytes_sent / total_bytes) * 100)
        progress.setValue(progress_value)

        if bytes_sent >= total_bytes:
            QMessageBox.information(temp_ui_uart_obj, 'Success', 'File sent successfully!')
            progress.deleteLater()


class ct67_FileDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.exec_loop = QEventLoop()

    def initUI(self):
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('乐畅-固件更新')

        self.file_path = QLineEdit()
        self.btn_select_file = QPushButton('Select File')
        self.btn_select_file.clicked.connect(self.selectFile)

        self.btn_send_file = QPushButton('Send File Content')
        self.btn_send_file.clicked.connect(self.sendFile)

        self.progress = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(self.file_path)
        layout.addWidget(self.btn_select_file)
        layout.addWidget(self.btn_send_file)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def selectFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择更新固件', '', 'Binary files (*.bin)')

        if file_path:
            self.file_path.setText(file_path)

    def sendFile(self):
        file_path = self.file_path.text()

        if file_path:
            with open(file_path, 'rb') as file:
                file_content = file.read()
                total_bytes = len(file_content)
                bytes_sent = 0

                while bytes_sent < total_bytes:
                    time.sleep(0.01)
                    bytes_sent += 1000 # Simulate sending 1000 bytes at a time
                    progress_value = int((bytes_sent / total_bytes) * 100)
                    self.progress.setValue(progress_value)

                    if bytes_sent >= total_bytes:
                        QMessageBox.information(self, '更新成功', '哥们,文件发送成功了!')
