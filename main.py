import tkinter as tk
import serial
import time
import threading
import serial.tools.list_ports
# import fjz_timer
import waveform_work
import test_csv_simulator



import sys
from PyQt5 import QtWidgets
from MyPyQT_Form import MyPyQT_Form
# from lc_uart_test_tool import Ui_Form
import ctypes as C

# from lc_pylib import crc_16




if __name__ == '__main__' :

    # dll = C.cdll.LoadLibrary('Project2.dll')
    # # 获取DLL中所有可被调用的函数
    # functions = [func for func in dll.__dict__.values() if isinstance(func, C.CDLL)]
    # # 打印所有可被调用的函数名称
    # for func in functions:
    #     print(func.__name__)
    # dll.HelloWorld()

    # 启动测试数据生成线程
    # test_thread = test_csv_simulator.start_test_data_thread()

    
    # osc = waveform_work.WaveformOscilloscope(default_points=100)
    # osc.load_data()
    # osc.start()

    app = QtWidgets.QApplication(sys.argv)
    my_pyqt_form = MyPyQT_Form()
    my_pyqt_form.show()

    # Ui_Form.setupUi()
    sys.exit(app.exec_())





