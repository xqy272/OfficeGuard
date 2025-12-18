# -*- coding: utf-8 -*-
"""
定时任务页面
简洁现代风格
"""

import tkinter as tk
from typing import Callable, Optional
from ..theme import Theme
from ..components.base import ModernButton, ModernEntry
from ..components.card import Card, SectionHeader, Separator
from ..components.progress import CircularProgress
from ..components.scrollable import ScrollableFrame


class TimerPage(tk.Frame):
    """定时任务页面"""
    
    def __init__(self, parent, theme: Theme, **kwargs):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        self._on_start_shutdown: Callable[[float, int], None] = None
        self._on_start_sleep: Callable[[float, int], None] = None
        self._on_cancel: Callable[[], None] = None
        self._is_running = False
        
        self._create_ui()
    
    def set_callbacks(
        self,
        on_start_shutdown: Callable = None,
        on_start_sleep: Callable = None,
        on_cancel: Callable = None
    ):
        """设置回调函数"""
        self._on_start_shutdown = on_start_shutdown
        self._on_start_sleep = on_start_sleep
        self._on_cancel = on_cancel
    
    def _create_ui(self):
        """创建界面"""
        container = tk.Frame(self, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=32, pady=24)
        
        # 页面标题
        header = tk.Frame(container, bg=self.theme.bg)
        header.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            header,
            text="定时任务",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XL3, "bold"),
            fg=self.theme.fg,
            bg=self.theme.bg
        ).pack(side="left")
        
        # 状态标签
        self.status_frame = tk.Frame(header, bg=self.theme.bg)
        self.status_frame.pack(side="right")
        
        self.status_dot = tk.Label(
            self.status_frame,
            text="●",
            font=(self.theme.fonts.FAMILY, 8),
            fg=self.theme.colors.success,
            bg=self.theme.bg
        )
        self.status_dot.pack(side="left", padx=(0, 4))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="准备就绪",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.muted,
            bg=self.theme.bg
        )
        self.status_label.pack(side="left")
        
        # 可滚动区域
        scroll = ScrollableFrame(container, self.theme)
        scroll.pack(fill="both", expand=True)
        
        scroll_content = scroll.get_frame()
        
        # 主内容区 - 两列布局
        content = tk.Frame(scroll_content, bg=self.theme.bg)
        content.pack(fill="both", expand=True, padx=4)
        
        # 左侧 - 进度显示
        left = tk.Frame(content, bg=self.theme.bg)
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))
        
        # 进度卡片
        progress_card = Card(left, self.theme, padding=24)
        progress_card.pack(fill="both", expand=True)
        
        progress_content = progress_card.get_content_frame()
        
        # 圆形进度
        self.progress = CircularProgress(
            progress_content,
            self.theme,
            size=160,
            thickness=6
        )
        self.progress.pack(expand=True, pady=16)
        
        # 剩余时间
        self.time_label = tk.Label(
            progress_content,
            text="--:--",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XL4, "bold"),
            fg=self.theme.fg,
            bg=self.theme.card
        )
        self.time_label.pack(pady=(0, 4))
        
        self.desc_label = tk.Label(
            progress_content,
            text="设置时间后点击开始",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.muted,
            bg=self.theme.card
        )
        self.desc_label.pack()
        
        # 右侧 - 设置面板
        right = tk.Frame(content, bg=self.theme.bg, width=320)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        
        # 时间设置卡片
        time_card = Card(right, self.theme)
        time_card.pack(fill="x", pady=(0, 12))
        
        time_content = time_card.get_content_frame()
        
        SectionHeader(time_content, self.theme, "时间设置").pack(fill="x", pady=(0, 12))
        
        # 定时时间
        time_row = tk.Frame(time_content, bg=self.theme.card)
        time_row.pack(fill="x", pady=(0, 8))
        
        tk.Label(
            time_row,
            text="定时时间",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg,
            bg=self.theme.card
        ).pack(side="left")
        
        time_input = tk.Frame(time_row, bg=self.theme.card)
        time_input.pack(side="right")
        
        self.time_entry = ModernEntry(
            time_input,
            self.theme,
            width=60,
            placeholder="60"
        )
        self.time_entry.pack(side="left")
        self.time_entry.insert(0, "60")
        
        tk.Label(
            time_input,
            text="分钟",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack(side="left", padx=(6, 0))
        
        # 宽限期
        grace_row = tk.Frame(time_content, bg=self.theme.card)
        grace_row.pack(fill="x")
        
        tk.Label(
            grace_row,
            text="宽限期",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg,
            bg=self.theme.card
        ).pack(side="left")
        
        grace_input = tk.Frame(grace_row, bg=self.theme.card)
        grace_input.pack(side="right")
        
        self.grace_entry = ModernEntry(
            grace_input,
            self.theme,
            width=60,
            placeholder="30"
        )
        self.grace_entry.pack(side="left")
        self.grace_entry.insert(0, "30")
        
        tk.Label(
            grace_input,
            text="秒",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack(side="left", padx=(6, 0))
        
        # 操作卡片
        action_card = Card(right, self.theme)
        action_card.pack(fill="x")
        
        action_content = action_card.get_content_frame()
        
        SectionHeader(action_content, self.theme, "执行操作").pack(fill="x", pady=(0, 12))
        
        # 关机按钮
        self.shutdown_btn = ModernButton(
            action_content,
            self.theme,
            text="定时关机",
            variant="primary",
            command=self._on_shutdown_click
        )
        self.shutdown_btn.pack(fill="x", pady=(0, 8))
        
        # 睡眠按钮
        self.sleep_btn = ModernButton(
            action_content,
            self.theme,
            text="定时睡眠",
            variant="outline",
            command=self._on_sleep_click
        )
        self.sleep_btn.pack(fill="x", pady=(0, 8))
        
        Separator(action_content, self.theme).pack(fill="x", pady=8)
        
        # 取消按钮
        self.cancel_btn = ModernButton(
            action_content,
            self.theme,
            text="取消任务",
            variant="destructive",
            command=self._on_cancel_click
        )
        self.cancel_btn.pack(fill="x")
        self.cancel_btn.configure(state="disabled")
    
    def _on_shutdown_click(self):
        """点击关机按钮"""
        if self._is_running:
            return
        
        try:
            minutes = float(self.time_entry.get() or "60")
            grace = int(self.grace_entry.get() or "30")
            
            if self._on_start_shutdown:
                self._on_start_shutdown(minutes, grace)
        except ValueError:
            pass
    
    def _on_sleep_click(self):
        """点击睡眠按钮"""
        if self._is_running:
            return
        
        try:
            minutes = float(self.time_entry.get() or "60")
            grace = int(self.grace_entry.get() or "30")
            
            if self._on_start_sleep:
                self._on_start_sleep(minutes, grace)
        except ValueError:
            pass
    
    def _on_cancel_click(self):
        """点击取消按钮"""
        if self._on_cancel:
            self._on_cancel()
    
    def update_state(self, is_running: bool, remaining: Optional[int] = None, task_type: str = ""):
        """更新状态"""
        self._is_running = is_running
        
        if is_running:
            self.shutdown_btn.configure(state="disabled")
            self.sleep_btn.configure(state="disabled")
            self.cancel_btn.configure(state="normal")
            
            self.status_dot.configure(fg=self.theme.colors.warning)
            self.status_label.configure(text=f"正在运行 - {task_type}")
            
            if remaining is not None:
                mins = remaining // 60
                secs = remaining % 60
                self.time_label.configure(text=f"{mins:02d}:{secs:02d}")
                self.desc_label.configure(text="剩余时间")
        else:
            self.shutdown_btn.configure(state="normal")
            self.sleep_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            
            self.status_dot.configure(fg=self.theme.colors.success)
            self.status_label.configure(text="准备就绪")
            
            self.time_label.configure(text="--:--")
            self.desc_label.configure(text="设置时间后点击开始")
            self.progress.set_progress(0)
    
    def update_progress(self, progress: float, remaining: int):
        """更新进度"""
        self.progress.set_progress(progress)
        
        mins = remaining // 60
        secs = remaining % 60
        self.time_label.configure(text=f"{mins:02d}:{secs:02d}")
