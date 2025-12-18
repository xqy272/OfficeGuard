"""
卡片组件
简洁现代风格 - 参考 shadcn/ui
"""

import tkinter as tk
from ..theme import Theme


class Card(tk.Frame):
    """现代化卡片组件 - 简洁边框风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        title: str = None,
        description: str = None,
        padding: int = 24,
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        # 边框容器
        self.border = tk.Frame(self, bg=theme.border)
        self.border.pack(fill="both", expand=True)
        
        # 内容容器
        self.container = tk.Frame(self.border, bg=theme.card)
        self.container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # 内边距
        self.inner = tk.Frame(self.container, bg=theme.card)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)
        
        # 标题区域
        if title:
            header = tk.Frame(self.inner, bg=theme.card)
            header.pack(fill="x", pady=(0, 16))
            
            tk.Label(
                header,
                text=title,
                font=(theme.fonts.FAMILY, 14, "bold"),
                fg=theme.fg,
                bg=theme.card
            ).pack(anchor="w")
            
            if description:
                tk.Label(
                    header,
                    text=description,
                    font=(theme.fonts.FAMILY, 11),
                    fg=theme.muted,
                    bg=theme.card
                ).pack(anchor="w", pady=(4, 0))
        
        # 内容区域
        self.content = tk.Frame(self.inner, bg=theme.card)
        self.content.pack(fill="both", expand=True)
    
    def get_content_frame(self) -> tk.Frame:
        """获取内容区域 Frame"""
        return self.content


class SectionHeader(tk.Frame):
    """段落标题"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        title: str,
        description: str = None,
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        tk.Label(
            self,
            text=title,
            font=(theme.fonts.FAMILY, 14, "bold"),
            fg=theme.fg,
            bg=theme.bg
        ).pack(anchor="w")
        
        if description:
            tk.Label(
                self,
                text=description,
                font=(theme.fonts.FAMILY, 11),
                fg=theme.muted,
                bg=theme.bg
            ).pack(anchor="w", pady=(2, 0))


class Separator(tk.Frame):
    """分隔线"""
    
    def __init__(self, parent, theme: Theme, **kwargs):
        super().__init__(parent, bg=theme.border, height=1, **kwargs)


class Badge(tk.Frame):
    """标签徽章"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        text: str,
        variant: str = "default",
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        # 颜色映射
        color_map = {
            "default": (theme.bg3, theme.fg),
            "success": ("#dcfce7", "#166534"),
            "warning": ("#fef3c7", "#92400e"),
            "danger": ("#fee2e2", "#991b1b"),
            "info": ("#dbeafe", "#1e40af"),
        }
        
        bg_color, fg_color = color_map.get(variant, color_map["default"])
        
        # 标签
        self.label = tk.Label(
            self,
            text=text,
            font=("Segoe UI", 9),
            fg=fg_color,
            bg=bg_color,
            padx=8,
            pady=2
        )
        self.label.pack()


class Alert(tk.Frame):
    """提示框"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        title: str = None,
        message: str = "",
        variant: str = "info",
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        # 颜色映射
        color_map = {
            "info": (theme.colors.info, "#dbeafe"),
            "success": (theme.colors.success, "#dcfce7"),
            "warning": (theme.colors.warning, "#fef3c7"),
            "danger": (theme.colors.danger, "#fee2e2"),
        }
        
        accent_color, bg_color = color_map.get(variant, color_map["info"])
        
        # 左侧强调条
        accent = tk.Frame(self, bg=accent_color, width=4)
        accent.pack(side="left", fill="y")
        
        # 内容区域
        content = tk.Frame(self, bg=bg_color)
        content.pack(side="left", fill="both", expand=True)
        
        inner = tk.Frame(content, bg=bg_color)
        inner.pack(fill="both", expand=True, padx=16, pady=12)
        
        if title:
            tk.Label(
                inner,
                text=title,
                font=("Segoe UI Semibold", 10),
                fg=theme.fg,
                bg=bg_color
            ).pack(anchor="w")
        
        tk.Label(
            inner,
            text=message,
            font=("Segoe UI", 10),
            fg=theme.fg2,
            bg=bg_color,
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(4 if title else 0, 0))
