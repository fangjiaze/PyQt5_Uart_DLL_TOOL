import json
import sys
import traceback

from PyQt5.QtCore import QEventLoop, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, \
    QFileDialog, QProgressBar, QDialog, QVBoxLayout
import struct  # 导入这个模块可以完成 hex格式数据来拼凑出bytes的数据来

from ct67_update_firmware_tool_form import ct67_update_firmware_tool_form
from lc_pylib import crc_16
from User_ErrorDialog import error_dialog_run
import time
# ct67_msg_n = 0
# temp_ui_uart_obj = None
class CT67_protocol_module(object):


    def __init__(self, temp_ui_uart_obj):
        self.temp_ui_uart_obj = temp_ui_uart_obj
        self.ct67_msg_n = 0
        self.json_str = """{
            "map":[
                {"n":1,"param1":"机组号","button":"心跳查询"},
                {"n":2,"param1":"机组号","param2":"仓道口","button":"租借"},
                {"n":2,"param1":"机组号","param2":"仓道口","button":"运维出仓"},
                {"n":2,"param1":"机组号","param2":"仓道口","button":"强制出仓"},
                {"n":1,"param1":"机组号","button":"重启设备"},
                {"n":1,"param1":"机组号","button":"固件更新"}
            ]
        }"""

    def protocol_uart_rec_process(self, data):
        
        len1 = len(data)

        if(len1 <= 8):
            return
        try:

            if data[0] != 0x5A or data[1] != 0xA5:
                return

            result = struct.unpack(f">HBBH", data[:6])
            data_len = result[3]
            crc_check_result = struct.unpack(f">{data_len + 6}sH", data[:data_len + 8])
            if crc_check_result[1] != crc_16(0xffff, crc_check_result[0]) :
                print("校验失败")
            else:
                print(f"地址：{result[1]},指令值：{result[2]},数据长度：{result[3]}")

            result = struct.unpack(f">HBBH{data_len}sH", data[:data_len + 8])

            if result[2] == 1:  # 心跳查询
                print("心跳应答")
            elif result[2] == 2:  # 租借
                print("租借应答")
            elif result[2] == 4:  # 运维出仓
                print("控制应答")
            elif result[2] == 5:  # 启动更新 固件更新
                print("固件更新应答")
                update_list = [5]
                self.temp_ui_uart_obj.update_response_signal.emit(update_list)
            elif result[2] == 6:  # 更新查询
                print("更新查询应答")
                data_tuple = struct.unpack(">II", result[4])
                if data_tuple[0] == 0:
                    print("===>处理失败")
                elif data_tuple[0] == 1:
                    print("===>升级模式中")
                elif data_tuple[0] == 2:
                    print("===>正常模式中")
            elif result[2] == 7:  # 固件发送应答
                print("固件发送应答")
                data_tuple = struct.unpack(">BBII", result[4])
                update_list = [7]
                update_list.append(data_tuple[2])  # 传输下载了多少byte
                print(update_list)
                self.temp_ui_uart_obj.update_response_signal.emit(update_list)
        except:
            # 获取当前的堆栈跟踪信息
            tb = traceback.extract_tb(sys.exc_info()[2])
            # 输出异常发生的行号
            print(f"Exception occurred at line {tb[-1].lineno}")
            print("指令有误,解析异常")




                

    def protocol_fuction(self, index, line_edits):
        if index == 0:  # 心跳查询
            self.ct67_detail_cmd(line_edits[0].text())
            # ui_uart_obj.send_uart_data(1,line_edits[0].t().encextode())
        elif index == 1:  # 租借
            self.ct67_rent_cmd(line_edits[0].text(), line_edits[1].text())
        elif index == 2:  # 运维出仓
            self.ct67_yunwei_out_cmd(line_edits[0].text(), line_edits[1].text())
        elif index == 3:  # 强制出仓
            self.ct67_force_out_cmd(line_edits[0].text(), line_edits[1].text())
        elif index == 4:  # 重启设备
            self.ct67_reset_device_cmd(line_edits[0].text())
        elif index == 5:  # 固件更新
            self.ct67_update_firmware_cmd(line_edits[0].text())


    def ct67_sent_cmd(self, aims, cmd, bytes_data, debug_flag):
        len1 = len(bytes_data)
        aformat = f'>HBBH{len1}sI'  #  > 表示 大端輸入  , B 表示 unsigned char,  H 表示 unsigned short , I 表示 unsigned int , s 表示 string
        prefix_data = struct.pack(aformat, 0x5aa5, aims, cmd, len1 + 4, bytes_data, self.ct67_msg_n)
        self.ct67_msg_n += 1
        crc_data = crc_16(0xffff, prefix_data)

        len1 = len(prefix_data)
        aformat = f'>{len1}sH'.format(len1)
        all_data = struct.pack(aformat, prefix_data, crc_data)
        if debug_flag :
            self.temp_ui_uart_obj.send_uart_data(1, all_data)
        else :
            self.temp_ui_uart_obj.send_uart_put_data(all_data)
            # self.temp_ui_uart_obj.send_uart_data(2, all_data)  # 不打印
    # return prefix_data + crc_data


    def ct67_detail_cmd(self, str_aims):
        # 判断str_aims是否是数字
        if str_aims.isdigit():
            aims = int(str_aims)
            self.ct67_sent_cmd(aims, 0x01, b'\x00\x00\x00\x00\x00\x00', 1)
        else :
            error_dialog_run("机组号必须为数字")


    def ct67_rent_cmd(self, str_aims, str_n):
        if str_aims.isdigit() and str_n.isdigit():
            aims = int(str_aims)
            n = int(str_n)
            bytes_data = struct.pack('>B10s', n, bytes(10))
            self.ct67_sent_cmd(aims, 0x02, bytes_data, 1)


    def ct67_yunwei_out_cmd(self, str_aims, str_n):
        if str_aims.isdigit() and str_n.isdigit():
            aims = int(str_aims)
            n = int(str_n)
            bytes_data = struct.pack('>BB10s', 0x00, n, bytes(10))  # 0子命令 运维出仓
            self.ct67_sent_cmd(aims, 0x04, bytes_data, 1)

    def ct67_force_out_cmd(self, str_aims, str_n):
        if str_aims.isdigit() and str_n.isdigit():
            aims = int(str_aims)
            n = int(str_n)
            bytes_data = struct.pack('>BB10s', 0x01, n, bytes(10))  # 1子命令 强制出仓
            self.ct67_sent_cmd(aims, 0x04, bytes_data, 1)


    def ct67_reset_device_cmd(self, str_aims):
        if str_aims.isdigit():
            aims = int(str_aims)
            bytes_data = struct.pack('>BB10s', 0x02, 0x00, bytes(10))  # 2子命令 重启设备
            self.ct67_sent_cmd(aims, 0x04, bytes_data, 1)




    def ct67_update_firmware_cmd(self, str_aims):

        if str_aims.isdigit() is False:
            error_dialog_run("机组号必须为数字")
            return

        # thread = ct67_FileDialog_thread(int(str_aims))
        # thread.start()

        self.my2_pyqt_form = ct67_update_firmware_tool_form(self, int(str_aims))
        self.my2_pyqt_form.show()




    def ct67_send_update_start(self, aims, file_size):

        bytes_data = struct.pack('>IHH16s', file_size, 0, 0, bytes(16))
        self.ct67_sent_cmd(aims, 0x05, bytes_data, 0)


    def ct67_send_update_data(self, aims, offset, file_data):
        len1 = len(file_data)
        aformat = f'>II{len1}s'.format(len1)
        bytes_data = struct.pack(aformat, offset, len1, file_data)
        self.ct67_sent_cmd(aims, 0x07, bytes_data, 0)


class ct67_FileDialog_thread(QThread):
    def __init__(self, aims):
        self.aims = aims
        super(ct67_FileDialog_thread, self).__init__()

    def run(self):
        file_dialog = ct67_FileDialog(self.aims)
        file_dialog.show()




class ct67_FileDialog(QDialog):
    def __init__(self, aims):
        super().__init__()

        self.initUI(aims)
        self.exec_loop = QEventLoop()

    def initUI(self, aims):

        
        
        self.aims = aims


        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle(f'乐畅-固件更新(升级第{self.aims}组)')

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

    # def selectFile(self):
    #     file_path, _ = QFileDialog.getOpenFileName(self, '选择更新固件', '', 'Binary files (*.bin)')
    #
    #     if file_path:
    #         self.file_path.setText(file_path)
    #
    # def sendFile(self):
    #     file_path = self.file_path.text()
    #
    #     if file_path:
    #         with open(file_path, 'rb') as file:
    #             file_content = file.read()
    #             total_bytes = len(file_content)
    #             bytes_sent = 0
    #
    #
    #             ct67_send_update_start(self.aims, total_bytes)
    #
    #             time.sleep(5)
    #
    #             ts = time.time()
    #
    #             while (bytes_sent < total_bytes) or ((ts - time.time()) > 5):
    #
    #                 time.sleep(1)
    #                 ts = time.time()
    #                 ct67_send_update_data(self.aims, bytes_sent, file_content[bytes_sent:bytes_sent + 1024])
    #                 # ct67_sent_cmd(self.aims, 0x03, file_content[bytes_sent:bytes_sent + 1000])
    #
    #                 bytes_sent += 1024 # Simulate sending 1000 bytes at a time
    #                 progress_value = int((bytes_sent / total_bytes) * 100)
    #                 self.progress.setValue(progress_value)
    #
    #                 if bytes_sent >= total_bytes:
    #                     QMessageBox.information(self, '更新成功', '哥们,文件发送成功了!')
