"""
主应用程序类
整合所有模块，构建完整的应用
"""

import tkinter as tk
from tkinter import messagebox
import atexit
import ctypes

from .theme import Theme
from .components.sidebar import Sidebar, SidebarItem
from .pages.timer_page import TimerPage
from .pages.lock_page import LockPage
from .pages.settings_page import SettingsPage
from .pages.about_page import AboutPage

from ..core.config import ConfigManager
from ..core.timer import TimerManager
from ..core.locker import SystemLocker
from ..core.hotkey import HotkeyManager
from ..core.tray import TrayManager
from ..core.autostart import (
    AutoStartManager, AutoLogonManager, 
    is_system_boot, remove_boot_startup_args, launch_startup_apps
)
from ..utils.logger import get_logger

logger = get_logger('app')


class ModernApp:
    """现代化主应用"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("OfficeGuard - 系统优化助手")
        self.root.configure(bg="#ffffff")
        
        # 初始化管理器
        self.config = ConfigManager()
        # 强制使用浅色主题
        self.theme = Theme("light")
        self.config.set("theme", "light")
        self.timer = TimerManager()
        self.locker = SystemLocker()
        self.hotkey = HotkeyManager()
        self.tray = TrayManager()
        self.autostart = AutoStartManager()
        self.autologon = AutoLogonManager()
        
        # 窗口设置
        self._setup_window()
        
        # 创建UI
        self._create_ui()
        
        # 设置回调
        self._setup_callbacks()
        
        # 启动服务
        self._start_services()
        
        # 注册退出处理
        atexit.register(self._cleanup)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 检查开机启动
        self._check_boot_startup()
        
        # 首次运行引导
        if self.config.is_first_run:
            self.root.after(1000, self._show_first_run_guide)
    
    def _setup_window(self):
        """设置窗口"""
        # 尝试设置 DPI 感知
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        # 窗口大小和位置
        w = self.config.get("win_w")
        h = self.config.get("win_h")
        x = self.config.get("win_x")
        y = self.config.get("win_y")
        
        if x != -1 and y != -1:
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        else:
            # 居中显示
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            cx = (sw - w) // 2
            cy = (sh - h) // 2
            self.root.geometry(f"{w}x{h}+{cx}+{cy}")
        
        # 最小尺寸
        self.root.minsize(800, 550)
    
    def _create_ui(self):
        """创建用户界面"""
        # 主容器
        self.main_frame = tk.Frame(self.root, bg=self.theme.bg)
        self.main_frame.pack(fill="both", expand=True)
        
        # 侧边栏
        menu_items = [
            SidebarItem("timer", "定时任务", "⏱️"),
            SidebarItem("lock", "系统保护", "🛡️"),
            SidebarItem("settings", "设置", "⚙️"),
            SidebarItem("about", "关于", "ℹ️"),
        ]
        
        self.sidebar = Sidebar(
            self.main_frame,
            self.theme,
            items=menu_items,
            on_select=self._on_page_change
        )
        self.sidebar.pack(side="left", fill="y")
        
        # 内容区域
        self.content_frame = tk.Frame(self.main_frame, bg=self.theme.bg)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # 创建页面
        self.pages = {}
        self._create_pages()
        
        # 显示默认页面
        self._show_page("timer")
    
    def _create_pages(self):
        """创建所有页面"""
        # 定时任务页面
        self.pages["timer"] = TimerPage(self.content_frame, self.theme)
        self.pages["timer"].set_callbacks(
            on_start_shutdown=lambda m, g: self._start_timer("shutdown", m, g),
            on_start_sleep=lambda m, g: self._start_timer("sleep", m, g),
            on_cancel=self._cancel_timer
        )
        
        # 系统保护页面
        self.pages["lock"] = LockPage(self.content_frame, self.theme)
        self.pages["lock"].set_callbacks(on_lock=self._lock_system)
        self.pages["lock"].update_hotkey(self.config.get_hotkey_display())
        
        # 设置页面
        self.pages["settings"] = SettingsPage(self.content_frame, self.theme)
        self.pages["settings"].set_callbacks(
            on_save_hotkey=self._save_hotkey_settings,
            on_app_autostart_change=self._on_app_autostart_change,
            on_save_autologon=self._save_autologon_settings,
            on_startup_apps_change=self._save_startup_apps
        )
        self._load_settings_page()
        
        # 关于页面
        self.pages["about"] = AboutPage(self.content_frame, self.theme)
    
    def _show_page(self, page_id: str):
        """显示指定页面"""
        for pid, page in self.pages.items():
            if pid == page_id:
                page.pack(fill="both", expand=True)
            else:
                page.pack_forget()
    
    def _on_page_change(self, page_id: str):
        """页面切换回调"""
        self._show_page(page_id)
    
    def _setup_callbacks(self):
        """设置各模块回调"""
        # 定时器回调
        self.timer.set_callbacks(
            on_tick=self._on_timer_tick,
            on_grace_tick=self._on_grace_tick,
            on_complete=self._on_timer_complete,
            on_cancel=self._on_timer_cancel
        )
        
        # 锁定器回调
        self.locker.set_callbacks(on_unlock=self._on_unlock)
        
        # 快捷键回调
        self.hotkey.set_callback(on_trigger=self._on_hotkey_trigger)
        
        # 托盘回调
        self.tray.set_callbacks(
            on_show=self._show_window,
            on_quit=self._quit_app,
            on_toggle_hotkey=self._toggle_hotkey
        )
    
    def _start_services(self):
        """启动后台服务"""
        # 配置并启动快捷键
        self.hotkey.configure(
            ctrl=self.config.get("hotkey_ctrl"),
            alt=self.config.get("hotkey_alt"),
            shift=self.config.get("hotkey_shift"),
            key=self.config.get("hotkey_key")
        )
        self.hotkey.enabled = self.config.get("hotkey_enabled")
        self.hotkey.start()
        
        # 启动托盘
        self.root.after(100, self._start_tray)
    
    def _start_tray(self):
        """启动系统托盘"""
        self.tray.start(hotkey_enabled=self.config.get("hotkey_enabled"))
        # 隐藏主窗口
        self.root.withdraw()
        logger.info("应用已最小化到托盘")
    
    def _check_boot_startup(self):
        """检查是否是开机启动"""
        if is_system_boot():
            logger.info("检测到开机启动")
            remove_boot_startup_args()
            
            # 延迟执行开机任务
            self.root.after(2000, self._run_boot_tasks)
    
    def _run_boot_tasks(self):
        """执行开机启动任务"""
        if not self.config.get("autostart_enabled"):
            return
        
        startup_apps = self.config.get("startup_apps")
        if startup_apps:
            launched, failed = launch_startup_apps(startup_apps)
            logger.info(f"开机启动完成: 成功={launched}, 失败={failed}")
    
    def _show_first_run_guide(self):
        """显示首次运行引导"""
        self._show_window()
        
        hotkey = self.config.get_hotkey_display()
        msg = (
            f"🎉 欢迎使用 OfficeGuard！\n\n"
            f"💡 功能说明：\n"
            f"  • 定时任务：设置定时关机/睡眠\n"
            f"  • 系统保护：一键锁定系统\n"
            f"  • 快捷键：{hotkey} 快速锁定\n"
            f"  • 托盘图标：右下角可快速访问\n\n"
            f"⚠️ 使用提示：\n"
            f"  • 锁定后需输入数字密码恢复\n"
            f"  • 可在设置中自定义快捷键\n"
            f"  • 配置文件已使用加密保护"
        )
        
        messagebox.showinfo("欢迎", msg, parent=self.root)
        self.config.mark_first_run_complete()
    
    # ==================== 定时器相关 ====================
    
    def _start_timer(self, action: str, minutes: float, grace: int):
        """启动定时器"""
        if self.timer.start(action, minutes, grace, self.config.get("mouse_threshold")):
            self.pages["timer"].update_state(True, task_type="关机" if action == "shutdown" else "睡眠")
            self._timer_loop()
            
            # 保存设置
            self.config.set("timer_minutes", minutes)
            self.config.set("grace_seconds", grace)
            self.config.save()
    
    def _timer_loop(self):
        """定时器更新循环"""
        if not self.timer.running:
            return
        
        running, in_grace = self.timer.update()
        
        if running:
            if in_grace:
                # 缓冲期
                if self.timer.update_grace():
                    # 检测到活动，取消
                    self._cancel_timer()
                    messagebox.showinfo("提示", "检测到用户活动，任务已取消", parent=self.root)
                else:
                    self.root.after(1000, self._timer_loop)
            else:
                self.root.after(500, self._timer_loop)
    
    def _cancel_timer(self):
        """取消定时器"""
        self.timer.cancel("手动取消")
        self.pages["timer"].update_state(False)
    
    def _on_timer_tick(self, h: int, m: int, s: int):
        """定时器计时回调"""
        total = self.timer.total_seconds
        remaining = self.timer.remaining_seconds
        progress = remaining / total if total > 0 else 0
        self.pages["timer"].update_progress(progress, remaining)
    
    def _on_grace_tick(self, remaining: int):
        """缓冲期计时回调"""
        self.pages["timer"].update_grace(remaining)
        
        # 显示窗口
        self._show_window()
        self.root.attributes("-topmost", True)
    
    def _on_timer_complete(self):
        """定时器完成回调"""
        self.pages["timer"].update_state(False)
        self.root.attributes("-topmost", False)
    
    def _on_timer_cancel(self, msg: str):
        """定时器取消回调"""
        self.pages["timer"].update_state(False)
        self.root.attributes("-topmost", False)
    
    # ==================== 锁定相关 ====================
    
    def _lock_system(self, password: str):
        """锁定系统"""
        self.config.set("password", password)
        self.config.save()
        
        if self.locker.lock(password):
            self.root.withdraw()
            self._create_blocker()
            self._mouse_trap_loop()
    
    def _create_blocker(self):
        """创建遮挡窗口"""
        user32 = ctypes.windll.user32
        
        vx = user32.GetSystemMetrics(76)
        vy = user32.GetSystemMetrics(77)
        vw = user32.GetSystemMetrics(78)
        vh = user32.GetSystemMetrics(79)
        
        self.blocker = tk.Toplevel(self.root)
        self.blocker.geometry(f"{vw}x{vh}+{vx}+{vy}")
        self.blocker.overrideredirect(True)
        self.blocker.attributes("-topmost", True)
        self.blocker.configure(bg="black", cursor="none")
        self.blocker.attributes("-alpha", 0.01)
        self.blocker.bind("<Key>", lambda e: "break")
        self.blocker.focus_force()
        
        self._focus_loop()
    
    def _focus_loop(self):
        """保持焦点循环"""
        if self.locker.is_locked and hasattr(self, 'blocker') and self.blocker:
            try:
                self.blocker.focus_force()
            except:
                pass
            self.root.after(200, self._focus_loop)
    
    def _mouse_trap_loop(self):
        """鼠标困禁循环"""
        if self.locker.is_locked:
            self.locker.trap_mouse()
            self.root.after(500, self._mouse_trap_loop)
    
    def _on_unlock(self):
        """解锁回调"""
        if hasattr(self, 'blocker') and self.blocker:
            try:
                self.blocker.destroy()
            except:
                pass
            self.blocker = None
        
        logger.info("系统已解锁")
    
    def _on_hotkey_trigger(self):
        """快捷键触发回调"""
        if self.locker.is_locked:
            return
        
        password = self.config.get("password")
        self.root.after(0, lambda: self._lock_system(password))
    
    # ==================== 设置相关 ====================
    
    def _load_settings_page(self):
        """加载设置页面数据"""
        self.pages["settings"].load_settings(
            hotkey_enabled=self.config.get("hotkey_enabled"),
            hotkey_ctrl=self.config.get("hotkey_ctrl"),
            hotkey_alt=self.config.get("hotkey_alt"),
            hotkey_shift=self.config.get("hotkey_shift"),
            hotkey_key=self.config.get("hotkey_key"),
            autostart_enabled=self.config.get("autostart_enabled"),
            autologon_enabled=self.config.get("autologon_enabled"),
            autologon_username=self.config.get("autologon_username"),
            autologon_domain=self.config.get("autologon_domain"),
            startup_apps=self.config.get("startup_apps")
        )
    
    def _save_hotkey_settings(self, enabled: bool, ctrl: bool, alt: bool, shift: bool, key: str):
        """保存快捷键设置"""
        self.config.set("hotkey_enabled", enabled)
        self.config.set("hotkey_ctrl", ctrl)
        self.config.set("hotkey_alt", alt)
        self.config.set("hotkey_shift", shift)
        self.config.set("hotkey_key", key)
        self.config.save()
        
        # 重新配置快捷键
        self.hotkey.stop()
        self.hotkey.configure(ctrl, alt, shift, key)
        self.hotkey.enabled = enabled
        self.hotkey.start()
        
        # 更新显示
        self.pages["lock"].update_hotkey(self.config.get_hotkey_display())
        
        messagebox.showinfo("成功", f"快捷键已更新为：{self.config.get_hotkey_display()}", parent=self.root)
    
    def _on_app_autostart_change(self, enabled: bool):
        """开机自启动开关回调"""
        def task():
            # 在主线程更新UI
            self.root.after(0, lambda: self.pages["settings"].set_autostart_loading(True))
            
            success = self.autostart.set_autostart(enabled)
            
            def on_complete():
                self.pages["settings"].set_autostart_loading(False)
                if success:
                    self.config.set("autostart_enabled", enabled)
                    self.config.save()
                else:
                    messagebox.showerror("错误", "设置开机自启动失败", parent=self.root)
                    # 恢复开关状态
                    self.pages["settings"].app_autostart.set(not enabled)
            
            self.root.after(0, on_complete)
        
        import threading
        threading.Thread(target=task, daemon=True).start()

    def _save_autologon_settings(self, enabled: bool, username: str, password: str, domain: str):
        """保存自动登录设置"""
        if enabled:
            if not username or not password:
                messagebox.showwarning("警告", "请输入用户名和密码", parent=self.root)
                return
            
            success, msg = self.autologon.set_autologon(True, username, password, domain)
            if success:
                self.config.set("autologon_enabled", True)
                self.config.set("autologon_username", username)
                self.config.set("autologon_password", password)
                self.config.set("autologon_domain", domain)
                self.config.save()
                messagebox.showinfo("成功", msg, parent=self.root)
            else:
                messagebox.showerror("错误", f"设置自动登录失败: {msg}", parent=self.root)
        else:
            if self.config.get("autologon_enabled"):
                success, msg = self.autologon.set_autologon(False)
                if success:
                    self.config.set("autologon_enabled", False)
                    self.config.save()
                    messagebox.showinfo("成功", msg, parent=self.root)
                else:
                    messagebox.showerror("错误", f"禁用自动登录失败: {msg}", parent=self.root)
            else:
                # 已经是禁用状态
                self.config.set("autologon_enabled", False)
                self.config.save()
    
    def _save_startup_apps(self, apps: list):
        """保存启动软件列表"""
        self.config.set("startup_apps", apps)
        self.config.save()
    
    def _toggle_hotkey(self):
        """切换快捷键状态"""
        enabled = not self.config.get("hotkey_enabled")
        self.config.set("hotkey_enabled", enabled)
        self.config.save()
        
        self.hotkey.enabled = enabled
        if enabled:
            self.hotkey.start()
        else:
            self.hotkey.stop()
        
        logger.info(f"快捷键已{'启用' if enabled else '禁用'}")
    
    # ==================== 窗口管理 ====================
    
    def _show_window(self):
        """显示主窗口"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def _on_close(self):
        """窗口关闭事件"""
        if self.locker.is_locked:
            return
        
        # 隐藏到托盘
        self.root.withdraw()
    
    def _quit_app(self):
        """退出应用"""
        if self.locker.is_locked:
            return
        
        self._cleanup()
        self.root.quit()
    
    def _cleanup(self):
        """清理资源"""
        logger.info("正在清理资源...")
        
        # 停止定时器
        if self.timer.running:
            self.timer.cancel("程序退出")
        
        # 解锁系统
        if self.locker.is_locked:
            self.locker.cleanup()
        
        # 停止快捷键
        self.hotkey.stop()
        
        # 停止托盘
        self.tray.stop()
        
        # 保存窗口位置
        try:
            self.config.set("win_w", self.root.winfo_width())
            self.config.set("win_h", self.root.winfo_height())
            self.config.set("win_x", self.root.winfo_x())
            self.config.set("win_y", self.root.winfo_y())
            self.config.save()
        except:
            pass
        
        logger.info("清理完成")
    
    def run(self):
        """运行应用"""
        logger.info("应用已启动")
        self.root.mainloop()
