import tkinter as tk
import serial
import time
import threading
import serial.tools.list_ports
import fjz_timer
import ctypes as C

import sys
from PyQt5 import QtWidgets
from lc_uart_test_tool import Ui_Form
from User_ErrorDialog import error_dialog_run

from PyQt5.QtWidgets import QMessageBox

com_config_parity_dict = {
    'None' : 'N',
    'Even' : 'E',
    'Odd' : 'O'
}

def update_com() :
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print(f"Port: {port}, Description: {desc}, HWID: {hwid}")
    port_list = [port.device for port in ports]
    return port_list


class MyPyQT_Form(QtWidgets.QWidget,Ui_Form):
    port_state = False
    com_port_list = []
    fjz_timer_obj = None
    serial = None
    receive_thread = None
    def __init__(self):
        super(MyPyQT_Form,self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.button_click)
        self.fjz_timer_obj = fjz_timer.fjz_timer(1000, self.update_com_list, -1)
        self.fjz_timer_obj.start()
        self.comboBox_2.addItems(['115200', '9600', '4800'])
        self.comboBox_3.addItems(['1', '1.5', '2'])
        self.comboBox_4.addItems(['None', 'Even', 'Odd'])
        self.comboBox_5.addItems(['8', '7', '6', '5'])

        self.pushButton_clear_log.clicked.connect(self.clear_log)
        self.pushButton_sent_data.clicked.connect(self.send_data)
        self.pushButton_select_dll.clicked.connect(self.select_dll)
        self.pushButton_open_dll.clicked.connect(self.open_dll_pro)


        # self.serial = None
        # self.receive_thread = None

    def closeEvent(self, event): # 关闭窗口处理

        reply = QtWidgets.QMessageBox.question(self,
                                               '关闭提示',
                                               "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            # 关闭更新com定时器线程
            print("stop com update timer")
            self.fjz_timer_obj.stop()
            self.port_state = False
            self.close_com()
        else:
            event.ignore()

    # def __del__(self):
    #     print("stop com update timer")
    #     self.fjz_timer_obj.stop()


    def button_click(self): # 端口打开或关闭按键触发函数
        if self.port_state :
            self.port_state = False
            self.pushButton.setText("open port")
            self.close_com()
            print("button click !!! close port")
            self.comboBox.setEnabled(True)
            self.comboBox_2.setEnabled(True)
            self.comboBox_3.setEnabled(True)
            self.comboBox_4.setEnabled(True)
            self.comboBox_5.setEnabled(True)

        else:
            self.port_state = True
            self.pushButton.setText("close port")
            if self.open_com() is False :
                self.port_state = False
                self.pushButton.setText("open port")
            else :
                print("button click!!! open port")
                # self.comboBox.setEditable(False)
                self.comboBox.setEnabled(False)
                self.comboBox_2.setEnabled(False)
                self.comboBox_3.setEnabled(False)
                self.comboBox_4.setEnabled(False)
                self.comboBox_5.setEnabled(False)



    def update_com_list(self): # 更新串口端口定时器函数
        if self.port_state is False:
            list = update_com()
            if list != self.com_port_list :
                self.com_port_list = list
                self.comboBox.clear()
                self.comboBox.addItems(list)

    def open_com(self): # 打开串口
        port = self.comboBox.currentText()
        baud_rate = int(self.comboBox_2.currentText())
        stop_bits = int(self.comboBox_3.currentText())
        parity = com_config_parity_dict[self.comboBox_4.currentText()]
        data_bits = int(self.comboBox_5.currentText())
        try:
            self.serial = serial.Serial(port, baud_rate, stopbits=stop_bits, parity=parity,
                                        bytesize=data_bits, timeout=0.01)
            if self.serial.is_open :
                print(self.serial)
        except serial.SerialException:
            print("Failed to open COM port.")
            error_dialog_run("打开串口失败！！！")
            return False

        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()
        return True

    def close_com(self): # 关闭串口
        if self.serial and self.serial.is_open:
            self.serial.close()

        if self.receive_thread:
            self.receive_thread.join()

    def receive_data(self): # 接收处理
        while self.port_state:
            try:
                num = self.serial.inWaiting()
                if num > 0:
                    data = self.serial.read(num)
                    num = len(data)

                    if self.checkBox_showtime.isChecked():
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        self.TextEdit_log.insertPlainText("[" + timestamp + ",len:" + str(num) + "]")
                    else :
                        self.TextEdit_log.insertPlainText("[" + "rec len:" + str(num) + "]")

                    if self.checkBox_showhex.isChecked():
                        out_s = ''
                        for i in range(0, len(data)):
                            out_s = out_s + '{:02X}'.format(data[i]) + ' '
                        self.TextEdit_log.insertPlainText(out_s)
                    else :
                        # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                        self.TextEdit_log.insertPlainText(data.decode('utf-8'))

                    # 滚动到文本末尾
                    if self.checkBox_log_lock.isChecked() is False :
                        scroll_bar = self.TextEdit_log.verticalScrollBar()
                        scroll_bar.setValue(scroll_bar.maximum())
            except serial.SerialException:
                break

    def send_data(self): # 发送数据
        if self.serial and self.port_state :
            input_s = self.textEdit.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.checkBox_sent_hex.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    if self.checkBox_sentwith_rn.isChecked() :
                        input_s = (input_s + '\r\n').encode('utf-8')
                    else :
                        input_s = (input_s).encode('utf-8')

                num = self.serial.write(input_s)
                # self.data_num_sended += num
        else:
            pass



    def clear_log(self): # 清除日志
        self.TextEdit_log.clear()

    def select_dll(self):
        file_dialog = QtWidgets.QFileDialog.getOpenFileName(self, "Select DLL File", "", "Dynamic Link Libraries (*.dll)")
        dll_path = file_dialog[0]
        if dll_path:
            self.lineEdit_dll.setText(dll_path)

    def open_dll_pro(self):
        if self.pushButton_open_dll.text() == "启动dll" :
            self.pushButton_open_dll.setText(("关闭dll"))
            self.lineEdit_dll.setEnabled(False)

            dll = C.cdll.LoadLibrary(self.lineEdit_dll.text())
            dll.HelloWorld()

        else :
            self.pushButton_open_dll.setText(("启动dll"))
            self.lineEdit_dll.setEnabled(True)