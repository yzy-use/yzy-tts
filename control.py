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

    # 点击实践
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

    # 生成 HTML 的按钮事件
    def btnClickHtml(self,evt):
        def start_async():
            def update_button_state(state):
                self.ui.tk_button_generateHtmlBtn.config(state=state)  # 更新按钮状态
            self.app.after(0,update_button_state(tkinter.DISABLED))

            # 在子线程中运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.generateAllHtml())

            self.app.after(0, update_button_state(tkinter.NORMAL))

        # 在子线程中运行异步任务
        Thread(target=start_async, daemon=True).start()

    # 拆分章节并生成语音
    async def generateAll(self):
        content = self.ui.tk_text_content.get("1.0", "end")
        path = os.getcwd() + '\\media\\'
        voice = self.ui.tk_select_box_voicebox.get()

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.delete("1.0","end"))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"开始生成语音\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))
        # 替换特殊符号
        content = textUtils.replace_symbols_with_space(content)
        # 拆分文本
        chapters = textUtils.split_text_by_chapters(content)
        # 合并
        merged_sections = textUtils.merge_chapters_with_limit(chapters)

        for chunk in merged_sections:
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
            self.app.after(0, self.ui.tk_text_log.insert("end", f"【{chunk['name']}】\n"))
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

            start_time = time.time()
            # 核心
            # 创建文件夹（如果不存在）
            os.makedirs(os.path.dirname(path), exist_ok=True)
            await ttsUtils.generateMp3(chunk['content'], voice, path + chunk['name'] + '.mp3')
            end_time = time.time()  # 记录结束时间
            elapsed_time = end_time - start_time

            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
            self.app.after(0, self.ui.tk_text_log.insert("end", f"\n【{chunk['name']}】 (字符数: {len(chunk['content'])}) （运行时常：{elapsed_time:.4f}） 成功\n"))
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"全部完成\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

    # 批量导出 HTML
    async def generateAllHtml(self):
        content = self.ui.tk_text_content.get("1.0", "end")
        base_path = os.getcwd() + '\\media\\'

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.delete("1.0","end"))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"开始生成HTML\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

        # 替换特殊符号
        content = textUtils.replace_symbols_with_space(content)
        # 拆分文本
        chapters = textUtils.split_text_by_chapters(content)
        # 合并为 HTML 内容
        merged_sections = textUtils.merge_chapters_with_limit_html(chapters)

        # 创建文件夹（如果不存在）
        os.makedirs(os.path.dirname(base_path), exist_ok=True)

        for chunk in merged_sections:
            name = chunk['name']
            html = chunk['content']
            file_path = base_path + name + '.html'

            start_time = time.time()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            end_time = time.time()
            elapsed_time = end_time - start_time

            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
            self.app.after(0, self.ui.tk_text_log.insert("end", f"\n【{name}】（运行时常：{elapsed_time:.4f}） 成功\n"))
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"全部完成\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

    # 合并 HTML 的按钮事件
    def btnClickMergeHtml(self, evt):
        def start_async():
            def update_button_state(state):
                self.ui.tk_button_mergeHtmlBtn.config(state=state)  # 更新按钮状态
            self.app.after(0, update_button_state(tkinter.DISABLED))

            # 在子线程中运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.generateMergedHtml())

            self.app.after(0, update_button_state(tkinter.NORMAL))

        # 在子线程中运行异步任务
        Thread(target=start_async, daemon=True).start()

    # 生成合并的 HTML 文件
    async def generateMergedHtml(self):
        content = self.ui.tk_text_content.get("1.0", "end")
        base_path = os.getcwd() + '\\media\\'

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.delete("1.0", "end"))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"开始生成合并HTML\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

        # 替换特殊符号
        content = textUtils.replace_symbols_with_space(content)
        # 拆分文本
        chapters = textUtils.split_text_by_chapters(content)
        
        # 创建文件夹（如果不存在）
        os.makedirs(os.path.dirname(base_path), exist_ok=True)

        start_time = time.time()
        # 生成合并的 HTML
        merged_html = textUtils.create_merged_html_with_pagination(chapters)
        file_path = base_path + '完整小说.html'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(merged_html)
        end_time = time.time()
        elapsed_time = end_time - start_time

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"合并HTML生成完成（运行时常：{elapsed_time:.4f}）\n"))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"文件保存至：{file_path}\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

    async def generateAllTxt(self):
        content = self.ui.tk_text_content.get("1.0", "end")
        base_path = os.getcwd() + '\\media\\'

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.delete("1.0","end"))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"开始生成HTML\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

        # 替换特殊符号
        content = textUtils.replace_symbols_with_space(content)
        # 拆分文本
        chapters = textUtils.split_text_by_chapters(content)
        # 合并为 HTML 内容
        merged_sections = textUtils.merge_chapters_with_limit(chapters)

        # 创建文件夹（如果不存在）
        os.makedirs(os.path.dirname(base_path), exist_ok=True)

        for chunk in merged_sections:
            name = chunk['name']
            html = chunk['content']
            file_path = base_path + name + '.txt'

            start_time = time.time()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            end_time = time.time()
            elapsed_time = end_time - start_time

            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
            self.app.after(0, self.ui.tk_text_log.insert("end", f"\n【{name}】（运行时常：{elapsed_time:.4f}） 成功\n"))
            self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.NORMAL))
        self.app.after(0, self.ui.tk_text_log.insert("end", f"全部完成\n"))
        self.app.after(0, self.ui.tk_text_log.config(state=tkinter.DISABLED))

    # 初始化声音下拉框
    async def comboboxInit(self):
        voices = await ttsUtils.getVoices()
        self.ui.tk_select_box_voicebox['values'] = voices
        self.ui.tk_select_box_voicebox.set('zh-CN-YunxiNeural')