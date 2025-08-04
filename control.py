"""
本代码由[Tkinter布局助手]生成
官网:https://www.pytk.net
QQ交流群:905019785
在线反馈:https://support.qq.com/product/618914
"""
import os
import time
import tkinter
from threading import Thread
import asyncio
from utils import ttsUtils, textUtils

class Controller:
    # 导入UI类后，替换以下的 object 类型，将获得 IDE 属性提示功能
    ui: object
    def __init__(self,app):
        self.app = app

    def init(self, ui):
        """
        得到UI实例，对组件进行初始化配置
        """
        self.ui = ui
        # 组件初始化 赋值操作
        self.ui.tk_text_log.config(state=tkinter.DISABLED)

        def start_async():
            # 在子线程中运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.comboboxInit())
        # 在子线程中运行异步任务
        Thread(target=start_async, daemon=True).start()

    def btnClick(self,evt):
        def start_async():
            def update_button_state(state):
                self.ui.tk_button_generateBtn.config(state=state)  # 更新按钮状态
            self.app.after(0,update_button_state(tkinter.DISABLED))

            # 在子线程中运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.generateAll())

            self.app.after(0, update_button_state(tkinter.NORMAL))

        # 在子线程中运行异步任务
        Thread(target=start_async, daemon=True).start()

    async def generateAll(self):
        content = self.ui.tk_text_content.get("1.0", "end")
        # voice = "zh-CN-YunxiNeural"
        path = os.getcwd() + '\\media\\'
        voice = self.ui.tk_select_box_voicebox.get()

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.delete("1.0","end"))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"开始生成语音\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))
        # 替换一些符号
        content = textUtils.replace_symbols_with_space(content)
        # 拆分文本
        chapters = textUtils.split_text_by_chapters(content)
        # 合并
        merged_sections = textUtils.merge_chapters_with_limit(chapters)

        for chunk in merged_sections:
            chunk['name'] = textUtils.convert_chinese_number(chunk['name'])
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
            self.app.after(0, self.ui.tk_text_log.insert("end", f"【{chunk['name']}】\n"))
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

            start_time = time.time()
            # 核心
            await ttsUtils.generateMp3(chunk['content'], voice, path + chunk['name'] + '.mp3')
            end_time = time.time()  # 记录结束时间
            elapsed_time = end_time - start_time

            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
            self.app.after(0, self.ui.tk_text_log.insert("end", f"\n【{chunk['name']}】 (字符数: {len(chunk['content'])}) （运行时常：{elapsed_time:.4f}） 成功\n"))
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"全部完成\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

    async def comboboxInit(self):
        voices = await ttsUtils.getVoices()
        self.ui.tk_select_box_voicebox['values'] = voices
        self.ui.tk_select_box_voicebox.set('zh-CN-YunxiNeural')