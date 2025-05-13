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
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal

class PyQtWaveformWidget(QtWidgets.QWidget):
    closed = pyqtSignal()  # 自定义关闭信号
    
    def __init__(self, filename='lc_waveform.csv', default_points=100, parent=None):
        super(PyQtWaveformWidget, self).__init__(parent)

        self.filename = filename
        self.default_points = default_points
        # self.closed = False
        # self.closed = pyqtSignal()  # 自定义关闭信号
        self.data = []
        self.index = 0
        self.points = default_points
        self.dragging = False
        self.last_pos = None
        self.lock = threading.Lock()
        self._last_move_time = 0  # 添加节流时间戳

        # 使用 QTimer 替代 FuncAnimation
        # self.refresh_timer = QTimer(self)
        # self.refresh_timer.timeout.connect(lambda: self.update_plot(None))
        # self.refresh_timer.start(20)  # 每 20ms 刷新一次

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


        # 绑定事件
        self.cid_scroll = self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        # 右键右键自动跟随
        self.auto_follow = True
        self.cid_right_click = self.fig.canvas.mpl_connect('button_press_event', self.on_right_click)
        # 绑定十字线
        self.cid_hover = self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_hover)

        # 初始化数据处理类
        # self.osc = WaveformOscilloscope(filename=self.filename, default_points=self.default_points)
        # self.osc.fig = self.fig
        # self.osc.ax = self.ax
        # self.osc.line = self.line
        # self.osc.update_axis = self.update_axis  # 替换更新轴的方法

        # 动画定时器
        self.timer = self.fig.canvas.new_timer(interval=20)
        self.timer.add_callback(self.update_plot, None)
        self.timer.start()

        # 关闭按钮
        self.close_button = QtWidgets.QPushButton("关闭波形")
        self.close_button.clicked.connect(self.close_requested)
        layout.addWidget(self.close_button)

        self.setLayout(layout)
        self.setWindowTitle("示波器窗口")

        # 启动后台线程监听文件变化
        self.file_monitor_thread = threading.Thread(target=self.monitor_file, daemon=True)
        self.file_monitor_thread.start()

    def load_data(self):
        """从CSV文件中加载数据，增加对空白/未完成文件的保护"""
        try:
            if not os.path.exists(self.filename):
                print(f"⚠️ 文件 {self.filename} 不存在")
                return

            file_size = os.path.getsize(self.filename)
            if file_size == 0:
                print("⏳ 文件存在但为空，跳过本次加载")
                return

            data = np.loadtxt(self.filename, delimiter=',')

            if data.ndim == 1:
                loaded_data = data.tolist()
            else:
                loaded_data = data[:, 0].tolist()

            with self.lock:
                self.data = loaded_data

        except Exception as e:
            print(f"⚠️ 加载文件时出错: {e}")
            # 出错时不更新数据，保留原有 self.data 内容

    def get_windowed_data(self):
        """
        获取当前显示窗口内的数据（x 轴索引与 y 轴数值）

        返回值：
            (x, y): 当前窗口的 x 和 y 数据列表
        """
        with self.lock:
            # 如果数据为空，返回空列表以避免异常
            if not self.data:
                return [], []

            # 计算当前窗口结束索引：index + points 不能超过数据总长度
            end_idx = min(self.index + self.points, len(self.data))

            # 生成 x 轴索引（从 index 到 end_idx）
            x = list(range(self.index, end_idx))

            # 提取 y 轴对应的数据段
            y = self.data[self.index:end_idx]

            # 安全检查：确保 x 和 y 都有数据且长度一致
            if not x or not y or len(x) != len(y):
                return [], []

        # 返回当前窗口的 x 和 y 数据
        return x, y

    def update_axis(self):
        """更新坐标轴范围，避免非法值"""
        x, y = self.get_windowed_data()
        if x:
            try:
                self.ax.set_xlim(min(x), max(x))
            except Exception as e:
                print(f"⚠️ set_xlim error: {e}")
        # x, y = self.osc.get_windowed_data()
        # if x:
        #     try:
        #         self.ax.set_xlim(min(x), max(x))
        #         self.ax.relim()
        #         self.ax.autoscale_view()
        #         self.canvas.draw_idle()
        #     except Exception as e:
        #         print(f"⚠️ set_xlim error: {e}")

    def close_requested(self):
        # self.closed = True
        self.close()

    def closeEvent(self, event):
        """当窗口关闭时停止动画和线程"""
        print("📊 波形窗口已关闭")
        self.timer.stop()
        try:
            self.file_monitor_thread.join(timeout=0.1)
        except:
            pass
        self.closed.emit()   # 发送关闭信号
        event.accept()  # ✅ 添加此行以确保窗口真正关闭并触发 destroyed 信号

    def update_plot(self, frame):
        try:
            x, y = self.get_windowed_data()
            if x and y and len(x) == len(y):
                self.line.set_data(x, y)
                self.ax.relim()
                self.ax.autoscale_view()
                self.fig.canvas.draw_idle()
            return self.line, self.ax
        except Exception as e:
            print(f"⚠️ 动画刷新异常: {e}")
            return self.line, self.ax
    
    def on_scroll(self, event):
        """滚轮控制点数个数，以鼠标位置为中心缩放，并限制最大显示点数"""
        SENSITIVITY = 1.5       # 缩放灵敏度
        MAX_POINTS = 160000      # 最大允许的点数（防止无限放大）

        try:
            with self.lock:
                total_data_len = len(self.data)
            if total_data_len == 0:
                return

            canvas_width = self.ax.get_window_extent().width
            if canvas_width <= 0:
                return

            mouse_pos_ratio = (event.x - self.ax.bbox.x0) / canvas_width
            mouse_pos_ratio = max(0.0, min(1.0, mouse_pos_ratio))

            delta = -1 if event.step > 0 else 1  # 上滑缩小，下滑放大
            old_points = self.points

            # 根据滚轮方向计算新点数，并限制最大值为数据总长度或 MAX_POINTS
            new_points = int(old_points + delta * old_points / SENSITIVITY)
            new_points = max(10, min(new_points, total_data_len, MAX_POINTS))

            with self.lock:
                if total_data_len == 0:
                    return

                mouse_data_index = int(self.index + mouse_pos_ratio * old_points)
                new_index = int(mouse_data_index - mouse_pos_ratio * new_points)

                # 边界保护
                new_index = max(0, min(new_index, total_data_len - new_points))
                self.index = new_index
                self.points = new_points

            print(f"Zoom to {new_points} points at index {self.index}")
            self.update_axis()

        except Exception as e:
            print(f"⚠️ 滚轮缩放时发生异常: {e}")


    def on_mouse_hover(self, event):
        """
        鼠标悬停事件：只在有效数据范围内显示十字线和值
        """
        if event.inaxes != self.ax:
            self.clear_hover_indicator()
            return

        try:
            # 获取当前绘图区域的 xdata（可能为 None）
            xdata = int(event.xdata)
            if xdata is None or not (0 <= xdata < len(self.data)):
                self.clear_hover_indicator()
                return

            with self.lock:
                # 确保数据存在且 xdata 在合法范围内
                if not self.data or xdata >= len(self.data):
                    self.clear_hover_indicator()
                    return

                # 安全获取 ydata
                ydata = self.data[xdata]

            # 绘制十字线和文本提示
            self.clear_hover_indicator()

            self.hover_vline = self.ax.axvline(x=xdata, color='red', linestyle='--', lw=1)
            self.hover_hline = self.ax.axhline(y=ydata, color='red', linestyle='--', lw=1)

            self.hover_text = self.ax.text(
                xdata,
                ydata,
                f"x={xdata}, y={ydata:.4f}",
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", alpha=0.8)
            )

            self.fig.canvas.draw_idle()

        except Exception as e:
            self.clear_hover_indicator()
            print(f"⚠️ 悬停显示异常: {e}")
    def clear_hover_indicator(self):
        """清除悬停指示器"""
        if hasattr(self, 'hover_vline'):
            self.hover_vline.remove()
            del self.hover_vline
        if hasattr(self, 'hover_hline'):
            self.hover_hline.remove()
            del self.hover_hline
        if hasattr(self, 'hover_text'):
            self.hover_text.remove()
            del self.hover_text

    def on_right_click(self, event):
        """鼠标右键单击切换自动追尾模式"""
        if event.button == 3:  # 鼠标右键
            with self.lock:
                # total_data_len = len(self.data)
            # if self.auto_follow:
            #     print("⏸️ 手动退出自动追尾模式")
            #     self.auto_follow = False
            # else:
                print("🚀 启用自动追尾模式")
                self.auto_follow = True
                # self.index = max(0, total_data_len - self.points)
                # self.update_axis()
                # self.fig.canvas.draw_idle()  # 强制刷新画面

    def on_mouse_press(self, event):
        """鼠标左键按下触发拖动"""
        if event.button == 1:
            self.dragging = True
            self.start_mouse_x = event.x
            with self.lock:
                self.start_index = self.index

    def on_mouse_release(self, event):
        """释放鼠标停止拖动"""
        self.dragging = False
        self.last_pos = None

    def on_mouse_move(self, event):
        """鼠标移动拖动索引，支持连续平滑拖动"""
        if self.dragging and event.x is not None and hasattr(self, 'start_mouse_x'):

            # ✅ 安全判断
            if not (hasattr(event, 'x') and self.ax.bbox and self.ax.get_window_extent().width > 0):
                return

            canvas_width = self.ax.get_window_extent().width
            if canvas_width <= 0:
                return

            try:
                with self.lock:
                    total_data_len = len(self.data)
                    if total_data_len == 0 or total_data_len < self.points:
                        return
                    if self.index + self.points < total_data_len :
                        self.auto_follow = False
                        print("追尾关闭")

                dx_pixels = event.x - self.start_mouse_x

                print(f"dx_pixels={dx_pixels}, points={self.points}, data_len={total_data_len}")

                # 🔽 添加防抖动逻辑
                if abs(dx_pixels) < 3:
                    return

                pixels_per_point = canvas_width / self.points
                dx_points = int(dx_pixels / pixels_per_point)

                # ✅ 公式：新索引 = 上次的数据起点 - dx_points
                new_index = max(0, self.start_index - dx_points)
                new_index = min(new_index, total_data_len - self.points)

                self.index = new_index

                # ✅ 更新 start_mouse_x 和 start_index，实现连续拖动
                self.start_mouse_x = event.x
                self.start_index = self.index  # 新增：重置起点为当前索引

                print(f"Moved index to {self.index}")
                print(f"data_len={total_data_len}, points={self.points}, dx_pixels={dx_pixels}, dx_points={dx_points}")

                self.update_axis()

            except Exception as e:
                print(f"⚠️ 鼠标移动处理异常: {e}")
    
    def monitor_file(self):
        last_size = 0
        while True:
            try:
                if not os.path.exists(self.filename):
                    time.sleep(0.5)
                    continue

                current_size = os.path.getsize(self.filename)

                # 只有当文件增大且有效时才重新加载数据
                if current_size > 0 and current_size != last_size:

                    self.load_data()  # 加载最新数据

                    # with self.lock:
                    total_data_len = len(self.data)

                    # ✅ 设置最小点数限制
                    # MIN_POINTS = 20
                    # if total_data_len < MIN_POINTS:
                    #     print(f"⏳ 数据不足{MIN_POINTS}点，暂不更新索引")
                    #     return

                    # 如果处于追尾模式 or 当前窗口已接近末尾，则跳转到最后
                    if self.auto_follow :
                        prev_index = self.index
                        new_index = max(0, total_data_len - self.points)
                        if new_index != prev_index:
                            self.index = new_index
                            print(f"🚀 自动追尾跳转到最后: index={self.index}, points={self.points} data_len={total_data_len}")
                            self.update_axis()
                                # self.fig.canvas.draw_idle()  # 强制刷新画面

                last_size = current_size

            except Exception as e:
                print(f"⚠️ 文件监听发生错误: {e}")

            time.sleep(0.02)