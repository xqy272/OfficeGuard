# -*- coding: utf-8 -*-
"""
设置页面
简洁现代风格 - 参考 shadcn/ui
包含：快捷键设置、自动登录、启动软件管理
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, List, Dict
from ..theme import Theme
from ..components.base import ModernButton, ModernEntry, ModernCheckbox
from ..components.card import Card, SectionHeader, Separator
from ..components.switch import LabeledSwitch
from ..components.scrollable import ScrollableFrame


class SettingsPage(tk.Frame):
    """设置页面 - 简洁风格"""
    
    def __init__(self, parent, theme: Theme, **kwargs):
        super().__init__(parent, bg=theme.bg, **kwargs)
        self.theme = theme
        
        # 回调
        self._on_save_hotkey: Callable = None
        self._on_save_autostart: Callable = None
        self._on_startup_apps_change: Callable = None
        
        # 数据
        self._startup_apps: List[Dict] = []
        
        self._create_ui()
    
    def set_callbacks(
        self,
        on_save_hotkey: Callable = None,
        on_save_autostart: Callable = None,
        on_startup_apps_change: Callable = None,
        **kwargs  # 接受其他未使用的参数
    ):
        """设置回调函数"""
        self._on_save_hotkey = on_save_hotkey
        self._on_save_autostart = on_save_autostart
        self._on_startup_apps_change = on_startup_apps_change
    
    def _create_ui(self):
        """创建界面"""
        # 主容器
        container = tk.Frame(self, bg=self.theme.bg)
        container.pack(fill="both", expand=True, padx=32, pady=24)
        
        # 页面标题
        tk.Label(
            container,
            text="设置",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XL3, "bold"),
            fg=self.theme.fg,
            bg=self.theme.bg
        ).pack(anchor="w", pady=(0, 24))
        
        # 可滚动区域
        self.scroll = ScrollableFrame(container, self.theme)
        self.scroll.pack(fill="both", expand=True)
        
        scroll_content = self.scroll.get_frame()
        
        # ========== 快捷键设置 ==========
        hotkey_card = Card(scroll_content, self.theme)
        hotkey_card.pack(fill="x", pady=(0, 16), padx=4)
        
        hotkey_content = hotkey_card.get_content_frame()
        
        SectionHeader(
            hotkey_content,
            self.theme,
            "快捷键设置",
            "配置锁屏快捷键"
        ).pack(fill="x", pady=(0, 16))
        
        # 启用快捷键
        self.hotkey_enabled = LabeledSwitch(
            hotkey_content,
            self.theme,
            text="启用快捷键",
            description="启用全局快捷键快速锁屏"
        )
        self.hotkey_enabled.pack(fill="x", pady=(0, 12))
        
        # 快捷键组合
        hotkey_combo_frame = tk.Frame(hotkey_content, bg=self.theme.card)
        hotkey_combo_frame.pack(fill="x", pady=(0, 12))
        
        tk.Label(
            hotkey_combo_frame,
            text="快捷键组合",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg,
            bg=self.theme.card
        ).pack(anchor="w", pady=(0, 8))
        
        combo_row = tk.Frame(hotkey_combo_frame, bg=self.theme.card)
        combo_row.pack(fill="x")
        
        self.hotkey_ctrl = ModernCheckbox(combo_row, self.theme, text="Ctrl")
        self.hotkey_ctrl.pack(side="left", padx=(0, 16))
        
        self.hotkey_alt = ModernCheckbox(combo_row, self.theme, text="Alt")
        self.hotkey_alt.pack(side="left", padx=(0, 16))
        
        self.hotkey_shift = ModernCheckbox(combo_row, self.theme, text="Shift")
        self.hotkey_shift.pack(side="left", padx=(0, 16))
        
        tk.Label(
            combo_row,
            text="+",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack(side="left", padx=(0, 8))
        
        self.hotkey_key = ModernEntry(
            combo_row,
            self.theme,
            width=60,
            placeholder="L"
        )
        self.hotkey_key.pack(side="left")
        
        # 保存按钮
        ModernButton(
            hotkey_content,
            self.theme,
            text="保存快捷键设置",
            variant="outline",
            command=self._save_hotkey
        ).pack(anchor="w", pady=(8, 0))
        
        # ========== 自动登录设置 ==========
        autologon_card = Card(scroll_content, self.theme)
        autologon_card.pack(fill="x", pady=(0, 16), padx=4)
        
        autologon_content = autologon_card.get_content_frame()
        
        SectionHeader(
            autologon_content,
            self.theme,
            "自动登录设置",
            "配置 Windows 开机自动登录（需管理员权限）"
        ).pack(fill="x", pady=(0, 16))
        
        # 启用自动登录
        self.autologon_enabled = LabeledSwitch(
            autologon_content,
            self.theme,
            text="启用开机自动登录",
            description="使用 Sysinternals Autologon 工具安全存储凭据"
        )
        self.autologon_enabled.pack(fill="x", pady=(0, 12))
        
        # 用户名
        username_row = tk.Frame(autologon_content, bg=self.theme.card)
        username_row.pack(fill="x", pady=(0, 8))
        
        tk.Label(
            username_row,
            text="用户名",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg,
            bg=self.theme.card,
            width=10,
            anchor="w"
        ).pack(side="left")
        
        self.autologon_username = ModernEntry(
            username_row,
            self.theme,
            placeholder="Windows 用户名"
        )
        self.autologon_username.pack(side="left", fill="x", expand=True)
        
        # 密码
        password_row = tk.Frame(autologon_content, bg=self.theme.card)
        password_row.pack(fill="x", pady=(0, 8))
        
        tk.Label(
            password_row,
            text="密码",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg,
            bg=self.theme.card,
            width=10,
            anchor="w"
        ).pack(side="left")
        
        self.autologon_password = ModernEntry(
            password_row,
            self.theme,
            placeholder="Windows 密码",
            show="●"
        )
        self.autologon_password.pack(side="left", fill="x", expand=True)
        
        # 域名
        domain_row = tk.Frame(autologon_content, bg=self.theme.card)
        domain_row.pack(fill="x", pady=(0, 12))
        
        tk.Label(
            domain_row,
            text="域名",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg,
            bg=self.theme.card,
            width=10,
            anchor="w"
        ).pack(side="left")
        
        self.autologon_domain = ModernEntry(
            domain_row,
            self.theme,
            placeholder="."
        )
        self.autologon_domain.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            autologon_content,
            text="提示：域名填 . 表示本机，留空则使用当前域",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XS),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack(anchor="w", pady=(0, 8))
        
        # 保存按钮
        ModernButton(
            autologon_content,
            self.theme,
            text="保存自动登录设置",
            variant="outline",
            command=self._save_autologon
        ).pack(anchor="w")
        
        # ========== 启动软件管理 ==========
        startup_card = Card(scroll_content, self.theme)
        startup_card.pack(fill="x", pady=(0, 16), padx=4)
        
        startup_content = startup_card.get_content_frame()
        
        SectionHeader(
            startup_content,
            self.theme,
            "开机启动软件",
            "管理开机时自动运行的软件"
        ).pack(fill="x", pady=(0, 16))
        
        # 添加按钮
        btn_row = tk.Frame(startup_content, bg=self.theme.card)
        btn_row.pack(fill="x", pady=(0, 12))
        
        ModernButton(
            btn_row,
            self.theme,
            text="➕ 添加软件",
            variant="outline",
            command=self._add_startup_app
        ).pack(side="left")
        
        # 软件列表
        self.apps_list_frame = tk.Frame(startup_content, bg=self.theme.card)
        self.apps_list_frame.pack(fill="x")
        
        # ========== 程序自启动 ==========
        autostart_card = Card(scroll_content, self.theme)
        autostart_card.pack(fill="x", pady=(0, 16), padx=4)
        
        autostart_content = autostart_card.get_content_frame()
        
        SectionHeader(
            autostart_content,
            self.theme,
            "程序设置",
            "OfficeGuard 自身的启动设置"
        ).pack(fill="x", pady=(0, 16))
        
        self.app_autostart = LabeledSwitch(
            autostart_content,
            self.theme,
            text="开机自启动 OfficeGuard",
            description="计算机启动时自动运行此程序"
        )
        self.app_autostart.pack(fill="x")
    
    def _save_hotkey(self):
        """保存快捷键设置"""
        if self._on_save_hotkey:
            self._on_save_hotkey(
                self.hotkey_enabled.get(),
                self.hotkey_ctrl.get(),
                self.hotkey_alt.get(),
                self.hotkey_shift.get(),
                self.hotkey_key.get() or "L"
            )
    
    def _save_autologon(self):
        """保存自动登录设置"""
        if self._on_save_autostart:
            self._on_save_autostart(
                self.autologon_enabled.get(),
                self.autologon_username.get(),
                self.autologon_password.get(),
                self.autologon_domain.get() or "."
            )
    
    def _add_startup_app(self):
        """添加启动软件"""
        file_path = filedialog.askopenfilename(
            title="选择要添加的软件",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        
        if file_path:
            import os
            name = os.path.basename(file_path)
            
            app = {
                "name": name,
                "path": file_path,
                "args": "",
                "enabled": True
            }
            
            self._startup_apps.append(app)
            self._refresh_apps_list()
            
            if self._on_startup_apps_change:
                self._on_startup_apps_change(self._startup_apps)
    
    def _refresh_apps_list(self):
        """刷新软件列表显示"""
        # 清空现有列表
        for widget in self.apps_list_frame.winfo_children():
            widget.destroy()
        
        if not self._startup_apps:
            tk.Label(
                self.apps_list_frame,
                text="暂无启动软件，点击上方按钮添加",
                font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
                fg=self.theme.muted,
                bg=self.theme.card
            ).pack(anchor="w", pady=8)
            return
        
        for i, app in enumerate(self._startup_apps):
            self._create_app_row(i, app)
    
    def _create_app_row(self, index: int, app: Dict):
        """创建软件行"""
        row = tk.Frame(self.apps_list_frame, bg=self.theme.card)
        row.pack(fill="x", pady=4)
        
        # 启用开关
        enabled_var = tk.BooleanVar(value=app.get("enabled", True))
        
        def toggle_enabled():
            app["enabled"] = enabled_var.get()
            if self._on_startup_apps_change:
                self._on_startup_apps_change(self._startup_apps)
        
        cb = tk.Checkbutton(
            row,
            variable=enabled_var,
            command=toggle_enabled,
            bg=self.theme.card,
            activebackground=self.theme.card
        )
        cb.pack(side="left")
        
        # 软件名称
        tk.Label(
            row,
            text=app.get("name", "未命名"),
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.fg if app.get("enabled", True) else self.theme.muted,
            bg=self.theme.card
        ).pack(side="left", padx=(4, 0))
        
        # 路径
        tk.Label(
            row,
            text=f"({app.get('path', '')[:30]}...)" if len(app.get('path', '')) > 30 else f"({app.get('path', '')})",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.XS),
            fg=self.theme.muted,
            bg=self.theme.card
        ).pack(side="left", padx=(8, 0))
        
        # 删除按钮
        def delete_app():
            self._startup_apps.pop(index)
            self._refresh_apps_list()
            if self._on_startup_apps_change:
                self._on_startup_apps_change(self._startup_apps)
        
        del_btn = tk.Label(
            row,
            text="✕",
            font=(self.theme.fonts.FAMILY, self.theme.fonts.SM),
            fg=self.theme.colors.danger,
            bg=self.theme.card,
            cursor="hand2"
        )
        del_btn.pack(side="right")
        del_btn.bind("<Button-1>", lambda e: delete_app())
    
    def load_settings(
        self,
        hotkey_enabled: bool = False,
        hotkey_ctrl: bool = False,
        hotkey_alt: bool = False,
        hotkey_shift: bool = False,
        hotkey_key: str = "L",
        autostart_enabled: bool = False,
        autologon_enabled: bool = False,
        autologon_username: str = "",
        autologon_domain: str = ".",
        startup_apps: list = None
    ):
        """加载设置数据"""
        # 快捷键设置
        self.hotkey_enabled.set(hotkey_enabled)
        self.hotkey_ctrl.set(hotkey_ctrl)
        self.hotkey_alt.set(hotkey_alt)
        self.hotkey_shift.set(hotkey_shift)
        self.hotkey_key.set(hotkey_key or "L")
        
        # 自动登录
        self.autologon_enabled.set(autologon_enabled)
        self.autologon_username.set(autologon_username)
        self.autologon_domain.set(autologon_domain or ".")
        
        # 程序自启
        self.app_autostart.set(autostart_enabled)
        
        # 启动软件
        self._startup_apps = startup_apps or []
        self._refresh_apps_list()
