import os
import json



class sys_fjson_cfg :
    def __init__(self) :
        self.sys_fjs_cfg_init()


    def sys_fjs_cfg_init(self) :
        # 检查文件是否存在
        if not os.path.isfile('sys.fjs'):
            # 如果文件不存在，创建它并写入初始化数据
            self.data = {
                "cmd_cfg": [
                    {"n": i, "data": "", "hex": 0, "enter": 0, "button": str(i)} for i in range(1, 16)
                ]
            }

            with open('sys.fjs', 'w') as f:
                json.dump(self.data, f, indent=4)
                f.close()
        else :
            # 打开sys.fjz文件并读取数据
            with open('sys.fjs', 'r') as f:
                data = f.read()
                f.close()

            # 解析数据
            self.data = json.loads(data)



    def sys_fjs_cfg_update(self):
        with open('sys.fjs', 'w') as f:
            json.dump(self.data, f, indent=4)
            f.close()