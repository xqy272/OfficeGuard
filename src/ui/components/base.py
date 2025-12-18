"""
基础 UI 组件
简洁现代风格 - 参考 shadcn/ui
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from ..theme import Theme


class ModernFrame(tk.Frame):
    """现代化 Frame"""
    
    def __init__(self, parent, theme: Theme, **kwargs):
        bg = kwargs.pop('bg', theme.bg)
        super().__init__(parent, bg=bg, **kwargs)
        self.theme = theme


class ModernLabel(tk.Label):
    """现代化 Label"""
    
    def __init__(self, parent, theme: Theme, variant: str = "primary", **kwargs):
        # 根据变体选择颜色
        fg_map = {
            "primary": theme.fg,
            "secondary": theme.fg2,
            "muted": theme.muted,
            "accent": theme.accent,
            "success": theme.colors.success,
            "warning": theme.colors.warning,
            "danger": theme.colors.danger,
        }
        
        fg = kwargs.pop('fg', fg_map.get(variant, theme.fg))
        bg = kwargs.pop('bg', theme.bg)
        font = kwargs.pop('font', (theme.fonts.FAMILY, theme.fonts.BASE))
        
        super().__init__(parent, fg=fg, bg=bg, font=font, **kwargs)
        self.theme = theme


class ModernButton(tk.Frame):
    """现代化按钮 - 简洁风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        text: str = "",
        command: Callable = None,
        variant: str = "primary",
        width: int = None,
        height: int = 36,
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, **kwargs)
        
        self.theme = theme
        self.text = text
        self.command = command
        self.variant = variant
        self._height = height
        self._enabled = True
        self._hover = False  # 跟踪悬浮状态
        
        # 获取颜色
        self._setup_colors()
        
        # 创建按钮
        self._create_button(width)
    
    def _setup_colors(self):
        """设置按钮颜色"""
        c = self.theme.colors
        
        color_map = {
            "primary": (c.btn_primary_bg, c.btn_primary_fg, c.accent_hover),
            "secondary": (c.btn_secondary_bg, c.btn_secondary_fg, c.bg_tertiary),
            "danger": (c.btn_danger_bg, c.btn_danger_fg, "#dc2626"),
            "destructive": (c.btn_danger_bg, c.btn_danger_fg, "#dc2626"),
            "success": (c.success, "#ffffff", "#16a34a"),
            "outline": (c.btn_outline_bg, c.btn_outline_fg, c.bg_tertiary),
            "ghost": (c.bg_primary, c.text_secondary, c.bg_tertiary),
        }
        
        self.bg_color, self.fg_color, self.hover_color = color_map.get(
            self.variant, 
            color_map["primary"]
        )
        self.current_bg = self.bg_color
    
    def _create_button(self, width):
        """创建按钮"""
        # 边框容器 (用于 outline 变体)
        if self.variant == "outline":
            self.border_frame = tk.Frame(self, bg=self.theme.border)
            self.border_frame.pack(fill="both", expand=True)
            container = self.border_frame
            pad = 1
        else:
            container = self
            pad = 0
        
        # 按钮主体
        self.btn_bg = tk.Frame(container, bg=self.current_bg)
        if pad:
            self.btn_bg.pack(fill="both", expand=True, padx=pad, pady=pad)
        else:
            self.btn_bg.pack(fill="both", expand=True)
        
        # 内容
        content_frame = tk.Frame(self.btn_bg, bg=self.current_bg)
        content_frame.pack(expand=True)
        
        # 文字
        self.label = tk.Label(
            content_frame,
            text=self.text,
            font=(self.theme.fonts.FAMILY, self.theme.fonts.BASE),
            fg=self.fg_color,
            bg=self.current_bg,
            cursor="hand2"
        )
        self.label.pack(pady=8, padx=16)
        
        # 设置宽度
        if width:
            self.configure(width=width)
            self.btn_bg.configure(width=width - 2 if self.variant == "outline" else width)
        
        self.configure(height=self._height)
        
        # 绑定事件 - 使用统一的检测方法
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # 所有子组件都绑定点击事件
        for widget in [self, self.btn_bg, content_frame, self.label]:
            widget.bind("<Button-1>", self._on_click)
    
    def _on_enter(self, event):
        """鼠标进入按钮区域"""
        if not self._enabled:
            return
        # 取消任何待处理的离开检测
        if hasattr(self, '_leave_after_id') and self._leave_after_id:
            self.after_cancel(self._leave_after_id)
            self._leave_after_id = None
        
        # 只有真正需要改变时才更新
        if not self._hover:
            self._hover = True
            self._apply_hover_style()
    
    def _on_leave(self, event):
        """鼠标离开按钮区域"""
        if not self._enabled:
            return
        # 使用延迟检测，避免在子组件间移动时抖动
        if hasattr(self, '_leave_after_id') and self._leave_after_id:
            self.after_cancel(self._leave_after_id)
        self._leave_after_id = self.after(30, self._check_leave)
    
    def _check_leave(self):
        """延迟检查是否真的离开了按钮"""
        self._leave_after_id = None
        if not self._enabled:
            return
        
        # 检查鼠标是否真的离开了整个按钮区域
        try:
            x, y = self.winfo_pointerxy()
            bx = self.winfo_rootx()
            by = self.winfo_rooty()
            bw = self.winfo_width()
            bh = self.winfo_height()
            
            # 如果鼠标仍在按钮范围内，不处理
            if bx <= x < bx + bw and by <= y < by + bh:
                return
        except:
            pass
        
        # 只有真正需要改变时才更新
        if self._hover:
            self._hover = False
            self._apply_normal_style()
    
    def _apply_hover_style(self):
        """应用悬浮样式"""
        self.current_bg = self.hover_color
        self.btn_bg.configure(bg=self.current_bg)
        for child in self.btn_bg.winfo_children():
            try:
                child.configure(bg=self.current_bg)
                for subchild in child.winfo_children():
                    subchild.configure(bg=self.current_bg)
            except:
                pass
    
    def _apply_normal_style(self):
        """应用普通样式"""
        self.current_bg = self.bg_color
        self.btn_bg.configure(bg=self.current_bg)
        for child in self.btn_bg.winfo_children():
            try:
                child.configure(bg=self.current_bg)
                for subchild in child.winfo_children():
                    subchild.configure(bg=self.current_bg)
            except:
                pass
    
    def _on_click(self, event):
        """点击事件"""
        if self._enabled and self.command:
            self.command()
    
    def set_enabled(self, enabled: bool):
        """设置启用状态"""
        self._enabled = enabled
        if enabled:
            self.label.configure(fg=self.fg_color)
        else:
            self.label.configure(fg=self.theme.muted)
    
    def configure(self, **kwargs):
        """配置按钮属性（兼容 state 选项）"""
        if "state" in kwargs:
            state = kwargs.pop("state")
            self.set_enabled(state != "disabled")
        super().configure(**kwargs)
    
    def set_text(self, text: str):
        """设置按钮文字"""
        self.text = text
        self.label.configure(text=text)


class EyeIcon(tk.Canvas):
    """密码可见性切换图标"""
    
    def __init__(self, parent, theme: Theme, command: Callable, size: int = 16, **kwargs):
        bg = kwargs.pop('bg', theme.colors.input_bg)
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0, **kwargs)
        self.theme = theme
        self.command = command
        self._size = size
        self._is_visible = False
        
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Enter>", lambda e: self.configure(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.configure(cursor=""))
        self.draw()

    def set_state(self, is_visible: bool):
        self._is_visible = is_visible
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self._size, self._size
        color = self.theme.muted
        
        # 眼睛轮廓
        # 上眼睑
        self.create_line(1, h/2, w/2, 1, w-1, h/2, smooth=True, fill=color, width=1.5)
        # 下眼睑
        self.create_line(1, h/2, w/2, h-1, w-1, h/2, smooth=True, fill=color, width=1.5)
        
        # 瞳孔
        self.create_oval(w*0.35, h*0.35, w*0.65, h*0.65, fill=color, outline="")
        
        if self._is_visible:
            # 斜杠 (表示点击隐藏，或者当前是可见状态)
            # 这里设计为：可见状态下显示斜杠眼，表示"点击隐藏"
            self.create_line(3, 3, w-3, h-3, fill=color, width=1.5)


class ModernEntry(tk.Frame):
    """现代化输入框 - 简洁风格"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        placeholder: str = "",
        show: str = None,
        width: int = 200,
        **kwargs
    ):
        super().__init__(parent, bg=theme.bg, **kwargs)
        
        self.theme = theme
        self.placeholder = placeholder
        self._show_char = show
        self._has_focus = False
        self._has_content = False
        self._is_visible = False # 密码是否可见
        
        # 边框容器
        self.border_frame = tk.Frame(self, bg=theme.border)
        self.border_frame.pack(fill="both", expand=True)
        
        # 内部容器
        self.inner = tk.Frame(self.border_frame, bg=theme.colors.input_bg)
        self.inner.pack(fill="both", expand=True, padx=1, pady=1)
        
        # 输入框
        self.entry = tk.Entry(
            self.inner,
            font=(theme.fonts.FAMILY, theme.fonts.BASE),
            fg=theme.fg,
            bg=theme.colors.input_bg,
            insertbackground=theme.fg,
            relief="flat",
            width=width // 8,
            show=show if show else ""
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=8)
        
        # 密码可见性切换按钮
        if show:
            self.eye_icon = EyeIcon(
                self.inner,
                theme,
                command=self._toggle_visibility,
                bg=theme.colors.input_bg
            )
            self.eye_icon.pack(side="right", padx=(0, 10))
        
        # 显示 placeholder
        self._show_placeholder()
        
        # 绑定事件
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<KeyRelease>", self._on_key)
    
    def _toggle_visibility(self):
        """切换密码可见性"""
        self._is_visible = not self._is_visible
        self.eye_icon.set_state(self._is_visible)
        self._update_show_char()
        
    def _update_show_char(self):
        """更新显示字符"""
        if not self._show_char:
            return
            
        if not self._has_content and not self._has_focus:
            # 显示占位符时，不隐藏
            self.entry.configure(show="")
        else:
            # 显示内容时，根据可见性状态决定
            if self._is_visible:
                self.entry.configure(show="")
            else:
                self.entry.configure(show=self._show_char)
    
    def _show_placeholder(self):
        """显示占位符"""
        if not self._has_content and not self._has_focus:
            self.entry.delete(0, tk.END)
            self.entry.configure(show="") # 占位符始终可见
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=self.theme.muted)
    
    def _hide_placeholder(self):
        """隐藏占位符"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=self.theme.fg)
            self._update_show_char()
    
    def _on_focus_in(self, event):
        """获得焦点"""
        self._has_focus = True
        self.border_frame.configure(bg=self.theme.colors.input_focus)
        self._hide_placeholder()
    
    def _on_focus_out(self, event):
        """失去焦点"""
        self._has_focus = False
        self.border_frame.configure(bg=self.theme.border)
        self._has_content = bool(self.entry.get())
        if not self._has_content:
            self._show_placeholder()
    
    def _on_key(self, event):
        """按键事件"""
        self._has_content = bool(self.entry.get())
    
    def get(self) -> str:
        """获取输入值"""
        value = self.entry.get()
        if value == self.placeholder and not self._has_focus and not self._has_content:
             # 注意：如果用户输入的内容恰好和placeholder一样，_has_content应该是True
             # 这里逻辑稍微有点瑕疵，但通常placeholder是提示语，用户输入不会完全一样
             # 更好的判断是依赖 _has_content 标志，但 _has_content 在 _on_key 中更新
             return ""
        # 修正：如果显示的是placeholder，返回空
        if not self._has_content and not self._has_focus:
            return ""
        return value
    
    def set(self, value: str):
        """设置输入值"""
        self.entry.delete(0, tk.END)
        if value:
            self._has_content = True
            self.entry.configure(fg=self.theme.fg)
            self._update_show_char()
            self.entry.insert(0, value)
        else:
            self._has_content = False
            self._show_placeholder()
    
    def clear(self):
        """清空输入"""
        self.set("")
    
    def insert(self, index, value: str):
        """插入文本（兼容 Entry 接口）"""
        if index == 0 and not self._has_content:
            self._hide_placeholder()
        self._has_content = True
        self.entry.configure(fg=self.theme.fg)
        self._update_show_char()
        self.entry.insert(index, value)
    
    def delete(self, first, last=None):
        """删除文本（兼容 Entry 接口）"""
        self.entry.delete(first, last)
        self._has_content = bool(self.entry.get())
        if not self._has_content and not self._has_focus:
            self._show_placeholder()


class ModernCheckbox(tk.Frame):
    """现代化复选框"""
    
    def __init__(
        self,
        parent,
        theme: Theme,
        text: str = "",
        value: bool = False,
        command: Callable = None,
        **kwargs
    ):
        # 确定父组件的背景色
        parent_bg = theme.bg
        try:
            parent_bg = parent.cget('bg')
        except:
            pass
        
        super().__init__(parent, bg=parent_bg, **kwargs)
        
        self.theme = theme
        self.command = command
        self._value = tk.BooleanVar(value=value)
        self._parent_bg = parent_bg
        
        # 复选框 - selectcolor 使用白色背景确保可见
        self.cb = tk.Checkbutton(
            self,
            text=text,
            variable=self._value,
            font=(theme.fonts.FAMILY, theme.fonts.BASE),
            fg=theme.fg,
            bg=parent_bg,
            activebackground=parent_bg,
            activeforeground=theme.fg,
            selectcolor="#ffffff",
            indicatoron=True,
            command=self._on_change
        )
        self.cb.pack(side="left")
    
    def _on_change(self):
        if self.command:
            self.command()
    
    def get(self) -> bool:
        return self._value.get()
    
    def set(self, value: bool):
        self._value.set(value)
