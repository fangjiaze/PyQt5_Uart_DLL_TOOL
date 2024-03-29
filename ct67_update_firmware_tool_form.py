import os

from PyQt5.QtCore import QThread, pyqtSignal

from User_ErrorDialog import error_dialog_run
from ct67_update_firmware_tool import Ui_update_Form
from PyQt5 import QtWidgets
import json
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog
import time
import threading


class ct67_update_firmware_tool_form(QtWidgets.QWidget, Ui_update_Form):

    progressBat_signal = pyqtSignal(object)  # 更新进度条信号,因为发送任务时在另一个线程,另一个线程通过发送信号的方式到窗体进行更新进度条。
    reversed_sentfile_pushbutton_signal = pyqtSignal(object)  # 发送结束时,需要改回发送按键的初始值,同时报更新成功

    def __init__(self, ui_obj, aims):
        super(ct67_update_firmware_tool_form, self).__init__()
        self.thread = None
        self.setupUi(self)
        self.ui_obj = ui_obj  # 为了提供串口发送接口给该线程
        self.aims = aims
        self.thread_running = False

        self.select_file_pushbutton.clicked.connect(self.select_file_callback)
        self.sent_file_pushbutton.clicked.connect(self.sent_file_callback)

        self.progressBat_signal.connect(self.set_progressBar_value_slot)
        self.reversed_sentfile_pushbutton_signal.connect(self.init_sentfile_pushbutton_slot)




    def select_file_callback(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择更新固件', '', 'Binary files (*.bin)')

        if file_path:
            self.path_lineedit.setText(file_path)

    def sent_file_callback(self):

        if not self.thread_running:
            self.thread_running = True
            self.sent_file_pushbutton.setText(("停止"))
            self.thread = threading.Thread(target=self.update_firmware_thread)
            # self.thread.daemon = True
            self.thread.start()
        else:
            self.thread_running = False
            if self.thread:
                self.thread.join()
            self.thread = None
            self.sent_file_pushbutton.setText(("发送固件"))
            self.progressBar.setValue(0)

    def update_firmware_thread(self):

        state = 0
        while self.thread_running:
            if state == 0:
                file_path = self.path_lineedit.text()
                if file_path:
                    try:
                        with open(file_path, 'rb') as file:
                            self.file_content = file.read()
                            file.close()
                            self.total_bytes = len(self.file_content)
                            self.bytes_sent_cnt = 0
                            self.ui_obj.ct67_send_update_start(self.aims, self.total_bytes)
                            time.sleep(1)
                            ts = time.time()
                            state = 1
                    except IOError:
                        state = 5  # 结束
                else:
                    state = 5  # 结束
            elif state == 1:
                if (self.bytes_sent_cnt < self.total_bytes) or ((ts - time.time()) > 5):
                    time.sleep(0.1)
                    ts = time.time()
                    if self.bytes_sent_cnt + 512 > self.total_bytes:
                        self.ui_obj.ct67_send_update_data(self.aims, self.bytes_sent_cnt, self.file_content[self.bytes_sent_cnt:])
                        self.bytes_sent_cnt = self.total_bytes
                    else:
                        self.ui_obj.ct67_send_update_data(self.aims, self.bytes_sent_cnt, self.file_content[self.bytes_sent_cnt: self.bytes_sent_cnt + 512])
                        self.bytes_sent_cnt += 512
                    progress_value = int((self.bytes_sent_cnt / self.total_bytes) * 100)
                    self.set_progressBar_value_signal(progress_value)

                    if self.bytes_sent_cnt >= self.total_bytes:

                        state = 2
            elif state == 2:
                self.thread_running = False
                self.reversed_sentfile_pushbutton_signal.emit('哥们,文件发送成功了!')



    def set_progressBar_value_slot(self, value):
        self.progressBar.setValue(value)


    def set_progressBar_value_signal(self, value):
        self.progressBat_signal.emit(value)

    def init_sentfile_pushbutton_slot(self, str_data):
        QMessageBox.information(self, '更新成功', str_data)
        self.sent_file_pushbutton.setText(("发送固件"))

# class update_firmware_thread(QThread):
#     finished_signal = pyqtSignal()  # 定义一个信号，用于通知主线程线程已经完成

#     def __init__(self, ui_obj):
#         super(update_firmware_thread, self).__init__()
#         self.bytes_sent_cnt = None
#         self.total_bytes = None
#         self.file_content = None
#         self.file_path = None
#         self.ui_obj = ui_obj


#     def run(self):

#         file_path = self.ui_obj.path_lineedit.text()
#         if file_path :


#             with open(file_path, 'rb') as file:


#                 self.file_content = file.read()
#                 self.total_bytes = len(self.file_content)
#                 self.bytes_sent_cnt = 0

#                 self.ui_obj.ui_obj.ct67_send_update_start(self.ui_obj.aims, self.total_bytes)

#                 time.sleep(1)

#                 ts = time.time()

#                 while (self.bytes_sent_cnt < self.total_bytes) or ((ts - time.time()) > 5):

#                     time.sleep(0.2)
#                     ts = time.time()
#                     if self.bytes_sent_cnt + 512 > self.total_bytes :
#                         self.ui_obj.ui_obj.ct67_send_update_data(self.ui_obj.aims, self.bytes_sent_cnt,self.file_content[self.bytes_sent_cnt: ])
#                         self.bytes_sent_cnt = self.total_bytes
#                     else :
#                         self.ui_obj.ui_obj.ct67_send_update_data(self.ui_obj.aims, self.bytes_sent_cnt, self.file_content[self.bytes_sent_cnt: self.bytes_sent_cnt + 512])
#                         self.bytes_sent_cnt += 512

#                     # self.bytes_sent_cnt += 1024
#                     progress_value = int((self.bytes_sent_cnt / self.total_bytes) * 100)
#                     self.ui_obj.progressBar.setValue(progress_value)

#                     if self.bytes_sent_cnt >= self.total_bytes:
#                         # time.sleep(1)
#                         QMessageBox.information(self.ui_obj, '更新成功', '哥们,文件发送成功了!')
#                         break

#                 file.close()
