# -*- coding: utf-8 -*-
"""
关于页面
简洁现代风格 - 参考 shadcn/ui
"""

import tkinter as tk
from ..theme import Theme
from ..components.card import Card, SectionHeader
from ..components.scrollable import ScrollableFrame
from ...core.version import VERSION, BUILD_DATE


class AboutPage(tk.Frame):
    """关于页面 - 简洁风格"""
    
    def __init__(self, parent, theme: Theme, **kwargs):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        self._create_ui()
    
    def _create_ui(self):
        """创建界面"""
        # 主容器
        container = tk.Frame(self, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=32, pady=24)
        
        # 页面标题
        tk.Label(
            container,
            text="关于",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XL3, "bold"),
            fg=self.theme.fg,
            bg=self.theme.bg
        ).pack(anchor="w", pady=(0, 24))
        
        # 可滚动区域
        scroll = ScrollableFrame(container, self.theme)
        scroll.pack(fill="both", expand=True)
        
        content = scroll.get_frame()
        
        # 应用信息卡片
        info_card = Card(content, self.theme)
        info_card.pack(fill="x", pady=(0, 16), padx=4)
        
        info_content = info_card.get_content_frame()
        
        # Logo 区域
        logo_frame = tk.Frame(info_content, bg=self.theme.card)
        logo_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            logo_frame,
            text="🛡",
            font=(self.theme.fonts.FAMILY, 40),
            bg=self.theme.card
        ).pack()
        
        tk.Label(
            logo_frame,
            text="OfficeGuard",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XL2, "bold"),
            fg=self.theme.fg,
            bg=self.theme.card
        ).pack(pady=(8, 4))
        
        tk.Label(
            logo_frame,
            text="系统优化助手",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack()
        
        # 版本信息
        version_frame = tk.Frame(info_content, bg=self.theme.card)
        version_frame.pack(fill="x")
        
        version_info = [
            ("版本号", VERSION),
            ("发布日期", BUILD_DATE),
            ("运行环境", "Windows 10/11"),
        ]
        
        for label, value in version_info:
            row = tk.Frame(version_frame, bg=self.theme.card)
            row.pack(fill="x", pady=4)
            
            tk.Label(
                row,
                text=label,
                font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
                fg=self.theme.muted,
                bg=self.theme.card
            ).pack(side="left")
            
            tk.Label(
                row,
                text=value,
                font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
                fg=self.theme.fg,
                bg=self.theme.card
            ).pack(side="right")
        
        # 功能介绍卡片
        feature_card = Card(content, self.theme)
        feature_card.pack(fill="x", pady=(0, 16), padx=4)
        
        feature_content = feature_card.get_content_frame()
        
        SectionHeader(
            feature_content,
            self.theme,
            "功能特点",
            "OfficeGuard 提供的核心功能"
        ).pack(fill="x", pady=(0, 16))
        
        features = [
            ("⏱️", "定时任务", "支持定时关机和睡眠功能"),
            ("🔒", "系统保护", "密码锁屏防止未授权访问"),
            ("⚙️", "系统优化", "自动管理开机启动项和系统设置"),
        ]
        
        for icon, title, desc in features:
            feat_row = tk.Frame(feature_content, bg=self.theme.card)
            feat_row.pack(fill="x", pady=6)
            
            tk.Label(
                feat_row,
                text=icon,
                font=(self.theme.fonts.FAMILY, 18),
                bg=self.theme.card
            ).pack(side="left", padx=(0, 12))
            
            text_frame = tk.Frame(feat_row, bg=self.theme.card)
            text_frame.pack(side="left", fill="x", expand=True)
            
            tk.Label(
                text_frame,
                text=title,
                font=(self.theme.fonts.FAMILY, self.theme.fonts.SM, "bold"),
                fg=self.theme.fg,
                bg=self.theme.card
            ).pack(anchor="w")
            
            tk.Label(
                text_frame,
                text=desc,
                font=(self.theme.fonts.FAMILY, self.theme.fonts.XS),
                fg=self.theme.muted,
                bg=self.theme.card
            ).pack(anchor="w")
        
        # 版权信息
        copyright_card = Card(content, self.theme)
        copyright_card.pack(fill="x", padx=4)
        
        copyright_content = copyright_card.get_content_frame()
        
        tk.Label(
            copyright_content,
            text="© 2025 QingYang. All rights reserved.",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XS),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack()
        
        tk.Label(
            copyright_content,
            text="本软件仅供个人学习和使用",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XS),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack(pady=(4, 0))
