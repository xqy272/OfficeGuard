# -*- coding: utf-8 -*-
"""
系统锁定页面
简洁现代风格 - 参考 shadcn/ui
"""

import tkinter as tk
from typing import Callable
from ..theme import Theme
from ..components.base import ModernButton, ModernEntry
from ..components.card import Card, Alert
from ..components.scrollable import ScrollableFrame


class LockPage(tk.Frame):
    """系统锁定页面 - 简洁风格"""
    
    def __init__(self, parent, theme: Theme, **kwargs):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        # 回调
        self._on_lock: Callable[[str], None] = None
        
        self._create_ui()
    
    def set_callbacks(self, on_lock: Callable = None):
        """设置回调函数"""
        self._on_lock = on_lock
    
    def _create_ui(self):
        """创建界面"""
        # 主容器
        container = tk.Frame(self, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=32, pady=24)
        
        # 页面标题
        tk.Label(
            container,
            text="系统保护",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XL3, "bold"),
            fg=self.theme.fg,
            bg=self.theme.bg
        ).pack(anchor="w", pady=(0, 24))
        
        # 可滚动区域
        scroll = ScrollableFrame(container, self.theme)
        scroll.pack(fill="both", expand=True)
        
        content = scroll.get_frame()
        
        # 功能介绍卡片
        intro_card = Card(
            content, 
            self.theme,
            title="锁屏保护",
            description="使用密码保护您的系统，防止未经授权的访问"
        )
        intro_card.pack(fill="x", pady=(0, 16), padx=4)
        
        intro_content = intro_card.get_content_frame()
        
        # 功能列表
        features = [
            "• 自定义锁屏密码保护",
            "• 全屏覆盖防止绕过",
            "• 支持键盘快捷键解锁"
        ]
        
        for feat in features:
            tk.Label(
                intro_content,
                text=feat,
                font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
                fg=self.theme.muted,
                bg=self.theme.card
            ).pack(anchor="w", pady=2)
        
        # 警告提示
        Alert(
            content,
            self.theme,
            variant="warning",
            title="使用须知",
            message="请牢记您设置的密码，忘记密码需要重启计算机才能解除锁定。"
        ).pack(fill="x", pady=(0, 16), padx=4)
        
        # 操作卡片
        action_card = Card(content, self.theme, title="设置密码")
        action_card.pack(fill="x", padx=4)
        
        action_content = action_card.get_content_frame()
        
        # 密码输入
        password_frame = tk.Frame(action_content, bg=self.theme.card)
        password_frame.pack(fill="x", pady=(0, 16))
        
        tk.Label(
            password_frame,
            text="解锁密码",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg,
            bg=self.theme.card
        ).pack(anchor="w", pady=(0, 8))
        
        self.password_entry = ModernEntry(
            password_frame,
            self.theme,
            placeholder="输入密码（默认: 1234）",
            show="●"
        )
        self.password_entry.pack(fill="x")
        self.password_entry.insert(0, "1234")
        
        # 提示
        tk.Label(
            password_frame,
            text="输入正确密码后按回车即可解锁",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XS),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack(anchor="w", pady=(8, 0))
        
        # 锁定按钮
        self.lock_btn = ModernButton(
            action_content,
            self.theme,
            text="立即锁定系统",
            variant="primary",
            command=self._on_lock_click
        )
        self.lock_btn.pack(fill="x", pady=(8, 0))
    
    def _on_lock_click(self):
        """点击锁定按钮"""
        password = self.password_entry.get() or "1234"
        if self._on_lock:
            self._on_lock(password)
    
    def update_hotkey(self, hotkey: str):
        """更新热键显示（兼容接口）"""
        pass  # 当前版本不显示热键
