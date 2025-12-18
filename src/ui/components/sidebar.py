"""
侧边栏导航组件
简洁现代风格 - 参考 shadcn/ui
"""

import tkinter as tk
from typing import List, Callable, Optional
from ..theme import Theme


class SidebarItem:
    """侧边栏项目"""
    
    def __init__(self, id: str, text: str, icon: str = ""):
        self.id = id
        self.text = text
        self.icon = icon


class Sidebar(tk.Frame):
    """现代化侧边栏 - 简洁风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        items: List[SidebarItem],
        on_select: Callable[[str], None] = None,
        width: int = 220,
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, width=width, **kwargs)
        self.theme = theme
        self.items = items
        self.on_select = on_select
        self.selected_id = items[0].id if items else None
        self._buttons = {}
        
        self.pack_propagate(False)
        
        # Logo 区域
        logo_frame = tk.Frame(self, bg=theme.bg)
        logo_frame.pack(fill="x", pady=(16, 12), padx=12)
        
        # Logo - 简洁的盾牌图标
        logo_container = tk.Frame(logo_frame, bg=theme.bg)
        logo_container.pack(anchor="w")
        
        # 使用简洁的文字 Logo
        tk.Label(
            logo_container,
            text="🛡",
            font=(theme.fonts.FAMILY, 16),
            bg=theme.bg,
            fg=theme.colors.accent
        ).pack(side="left")
        
        tk.Label(
            logo_container,
            text="OfficeGuard",
            font=(theme.fonts.FAMILY, 12, "bold"),
            bg=theme.bg,
            fg=theme.fg
        ).pack(side="left", padx=(6, 0))
        
        # 分隔线
        sep = tk.Frame(self, bg=theme.border, height=1)
        sep.pack(fill="x", padx=16, pady=(0, 16))
        
        # 菜单项容器
        menu_frame = tk.Frame(self, bg=theme.bg)
        menu_frame.pack(fill="both", expand=True, padx=12)
        
        for item in items:
            self._create_menu_item(menu_frame, item)
        
        # 底部区域
        footer = tk.Frame(self, bg=theme.bg)
        footer.pack(fill="x", pady=16, padx=20)
        
        # 分隔线
        sep2 = tk.Frame(self, bg=theme.border, height=1)
        sep2.pack(fill="x", padx=16, before=footer)
        
        # 版本号
        tk.Label(
            footer,
            text="v2.0.0",
            font=(theme.fonts.FAMILY, 11),
            bg=theme.bg,
            fg=theme.muted
        ).pack(side="left", pady=(8, 0))
    
    def _create_menu_item(self, parent, item: SidebarItem):
        """创建菜单项 - 简洁风格"""
        is_selected = item.id == self.selected_id
        
        # 根据状态设置颜色
        if is_selected:
            bg_color = self.theme.bg3
            fg_color = self.theme.fg
            font_weight = "bold"
        else:
            bg_color = self.theme.bg
            fg_color = self.theme.muted
            font_weight = "normal"
        
        # 按钮容器 - 添加圆角效果
        btn_frame = tk.Frame(parent, bg=bg_color, cursor="hand2")
        btn_frame.pack(fill="x", pady=2)
        
        # 内边距容器
        inner = tk.Frame(btn_frame, bg=bg_color)
        inner.pack(fill="x", padx=8, pady=8)
        
        # 简洁图标映射
        icon_map = {
            "timer": "⏱",      # 时钟
            "lock": "🔒",       # 锁
            "settings": "⚙",   # 齿轮
            "about": "ℹ",      # 信息
        }
        
        icon_text = icon_map.get(item.id, "•")
        
        # 图标
        icon_label = tk.Label(
            inner,
            text=icon_text,
            font=(self.theme.fonts.FAMILY, 12),
            bg=bg_color,
            fg=fg_color,
            width=2
        )
        icon_label.pack(side="left")
        
        # 文字
        text_label = tk.Label(
            inner,
            text=item.text,
            font=(self.theme.fonts.FAMILY, 12, font_weight),
            bg=bg_color,
            fg=fg_color
        )
        text_label.pack(side="left", padx=(4, 0))
        
        # 存储引用
        self._buttons[item.id] = {
            'frame': btn_frame,
            'inner': inner,
            'icon': icon_label,
            'text': text_label,
            'item': item
        }
        
        # 绑定点击事件
        def on_click(e, item_id=item.id):
            self.select(item_id)
        
        for widget in [btn_frame, inner, icon_label, text_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", lambda e, iid=item.id: self._on_hover(iid, True))
            widget.bind("<Leave>", lambda e, iid=item.id: self._on_hover(iid, False))
    
    def _on_hover(self, item_id, entering):
        """鼠标悬停效果"""
        if item_id == self.selected_id:
            return
        
        btn_data = self._buttons.get(item_id)
        if not btn_data:
            return
        
        if entering:
            bg = self.theme.bg2
        else:
            bg = self.theme.bg
        
        # 更新背景色
        btn_data['frame'].configure(bg=bg)
        btn_data['inner'].configure(bg=bg)
        btn_data['icon'].configure(bg=bg)
        btn_data['text'].configure(bg=bg)
    
    def select(self, item_id: str):
        """选择菜单项"""
        if item_id == self.selected_id:
            return
        
        old_id = self.selected_id
        self.selected_id = item_id
        
        # 更新旧选中项样式
        if old_id and old_id in self._buttons:
            self._update_item_style(old_id, False)
        
        # 更新新选中项样式
        if item_id in self._buttons:
            self._update_item_style(item_id, True)
        
        # 触发回调
        if self.on_select:
            self.on_select(item_id)
    
    def _update_item_style(self, item_id: str, is_selected: bool):
        """更新菜单项样式"""
        btn_data = self._buttons.get(item_id)
        if not btn_data:
            return
        
        if is_selected:
            bg = self.theme.bg3
            fg = self.theme.fg
            font = (self.theme.fonts.FAMILY, 13, "bold")
        else:
            bg = self.theme.bg
            fg = self.theme.muted
            font = (self.theme.fonts.FAMILY, 13)
        
        btn_data['frame'].configure(bg=bg)
        btn_data['inner'].configure(bg=bg)
        btn_data['icon'].configure(bg=bg, fg=fg)
        btn_data['text'].configure(bg=bg, fg=fg, font=font)
