# PyQtWaveformWidget.py

from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
import os
import time
import threading

from waveform_work import WaveformOscilloscope  # 保留原有数据处理逻辑


class PyQtWaveformWidget(QtWidgets.QWidget):
    closed = None  # 在 init_ui 里定义信号

    def __init__(self, filename='lc_waveform.csv', default_points=100, parent=None):
        super(PyQtWaveformWidget, self).__init__(parent)

        self.filename = filename
        self.default_points = default_points
        self.closed = False

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 创建 matplotlib 的 canvas 控件
        self.fig = Figure(figsize=(14, 8))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], lw=2)

        layout.addWidget(self.canvas)

        # 添加导航工具栏（可选）
        toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(toolbar)

        # 初始化图形设置
        self.ax.set_title("Virtual Oscilloscope")
        self.ax.set_xlabel("Sample Index")
        self.ax.set_ylabel("Amplitude")

        # 初始化数据处理类
        self.osc = WaveformOscilloscope(filename=self.filename, default_points=self.default_points)
        self.osc.fig = self.fig
        self.osc.ax = self.ax
        self.osc.line = self.line
        self.osc.update_axis = self.update_axis  # 替换更新轴的方法

        # 动画定时器
        self.timer = self.fig.canvas.new_timer(interval=20)
        self.timer.add_callback(self.osc.update_plot, None)
        self.timer.start()

        # 关闭按钮
        self.close_button = QtWidgets.QPushButton("关闭波形")
        self.close_button.clicked.connect(self.close_requested)
        layout.addWidget(self.close_button)

        self.setLayout(layout)
        self.setWindowTitle("示波器窗口")

    def update_axis(self):
        x, y = self.osc.get_windowed_data()
        if x:
            try:
                self.ax.set_xlim(min(x), max(x))
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw_idle()
            except Exception as e:
                print(f"⚠️ set_xlim error: {e}")

    def close_requested(self):
        self.closed = True
        self.close()

    def closeEvent(self, event):
        """当窗口关闭时停止动画和线程"""
        print("📊 波形窗口已关闭")
        self.timer.stop()
        self.osc.file_monitor_thread.join(timeout=0.1)  # 安全退出线程
        event.accept()