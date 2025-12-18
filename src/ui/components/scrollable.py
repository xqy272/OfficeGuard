# -*- coding: utf-8 -*-
"""
可滚动容器组件
"""

import tkinter as tk
from ..theme import Theme


class ScrollableFrame(tk.Frame):
    """可滚动的Frame容器"""
    
    def __init__(self, parent, theme: Theme, **kwargs):
        super().__init__(parent, bg=theme.bg, **kwargs)
        
        self.theme = theme
        
        # 创建Canvas
        self.canvas = tk.Canvas(self, bg=theme.bg, highlightthickness=0)
        
        # 创建滚动条（仅在需要时显示）
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # 创建内部Frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=theme.bg)
        
        # 配置Canvas
        self.scrollable_frame.bind(
            "<Configure>",
            self._on_frame_configure
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self._on_scroll)
        
        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        # 滚动条初始隐藏
        
        # 绑定鼠标滚轮
        self.bind_mousewheel()
        
        # 绑定宽度变化
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _on_frame_configure(self, event):
        """内容Frame尺寸变化"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar()
    
    def _on_canvas_configure(self, event):
        """Canvas尺寸变化时调整内部Frame宽度"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        self._update_scrollbar()
    
    def _on_scroll(self, first, last):
        """滚动回调"""
        self.scrollbar.set(first, last)
        self._update_scrollbar()
    
    def _update_scrollbar(self):
        """根据内容是否超出显示区域来显示/隐藏滚动条"""
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()
    
    def bind_mousewheel(self):
        """绑定鼠标滚轮"""
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
    
    def _bind_mousewheel(self, event):
        """鼠标进入时绑定滚轮"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_mousewheel(self, event):
        """鼠标离开时解绑滚轮"""
        self.canvas.unbind_all("<MouseWheel>")
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        # 只有当内容超出时才滚动
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def get_frame(self):
        """获取可滚动的内部Frame"""
        return self.scrollable_frame
    
    def scroll_to_top(self):
        """滚动到顶部"""
        self.canvas.yview_moveto(0)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        self.canvas.yview_moveto(1)
