"""
开关组件
简洁现代风格 - 参考 shadcn/ui
"""

import tkinter as tk
from typing import Callable, Optional
from ..theme import Theme


class Switch(tk.Canvas):
    """现代化切换开关 - 简洁风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        value: bool = False,
        command: Callable[[bool], None] = None,
        width: int = 40,
        height: int = 22,
        **kwargs
    ):
        bg_color = kwargs.pop('bg', theme.bg)
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        
        self.theme = theme
        self._value = value
        self._command = command
        self._width = width
        self._height = height
        self._bg_color = bg_color
        
        # 颜色
        self._on_color = theme.fg
        self._off_color = theme.colors.border
        self._knob_color = "#ffffff"
        
        # 绘制
        self._draw()
        
        # 绑定事件
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
    
    def _draw(self):
        """绘制开关"""
        self.delete("all")
        
        w, h = self._width, self._height
        r = h // 2
        
        # 背景色
        bg_color = self._on_color if self._value else self._off_color
        
        # 绘制圆角矩形背景
        self.create_arc(0, 0, h, h, start=90, extent=180, fill=bg_color, outline=bg_color)
        self.create_arc(w - h, 0, w, h, start=270, extent=180, fill=bg_color, outline=bg_color)
        self.create_rectangle(r, 0, w - r, h, fill=bg_color, outline=bg_color)
        
        # 绘制圆形滑块
        knob_r = (h - 6) // 2
        if self._value:
            knob_x = w - r
        else:
            knob_x = r
        
        self.create_oval(
            knob_x - knob_r,
            3,
            knob_x + knob_r,
            h - 3,
            fill=self._knob_color,
            outline=self._knob_color
        )
    
    def _on_click(self, event):
        """点击切换"""
        self._value = not self._value
        self._draw()
        
        if self._command:
            self._command(self._value)
    
    def get(self) -> bool:
        """获取当前值"""
        return self._value
    
    def set(self, value: bool):
        """设置值"""
        if self._value != value:
            self._value = value
            self._draw()


class LabeledSwitch(tk.Frame):
    """带标签的开关 - 简洁风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        text: str,
        description: str = None,
        value: bool = False,
        command: Callable[[bool], None] = None,
        **kwargs
    ):
        super().__init__(parent, bg=theme.card, **kwargs)
        
        self.theme = theme
        self._command = command
        
        # 左侧文字
        text_frame = tk.Frame(self, bg=theme.card)
        text_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            text_frame,
            text=text,
            font=(theme.fonts.FAMILY, 13),
            fg=theme.fg,
            bg=theme.card
        ).pack(anchor="w")
        
        if description:
            tk.Label(
                text_frame,
                text=description,
                font=(theme.fonts.FAMILY, 11),
                fg=theme.muted,
                bg=theme.card
            ).pack(anchor="w", pady=(2, 0))
        
        # 右侧开关
        self.switch = Switch(
            self,
            theme,
            value=value,
            command=self._on_change,
            bg=theme.card
        )
        self.switch.pack(side="right", pady=4)
    
    def _on_change(self, value: bool):
        """开关状态改变"""
        if self._command:
            self._command(value)
    
    def get(self) -> bool:
        """获取当前值"""
        return self.switch.get()
    
    def set(self, value: bool):
        """设置值"""
        self.switch.set(value)
