"""
本代码由[Tkinter布局助手]生成
官网:https://www.pytk.net
QQ交流群:905019785
在线反馈:https://support.qq.com/product/618914
"""
import random
from tkinter import *
from tkinter.ttk import *

from control import Controller


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_text_content = self.__tk_text_content(self)
        self.tk_button_generateBtn = self.__tk_button_generateBtn(self)
        self.tk_button_generateHtmlBtn = self.__tk_button_generateHtmlBtn(self)
        self.tk_text_log = self.__tk_text_log(self)
        self.tk_select_box_voicebox = self.__tk_select_box_voicebox(self)
    def __win(self):
        self.title("yzy-tts")
        # 设置窗口大小、居中
        width = 1230
        height = 720
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self,vbar, hbar, widget):
        """自动隐藏滚动条"""
        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)
        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)
        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self,vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')
    def h_scrollbar(self,hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')
    def create_bar(self,master, widget,is_vbar,is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)
    def __tk_text_content(self,parent):
        text = Text(parent)
        text.place(x=10, y=10, width=900, height=700)
        self.create_bar(parent, text,True, False, 10, 10, 900,700,1230,720)
        return text
    def __tk_button_generateBtn(self,parent):
        btn = Button(parent, text="按钮", takefocus=False,)
        btn.place(x=1100, y=670, width=120, height=40)
        return btn
    def __tk_button_generateHtmlBtn(self,parent):
        btn = Button(parent, text="生成HTML", takefocus=False,)
        btn.place(x=970, y=670, width=120, height=40)
        return btn
    def __tk_text_log(self,parent):
        text = Text(parent)
        text.place(x=920, y=50, width=300, height=500)
        self.create_bar(parent, text,True, False, 920, 10, 300,500,1230,720)
        return text
    def __tk_select_box_voicebox(self, parent):
        cb = Combobox(parent, state="readonly", )
        cb['values'] = ("列表框", "Python", "Tkinter Helper")
        cb.place(x=920, y=10, width=300, height=30)
        return cb
class Win(WinGUI):
    def __init__(self):
        self.ctl = Controller(self)
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)
    def __event_bind(self):
        self.tk_button_generateBtn.bind('<Button-1>',self.ctl.btnClick)
        self.tk_button_generateHtmlBtn.bind('<Button-1>',self.ctl.btnClickHtml)
        pass
    def __style_config(self):
        pass
if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()