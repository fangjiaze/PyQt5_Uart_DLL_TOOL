import numpy as np
import os
import time
import threading
import csv

CSV_FILENAME = 'lc_waveform.csv'
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
DATA_INTERVAL_SECONDS = 0.1  # 100ms
STOP_EVENT = threading.Event()


def get_current_sine_value(t):
    """
    生成当前时间 t（单位：秒）对应的波形值：
    - 基础波：sin(t)
    - 每秒叠加一次高频波 sin(5t)
    """
    base = np.sin(t)
    if int(t) % 1 == 0:
        return base + np.sin(5 * t)
    else:
        return base


def create_or_clear_csv():
    """如果文件存在就清空，否则创建"""
    if os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, 'w', newline='') as f:
            pass  # 清空文件
    else:
        with open(CSV_FILENAME, 'w', newline='') as f:
            pass  # 创建空文件


def write_test_data_to_csv():
    """持续写入测试数据到 lc_waveform.csv"""
    print("📡 启动测试波形生成线程...")
    create_or_clear_csv()

    t = 0.0  # 时间计数器，以秒为单位
    while not STOP_EVENT.is_set():
        try:
            # 获取当前文件大小
            if os.path.exists(CSV_FILENAME) and os.path.getsize(CSV_FILENAME) >= MAX_FILE_SIZE_BYTES:
                print("⚠️ 文件已超过100MB，停止写入...")
                time.sleep(1)
                continue

            # 计算当前波形值
            value = get_current_sine_value(t)

            # 追加写入CSV
            with open(CSV_FILENAME, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([value])
                f.close()

            # 更新时间戳
            t += 0.1
            time.sleep(DATA_INTERVAL_SECONDS)

        except Exception as e:
            print(f"❌ 写入错误: {e}")
            time.sleep(1)

    # 程序退出前清空文件
    if os.path.exists(CSV_FILENAME):
        os.remove(CSV_FILENAME)
    print("🧹 测试数据文件已清除")


def start_test_data_thread():
    """启动测试数据生成线程"""
    test_thread = threading.Thread(target=write_test_data_to_csv, daemon=True)
    test_thread.start()
    return test_thread