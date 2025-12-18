"""
进度条组件
简洁现代风格 - 参考 shadcn/ui
"""

import tkinter as tk
import math
from typing import Optional
from ..theme import Theme


class CircularProgress(tk.Canvas):
    """圆形进度条 - 简洁风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        size: int = 200,
        thickness: int = 8,
        value: float = 0,
        max_value: float = 100,
        show_text: bool = True,
        **kwargs
    ):
        bg_color = kwargs.pop('bg', theme.card)
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        
        self.theme = theme
        self._size = size
        self._thickness = thickness
        self._value = value
        self._max_value = max_value
        self._show_text = show_text
        self._text = ""
        self._subtext = ""
        self._bg_color = bg_color
        
        self._draw()
    
    def _draw(self):
        """绘制进度条"""
        self.delete("all")
        
        size = self._size
        thickness = self._thickness
        center = size // 2
        radius = (size - thickness) // 2 - 8
        
        # 计算进度
        progress = min(1.0, self._value / self._max_value) if self._max_value > 0 else 0
        
        # 绘制背景圆环
        self._draw_circle(center, center, radius, thickness, self.theme.bg3)
        
        # 绘制进度圆环
        if progress > 0:
            # 简洁的颜色方案
            color = self.theme.fg
            self._draw_arc_progress(center, center, radius, thickness, progress, color)
        
        # 绘制文字
        if self._show_text:
            if self._text:
                # 主文字 - 大号
                self.create_text(
                    center, center - 10,
                    text=self._text,
                    font=(self.theme.fonts.FAMILY, 36, "bold"),
                    fill=self.theme.fg
                )
            else:
                # 显示百分比
                percent = int(progress * 100)
                self.create_text(
                    center, center - 10,
                    text=f"{percent}%",
                    font=(self.theme.fonts.FAMILY, 32, "bold"),
                    fill=self.theme.fg
                )
            
            # 副文字
            if self._subtext:
                self.create_text(
                    center, center + 32,
                    text=self._subtext,
                    font=(self.theme.fonts.FAMILY, 12),
                    fill=self.theme.muted
                )
    
    def _draw_circle(self, cx, cy, radius, thickness, color):
        """绘制完整圆环"""
        self.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            outline=color,
            width=thickness
        )
    
    def _draw_arc_progress(self, cx, cy, radius, thickness, progress, color):
        """绘制进度弧线"""
        extent = progress * 360
        
        # 使用 create_arc
        self.create_arc(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            start=90,
            extent=-extent,
            outline=color,
            width=thickness,
            style="arc"
        )
    
    def set_value(self, value: float, text: str = None, subtext: str = None):
        """设置进度值"""
        self._value = value
        if text is not None:
            self._text = text
        if subtext is not None:
            self._subtext = subtext
        self._draw()
    
    def set_text(self, text: str, subtext: str = None):
        """设置显示文字"""
        self._text = text
        if subtext is not None:
            self._subtext = subtext
        self._draw()
    
    def configure_bg(self, bg: str):
        """配置背景色"""
        self._bg_color = bg
        self.configure(bg=bg)
        self._draw()


class LinearProgress(tk.Frame):
    """线性进度条 - 简洁风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        width: int = 300,
        height: int = 6,
        value: float = 0,
        max_value: float = 100,
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, **kwargs)
        
        self.theme = theme
        self._value = value
        self._max_value = max_value
        self._width = width
        self._height = height
        
        # 背景轨道
        self.track = tk.Frame(self, bg=theme.bg3, height=height)
        self.track.pack(fill="x")
        self.track.pack_propagate(False)
        
        # 进度条
        self.bar = tk.Frame(self.track, bg=theme.fg, height=height)
        self.bar.place(x=0, y=0, relheight=1)
        
        self._update()
    
    def _update(self):
        """更新进度显示"""
        progress = min(1.0, self._value / self._max_value) if self._max_value > 0 else 0
        self.bar.place(relwidth=progress)
    
    def set_value(self, value: float):
        """设置进度值"""
        self._value = value
        self._update()


class Spinner(tk.Canvas):
    """加载动画"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        size: int = 24,
        **kwargs
    ):
        bg_color = kwargs.pop('bg', theme.bg)
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        
        self.theme = theme
        self._size = size
        self._angle = 0
        self._running = False
        
        self._draw()
    
    def _draw(self):
        """绘制加载动画"""
        self.delete("all")
        
        center = self._size // 2
        radius = self._size // 2 - 3
        
        # 绘制弧线
        self.create_arc(
            3, 3,
            self._size - 3, self._size - 3,
            start=self._angle,
            extent=270,
            outline=self.theme.fg,
            width=2,
            style="arc"
        )
    
    def start(self):
        """开始动画"""
        self._running = True
        self._animate()
    
    def stop(self):
        """停止动画"""
        self._running = False
    
    def _animate(self):
        """动画循环"""
        if not self._running:
            return
        
        self._angle = (self._angle + 10) % 360
        self._draw()
        self.after(50, self._animate)
