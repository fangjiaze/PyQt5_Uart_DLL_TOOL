import threading
import time

class fjz_timer:
    def __init__(self, interval, callback, repeat=1):
        self.interval = interval / 1000.0  # 转换为秒
        self.callback = callback
        self.repeat = repeat
        self.counter = 0
        self.timer = None

    def _run(self):
        self.callback()
        self.counter += 1

        if self.repeat > 0 and self.counter >= self.repeat:
            self.stop()
        else:
            self.timer = threading.Timer(self.interval, self._run)
            self.timer.start()

    def start(self):
        self.counter = 0
        self.timer = threading.Timer(self.interval, self._run)
        self.timer.start()

    def stop(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

# 示例使用
# def print_message():
#     print("Timer callback function called")
#
# # 创建定时器对象，每500ms执行一次，总共执行5次
# timer = fjz_timer(500, print_message, 5)
#
# # 启动定时器
# timer.start()
#
# # 休眠一段时间，模拟其他操作
# time.sleep(3)
#
# # 停止定时器
# timer.stop()
