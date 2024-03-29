import ctypes
import queue
import tkinter as tk
import serial
import time
import threading
import serial.tools.list_ports
import fjz_timer
import ctypes as C


import lc_pylib
import sys_f_json_cfg

import sys
from PyQt5 import QtWidgets
from lc_uart_test_tool import Ui_Form
from cp05_protocol_tool_form import cp05_protocol_tool_form
from User_ErrorDialog import error_dialog_run

from PyQt5.QtWidgets import QMessageBox

com_config_parity_dict = {
    'None' : 'N',
    'Even' : 'E',
    'Odd' : 'O'
}

class dll_param_class(C.Structure) :
    _fields_ = [
        ("ack_data", C.c_byte * 20),
        ("ack_len", C.c_uint16),
        ("ack_data_hex_flag", C.c_uint16),
        ("out_data", C.c_byte * 1024),
        ("out_len", C.c_uint16),
        ("out_data_hex_flag", C.c_uint16),
        ("log_print_data", C.c_byte * 512)]

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
    # serial = None
    # receive_thread = None
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


        self.pushButton_cmd_sent.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit, self.checkBox_cmd_hex_flag, self.checkBox_cmd_enter_flag))
        self.pushButton_cmd_sent_2.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_2, self.checkBox_cmd_hex_flag_2, self.checkBox_cmd_enter_flag_2))
        self.pushButton_cmd_sent_3.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_3, self.checkBox_cmd_hex_flag_3, self.checkBox_cmd_enter_flag_3))
        self.pushButton_cmd_sent_4.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_4, self.checkBox_cmd_hex_flag_4, self.checkBox_cmd_enter_flag_4))
        self.pushButton_cmd_sent_5.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_5, self.checkBox_cmd_hex_flag_5, self.checkBox_cmd_enter_flag_5))
        self.pushButton_cmd_sent_6.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_6, self.checkBox_cmd_hex_flag_6, self.checkBox_cmd_enter_flag_6))
        self.pushButton_cmd_sent_7.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_7, self.checkBox_cmd_hex_flag_7, self.checkBox_cmd_enter_flag_7))
        self.pushButton_cmd_sent_8.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_8, self.checkBox_cmd_hex_flag_8, self.checkBox_cmd_enter_flag_8))
        self.pushButton_cmd_sent_9.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_9, self.checkBox_cmd_hex_flag_9, self.checkBox_cmd_enter_flag_9))
        self.pushButton_cmd_sent_10.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_10, self.checkBox_cmd_hex_flag_10, self.checkBox_cmd_enter_flag_10))
        self.pushButton_cmd_sent_11.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_11, self.checkBox_cmd_hex_flag_11, self.checkBox_cmd_enter_flag_11))
        self.pushButton_cmd_sent_12.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_12, self.checkBox_cmd_hex_flag_12, self.checkBox_cmd_enter_flag_12))
        self.pushButton_cmd_sent_13.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_13, self.checkBox_cmd_hex_flag_13, self.checkBox_cmd_enter_flag_13))
        self.pushButton_cmd_sent_14.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_14, self.checkBox_cmd_hex_flag_14, self.checkBox_cmd_enter_flag_14))
        self.pushButton_cmd_sent_15.clicked.connect(lambda: self.sent_uart_cmd(self.cmd_edit_15, self.checkBox_cmd_hex_flag_15, self.checkBox_cmd_enter_flag_15))




        self.sys_fjs_cfg_open_init()


        self.serial = None
        self.receive_thread = None
        self.dll_thread = None
        self.dll = None
        self.my2_pyqt_form = None

        self.refer_uart_data = b''

        self.uart_queue = queue.Queue()

        import CT67_protocol_module

        self.my2_pyqt_form = cp05_protocol_tool_form(self, CT67_protocol_module)
        self.my2_pyqt_form.show()



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
            self.sys_fjs_cfg_close_pro()
            if self.my2_pyqt_form is not None :
                self.my2_pyqt_form.close()
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
                                        bytesize=data_bits, timeout=1, write_timeout=0.5)
            if self.serial.is_open :
                print(self.serial)
        except serial.SerialException:
            print("Failed to open COM port.")
            error_dialog_run("打开串口失败！！！")
            return False

        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        return True

    def close_com(self): # 关闭串口
        if self.serial and self.serial.is_open:
            self.serial.close()

        if self.receive_thread:
            self.receive_thread.join()


    def receive_data(self): # 接收处理
        num = 0
        while self.port_state:
            time.sleep(0.01)
            try:
                bytes_data = self.uart_queue.get_nowait()
                if bytes_data :
                    self.serial.write(bytes_data)
            except :
                pass

            try:

                temp_num = self.serial.inWaiting()
                if temp_num == 0 :
                    continue

                if num != temp_num :
                    num = temp_num
                    # time.sleep(0.01)
                else :
                    data = self.serial.read(num)
                    num = len(data)
                    self.TextEdit_log.moveCursor(self.TextEdit_log.textCursor().End) # 光标置末尾。
                    if self.checkBox_showtime.isChecked():
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        # self.TextEdit_log.insertPlainText("[" + timestamp + ",len:" + str(num) + "]")
                        self.TextEdit_log.insertPlainText(f"<{timestamp} , len:{num}>".format(timestamp, num))
                    else :
                        # self.TextEdit_log.insertPlainText("[" + "rec len:" + str(num) + "]")
                        self.TextEdit_log.insertPlainText(f"< rec len: { num }>".format(num))

                    if self.checkBox_showhex.isChecked():
                        out_s = ''
                        for i in range(0, len(data)):
                            out_s = out_s + '{:02X}'.format(data[i]) + ' '
                        out_s += '\r\n'
                        self.TextEdit_log.insertPlainText(out_s)
                    else :
                        # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去

                        self.TextEdit_log.insertPlainText(data.decode('utf-8') + '\r\n')
                        #self.TextEdit_log.append(data.decode('utf-8'))



                    self.dll_refer_rec_uart_data(data, num)


                    # 滚动到文本末尾
                    if self.checkBox_log_lock.isChecked() is False :
                        scroll_bar = self.TextEdit_log.verticalScrollBar()
                        scroll_bar.setValue(scroll_bar.maximum())
            except serial.SerialException:
                break
            except UnicodeDecodeError :
                pass


            

    def send_uart_put_data(self, bytes_data):
        self.uart_queue.put(bytes_data)

    def send_uart_data(self, hex_print_flag, bytes_data):
        if self.serial and self.port_state :
            try:
                if hex_print_flag != 2 :
                    self.TextEdit_log.moveCursor(self.TextEdit_log.textCursor().End) # 光标置末尾。
                    if self.checkBox_showtime.isChecked():
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                        self.TextEdit_log.insertPlainText(f"[{timestamp} ,send len:{len(bytes_data)}]".format(timestamp, len(bytes_data)))
                    else :
                        self.TextEdit_log.insertPlainText(f"[ send len: {len(bytes_data)}]".format(len(bytes_data)))
                    if hex_print_flag:
                        # hex打印
                        self.TextEdit_log.insertPlainText(lc_pylib.lc_hex_print(bytes_data) + '\r\n')
                    else:
                        # ascii打印
                        self.TextEdit_log.insertPlainText(bytes_data.decode('utf-8') + '\r\n')
            # self.serial.write(bytes_data)
            # self.serial.flush()
                self.send_uart_put_data(bytes_data)
            except Exception as e:
                print("发生异常：" + e)


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
                try :
                    # num = self.serial.write(input_s)
                    self.send_uart_put_data(input_s)
                except :
                    pass
                # self.data_num_sended += num
        else:
            pass

    def sent_uart_cmd(self, textedit, checkbox_hex, checkbox_rn) :
        if self.serial and self.port_state :
            input_s = textedit.text()
            if input_s != "":
                # 非空字符串
                if checkbox_hex.isChecked():
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
                    if checkbox_rn.isChecked() :
                        input_s = (input_s + '\r\n').encode('utf-8')
                    else :
                        input_s = (input_s).encode('utf-8')
                try :
                    # num = self.serial.write(input_s)
                    self.send_uart_put_data(input_s)
                except :
                    pass
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

            # self.dll_thread = threading.Thread(target=self.dll_thread_pro)
            # self.dll_thread.start()
            self.dll_thread_pro()
            self.refer_uart_data = b''

            # self.my2_pyqt_form = cp05_protocol_tool_form()
            # self.my2_pyqt_form.show()

        else :
            self.dll = None
            self.pushButton_open_dll.setText(("启动dll"))
            self.lineEdit_dll.setEnabled(True)
            self.refer_uart_data = b''

            self.my2_pyqt_form.close()
            self.my2_pyqt_form = None
            # self.my2_pyqt_form.close()

            # self.free_dll_work_and_data()

    def dll_thread_pro(self):
        reset_flag = 0

        try :
            self.dll = C.cdll.LoadLibrary(self.lineEdit_dll.text())
        except :
            pass
        if self.dll :
            print(self.dll)
            try :
                self.dll.dll_refer_data.argtypes = [C.c_char_p, C.c_uint32, C.c_void_p]
                self.dll.dll_refer_data.restype = C.c_int32

                # out_str = C.create_string_buffer(1024, '\0')
                # out_len = ctypes.c_int(0)
                # result = self.dll.dll_refer_data(out_str, 100, out_str, ctypes.addressof(out_len))
                #
                # print(f"result.value:{result}")
                # print(f"out_str : {out_str.value}")
                # print(f"out_len : {out_len.value}")
            except :
                reset_flag = 1
        else :
            reset_flag = 1


        if reset_flag :
            self.dll = None
            QMessageBox.critical(self, 'wrong data', '该dll文件不合规或没选择文件')
            self.pushButton_open_dll.setText(("启动dll"))
            self.lineEdit_dll.setEnabled(True)

        # print("传入空字符串指针，返回字符串demo:")
        # print(in_str.value)
        # print(out_str)
        # self.dll.main()
        # print("dll main work over")



    def dll_refer_rec_uart_data(self, data, data_len) :

        if self.dll is None :
            return

        self.refer_uart_data += data #将字节数据解码成py字符串数据
        c_str_data = C.string_at(self.refer_uart_data, len(self.refer_uart_data))#将py字符串数据转换成ctype类型的字符串
        param = dll_param_class() # 创建结构体对象
        param.ack_data_hex_flag = 2 # 初始化2 ，默认未置位
        param.out_data_hex_flag = 2 # 初始化2 ，默认未置位
        readed_len = self.dll.dll_refer_data(c_str_data, C.c_uint32(data_len), C.addressof(param)) #执行dll函数




        try :
            ack_data_p = C.cast(param.ack_data, C.POINTER(C.c_byte)) #获取ctype的数组的指针
            ack_data_string = C.string_at(ack_data_p, param.ack_len) #指针转换成py字符串
            # str = lc_pylib.remove_null_character(ack_data_string.decode())
            # sdata = ack_data_string.decode()
            if(param.ack_data_hex_flag == 1) :
                sdata = ''.join(lc_pylib.lc_hex_print(ack_data_string))
                self.TextEdit_log.insertPlainText("[ sent ack ]" + sdata + "\r\n")
            elif param.ack_data_hex_flag == 0:
                sdata = ack_data_string.decode()
                print(sdata)
                self.TextEdit_log.insertPlainText("[ sent ack ]" + sdata + "\r\n")
            else :
                pass
            if param.ack_data_hex_flag != 2 :
                # self.serial.write(ack_data_string)
                self.send_uart_put_data(ack_data_string)
        except :
            print("error 1")
            pass

        try :
            log_print_data_p = C.cast(param.log_print_data, C.POINTER(C.c_byte))  # 获取ctype的数组的指针
            log_print_data_string = C.string_at(log_print_data_p, 512) #指针转换成py字符串
            sdata = lc_pylib.remove_null_character(log_print_data_string.decode())
            if sdata != '' :
                print(sdata)
                self.TextEdit_log.insertPlainText("\r\n[dll refer]" + sdata + "\r\n")
        except :
            print("error 2")
            pass

        try :
            out_data_p = C.cast(param.out_data, C.POINTER(C.c_byte)) #获取ctype的数组的指针
            out_data_string = C.string_at(out_data_p, param.out_len)  # 指针转换成py字符串
            # sdata = out_data_string.decode()
            if (param.out_data_hex_flag == 1):
                sdata = ''.join(lc_pylib.lc_hex_print(out_data_string))
                self.TextEdit_log.insertPlainText("[ sent response ]" + sdata + "\r\n")
            elif param.out_data_hex_flag == 0:
                sdata = out_data_string.decode()
                print(sdata)
                self.TextEdit_log.insertPlainText("[ sent response ]" + sdata + "\r\n")
            else :
                pass
            if param.out_data_hex_flag != 2:
                # self.serial.write(out_data_string)
                self.send_uart_put_data(out_data_string)
        except :
            print("error 3")
            pass


        if readed_len <= len(self.refer_uart_data) :
            self.refer_uart_data = self.refer_uart_data[readed_len : ]
        else :
            self.refer_uart_data = b''


    def sys_fjs_cfg_open_init(self):

        self.sys_js_config = sys_f_json_cfg.sys_fjson_cfg()

        if self.sys_js_config.data["cmd_cfg"][0]["hex"] == 1:
            self.checkBox_cmd_hex_flag.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][1]["hex"] == 1:
            self.checkBox_cmd_hex_flag_2.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][2]["hex"] == 1:
            self.checkBox_cmd_hex_flag_3.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][3]["hex"] == 1:
            self.checkBox_cmd_hex_flag_4.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][4]["hex"] == 1:
            self.checkBox_cmd_hex_flag_5.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][5]["hex"] == 1:
            self.checkBox_cmd_hex_flag_6.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][6]["hex"] == 1:
            self.checkBox_cmd_hex_flag_7.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][7]["hex"] == 1:
            self.checkBox_cmd_hex_flag_8.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][8]["hex"] == 1:
            self.checkBox_cmd_hex_flag_9.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][9]["hex"] == 1:
            self.checkBox_cmd_hex_flag_10.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][10]["hex"] == 1:
            self.checkBox_cmd_hex_flag_11.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][11]["hex"] == 1:
            self.checkBox_cmd_hex_flag_12.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][12]["hex"] == 1:
            self.checkBox_cmd_hex_flag_13.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][13]["hex"] == 1:
            self.checkBox_cmd_hex_flag_14.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][14]["hex"] == 1:
            self.checkBox_cmd_hex_flag_15.setChecked(True)


        if self.sys_js_config.data["cmd_cfg"][0]["enter"] == 1:
            self.checkBox_cmd_enter_flag.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][1]["enter"] == 1:
            self.checkBox_cmd_enter_flag_2.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][2]["enter"] == 1:
            self.checkBox_cmd_enter_flag_3.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][3]["enter"] == 1:
            self.checkBox_cmd_enter_flag_4.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][4]["enter"] == 1:
            self.checkBox_cmd_enter_flag_5.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][5]["enter"] == 1:
            self.checkBox_cmd_enter_flag_6.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][6]["enter"] == 1:
            self.checkBox_cmd_enter_flag_7.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][7]["enter"] == 1:
            self.checkBox_cmd_enter_flag_8.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][8]["enter"] == 1:
            self.checkBox_cmd_enter_flag_9.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][9]["enter"] == 1:
            self.checkBox_cmd_enter_flag_10.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][10]["enter"] == 1:
            self.checkBox_cmd_enter_flag_11.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][11]["enter"] == 1:
            self.checkBox_cmd_enter_flag_12.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][12]["enter"] == 1:
            self.checkBox_cmd_enter_flag_13.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][13]["enter"] == 1:
            self.checkBox_cmd_enter_flag_14.setChecked(True)
        if self.sys_js_config.data["cmd_cfg"][14]["enter"] == 1:
            self.checkBox_cmd_enter_flag_15.setChecked(True)


        self.cmd_edit.setText(self.sys_js_config.data["cmd_cfg"][0]["data"])
        self.cmd_edit_2.setText(self.sys_js_config.data["cmd_cfg"][1]["data"])
        self.cmd_edit_3.setText(self.sys_js_config.data["cmd_cfg"][2]["data"])
        self.cmd_edit_4.setText(self.sys_js_config.data["cmd_cfg"][3]["data"])
        self.cmd_edit_5.setText(self.sys_js_config.data["cmd_cfg"][4]["data"])
        self.cmd_edit_6.setText(self.sys_js_config.data["cmd_cfg"][5]["data"])
        self.cmd_edit_7.setText(self.sys_js_config.data["cmd_cfg"][6]["data"])
        self.cmd_edit_8.setText(self.sys_js_config.data["cmd_cfg"][7]["data"])
        self.cmd_edit_9.setText(self.sys_js_config.data["cmd_cfg"][8]["data"])
        self.cmd_edit_10.setText(self.sys_js_config.data["cmd_cfg"][9]["data"])
        self.cmd_edit_11.setText(self.sys_js_config.data["cmd_cfg"][10]["data"])
        self.cmd_edit_12.setText(self.sys_js_config.data["cmd_cfg"][11]["data"])
        self.cmd_edit_13.setText(self.sys_js_config.data["cmd_cfg"][12]["data"])
        self.cmd_edit_14.setText(self.sys_js_config.data["cmd_cfg"][13]["data"])
        self.cmd_edit_15.setText(self.sys_js_config.data["cmd_cfg"][14]["data"])



        
    def sys_fjs_cfg_close_pro(self):

        self.sys_js_config.data["cmd_cfg"][0]["hex"] = 1 if self.checkBox_cmd_hex_flag.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][1]["hex"] = 1 if self.checkBox_cmd_hex_flag_2.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][2]["hex"] = 1 if self.checkBox_cmd_hex_flag_3.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][3]["hex"] = 1 if self.checkBox_cmd_hex_flag_4.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][4]["hex"] = 1 if self.checkBox_cmd_hex_flag_5.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][5]["hex"] = 1 if self.checkBox_cmd_hex_flag_6.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][6]["hex"] = 1 if self.checkBox_cmd_hex_flag_7.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][7]["hex"] = 1 if self.checkBox_cmd_hex_flag_8.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][8]["hex"] = 1 if self.checkBox_cmd_hex_flag_9.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][9]["hex"] = 1 if self.checkBox_cmd_hex_flag_10.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][10]["hex"] = 1 if self.checkBox_cmd_hex_flag_11.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][11]["hex"] = 1 if self.checkBox_cmd_hex_flag_12.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][12]["hex"] = 1 if self.checkBox_cmd_hex_flag_13.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][13]["hex"] = 1 if self.checkBox_cmd_hex_flag_14.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][14]["hex"] = 1 if self.checkBox_cmd_hex_flag_15.isChecked() else 0


        self.sys_js_config.data["cmd_cfg"][0]["enter"] = 1 if self.checkBox_cmd_enter_flag.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][1]["enter"] = 1 if self.checkBox_cmd_enter_flag_2.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][2]["enter"] = 1 if self.checkBox_cmd_enter_flag_3.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][3]["enter"] = 1 if self.checkBox_cmd_enter_flag_4.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][4]["enter"] = 1 if self.checkBox_cmd_enter_flag_5.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][5]["enter"] = 1 if self.checkBox_cmd_enter_flag_6.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][6]["enter"] = 1 if self.checkBox_cmd_enter_flag_7.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][7]["enter"] = 1 if self.checkBox_cmd_enter_flag_8.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][8]["enter"] = 1 if self.checkBox_cmd_enter_flag_9.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][9]["enter"] = 1 if self.checkBox_cmd_enter_flag_10.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][10]["enter"] = 1 if self.checkBox_cmd_enter_flag_11.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][11]["enter"] = 1 if self.checkBox_cmd_enter_flag_12.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][12]["enter"] = 1 if self.checkBox_cmd_enter_flag_13.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][13]["enter"] = 1 if self.checkBox_cmd_enter_flag_14.isChecked() else 0
        self.sys_js_config.data["cmd_cfg"][14]["enter"] = 1 if self.checkBox_cmd_enter_flag_15.isChecked() else 0


        self.sys_js_config.data["cmd_cfg"][0]["data"] = self.cmd_edit.text()
        self.sys_js_config.data["cmd_cfg"][1]["data"] = self.cmd_edit_2.text()
        self.sys_js_config.data["cmd_cfg"][2]["data"] = self.cmd_edit_3.text()
        self.sys_js_config.data["cmd_cfg"][3]["data"] = self.cmd_edit_4.text()
        self.sys_js_config.data["cmd_cfg"][4]["data"] = self.cmd_edit_5.text()
        self.sys_js_config.data["cmd_cfg"][5]["data"] = self.cmd_edit_6.text()
        self.sys_js_config.data["cmd_cfg"][6]["data"] = self.cmd_edit_7.text()
        self.sys_js_config.data["cmd_cfg"][7]["data"] = self.cmd_edit_8.text()
        self.sys_js_config.data["cmd_cfg"][8]["data"] = self.cmd_edit_9.text()
        self.sys_js_config.data["cmd_cfg"][9]["data"] = self.cmd_edit_10.text()
        self.sys_js_config.data["cmd_cfg"][10]["data"] = self.cmd_edit_11.text()
        self.sys_js_config.data["cmd_cfg"][11]["data"] = self.cmd_edit_12.text()
        self.sys_js_config.data["cmd_cfg"][12]["data"] = self.cmd_edit_13.text()
        self.sys_js_config.data["cmd_cfg"][13]["data"] = self.cmd_edit_14.text()
        self.sys_js_config.data["cmd_cfg"][14]["data"] = self.cmd_edit_15.text()


        self.sys_js_config.sys_fjs_cfg_update()








