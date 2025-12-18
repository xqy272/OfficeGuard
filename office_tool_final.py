# 标准库导入
import os
import sys
import time
import json
import math
import logging
import atexit
from pathlib import Path

# GUI相关
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw
import io

# Windows API
import ctypes
from ctypes import wintypes
import pystray

# 快捷键监听
from pynput import keyboard

# ==========================================
#      1. 环境检测与路径管理
# ==========================================
def get_app_data_dir():
    """
    获取应用数据目录
    打包为exe后使用: C:\\Users\\{用户}\\AppData\\Local\\OfficeGuard
    开发环境也使用相同路径，确保行为一致
    """
    # 使用 LOCALAPPDATA 而不是 APPDATA
    # LOCALAPPDATA = C:\\Users\\用户\\AppData\\Local (本地数据)
    # APPDATA = C:\\Users\\用户\\AppData\\Roaming (漫游数据)
    base_dir = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~')))
    app_dir = base_dir / 'OfficeGuard'
    
    try:
        app_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        # 如果创建失败，降级到用户目录
        app_dir = Path(os.path.expanduser('~')) / '.OfficeGuard'
        app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir

def is_frozen():
    """
    检测是否运行在打包的exe环境中
    PyInstaller: hasattr(sys, '_MEIPASS')
    cx_Freeze: hasattr(sys, 'frozen')
    """
    return getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS')

def get_executable_dir():
    """
    获取exe所在目录（打包后）或脚本所在目录（开发环境）
    """
    if is_frozen():
        # 打包后：返回exe所在目录
        return Path(sys.executable).parent
    else:
        # 开发环境：返回脚本所在目录
        return Path(__file__).parent

# ==========================================
#      2. 日志配置
# ==========================================
def setup_logging():
    """
    配置日志系统 - 日志保存在用户数据目录
    路径: C:\\Users\\{用户}\\AppData\\Local\\OfficeGuard\\logs\\guard.log
    """
    app_dir = get_app_data_dir()
    log_dir = app_dir / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'guard.log'
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带日志轮转）
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,          # 保留3个备份
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # 控制台处理器（仅在开发环境输出）
    handlers = [file_handler]
    if not is_frozen():
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers
    )
    
    logger = logging.getLogger('OfficeGuard')
    logger.info("=" * 60)
    logger.info(f"应用数据目录: {get_app_data_dir()}")
    logger.info(f"运行模式: {'打包EXE' if is_frozen() else '开发环境'}")
    logger.info("=" * 60)
    
    return logger

logger = setup_logging()

# ==========================================
#      0. 权限与优先级配置
# ==========================================
def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    except Exception as e:
        logger.warning(f"管理员检查失败: {e}")
        return False

run_as_admin()

# 提权至实时优先级
try:
    pid = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.kernel32.SetPriorityClass(pid, 0x00000100) # REALTIME_PRIORITY_CLASS
    logger.info("进程优先级已提升")
except Exception as e:
    logger.warning(f"优先级提升失败: {e}")

# ==========================================
#      Windows API & 结构体
# ==========================================
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD), ("flags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

HOOKPROC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# ==========================================
#      配置管理 (增加窗口记录)
# ==========================================
class ConfigManager:
    def __init__(self, filename=None):
        """
        配置管理器
        配置文件路径: C:\\Users\\{用户}\\AppData\\Local\\OfficeGuard\\config\\guard_config.json
        """
        if filename is None:
            app_dir = get_app_data_dir()
            config_dir = app_dir / 'config'
            config_dir.mkdir(parents=True, exist_ok=True)
            filename = config_dir / 'guard_config.json'
        
        self.filename = Path(filename)
        self.defaults = {
            "password": "000",
            "timer_minutes": 60,
            "grace_seconds": 30,
            "mouse_threshold": 15,
            "win_w": 780,
            "win_h": 600,
            "win_x": -1,
            "win_y": -1,
            "first_run": True,  # 首次运行标志
            "hotkey_enabled": True,  # 快捷键开关
            "hotkey_ctrl": True,  # Ctrl键
            "hotkey_alt": True,  # Alt键
            "hotkey_shift": False,  # Shift键
            "hotkey_key": "L"  # 主键
        }
        self.data = self.load()
        
        # 检查是否首次运行
        self.is_first_run = self.data.get("first_run", True)
    
    def mark_first_run_complete(self):
        """标记首次运行已完成"""
        self.set("first_run", False)
        self.save()

    def load(self):
        """加载配置文件"""
        if not os.path.exists(self.filename):
            logger.info("配置文件不存在，使用默认配置")
            return self.defaults.copy()
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                # 合并缺省值
                for k, v in self.defaults.items():
                    if k not in saved:
                        saved[k] = v
                logger.debug(f"配置已从 {self.filename} 加载")
                return saved
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            return self.defaults.copy()

    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            logger.debug("配置已保存")
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
    
    def get(self, key):
        return self.data.get(key, self.defaults.get(key))

    def set(self, key, value):
        if key in self.defaults:
            self.data[key] = value
        else:
            logger.warning(f"尝试设置未知配置项: {key}")

# ==========================================
#      主程序逻辑
# ==========================================
class OfficeGuardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("系统优化助手 v1.2.0")
        
        self.cfg = ConfigManager()
        
        # --- 初始化窗口位置与大小 ---
        self.init_window_geometry()
        
        # 运行时变量
        self.timer_running = False
        self.in_grace_period = False
        self.timer_action = ""
        self.target_timestamp = 0.0
        self.timer_job = None
        self.grace_job = None
        self.action_executed = False  # 新增：防止重复执行
        
        self.is_locked = False
        self.input_buffer = ""
        self.blocker_window = None
        
        self.h_kb_hook = None
        self.h_ms_hook = None
        self.kb_proc_ref = None
        self.ms_proc_ref = None
        self.hotkey_listener = None  # pynput键盘监听器
        
        # 快捷键开关
        self.hotkey_enabled = self.cfg.data.get("hotkey_enabled", True)
        
        # 系统托盘
        self.tray_icon = None
        
        # 注册退出处理器
        atexit.register(self.cleanup_on_exit)

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 安装全局快捷键
        self.install_global_hotkey()
        
        # 创建系统托盘并隐藏窗口
        self.root.after(100, self.setup_tray_and_hide)
        
        # 首次运行引导（在托盘创建后显示）
        if self.cfg.is_first_run:
            self.root.after(1000, self.show_first_run_guide)

    def show_first_run_guide(self):
        """显示首次运行引导"""
        try:
            hotkey_str = self.get_hotkey_display()
            msg = (
                f"🎉 欢迎使用系统优化助手！\n\n"
                f"💡 功能说明：\n"
                f"  • 定时任务：设置定时关机/睡眠\n"
                f"  • 系统优化：优化系统性能\n"
                f"  • 快捷键：{hotkey_str} 快速优化\n"
                f"  • 托盘图标：右下角可快速访问\n\n"
                f"⚠️ 使用提示：\n"
                f"  • 本软件需要管理员权限\n"
                f"  • 优化后需输入密码恢复\n"
                f"  • 可在设置中自定义快捷键\n"
            )
            
            # 显示窗口来弹出消息框
            self.root.deiconify()
            result = messagebox.showinfo(
                "首次运行引导",
                msg,
                parent=self.root
            )
            # 再次隐藏
            self.root.withdraw()
            
            # 标记首次运行已完成
            self.cfg.mark_first_run_complete()
            logger.info("首次运行引导已完成")
            
        except Exception as e:
            logger.error(f"首次运行引导失败: {e}")

    def init_window_geometry(self):
        """恢复上次的窗口大小和位置"""
        w = self.cfg.get("win_w")
        h = self.cfg.get("win_h")
        x = self.cfg.get("win_x")
        y = self.cfg.get("win_y")

        # 确保窗口能显示出来 (更新一下 idletasks 计算边框)
        self.root.update_idletasks()

        if x != -1 and y != -1:
            # 如果有保存的坐标，直接应用
            self.root.geometry(f'{w}x{h}+{x}+{y}')
        else:
            # 如果是首次运行 (-1)，则居中
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            cx = (sw - w) // 2
            cy = (sh - h) // 2
            self.root.geometry(f'{w}x{h}+{cx}+{cy}')

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_timer = tk.Frame(notebook, padx=20, pady=20)
        self.tab_stealth = tk.Frame(notebook, padx=20, pady=20)
        self.tab_settings = tk.Frame(notebook, padx=20, pady=20)
        
        notebook.add(self.tab_timer, text=" ⏱️ 定时任务 ")
        notebook.add(self.tab_stealth, text=" 🛡️ 系统优化 ")
        notebook.add(self.tab_settings, text=" ⚙️ 设置 ")
        
        self.setup_timer_ui()
        self.setup_stealth_ui()
        self.setup_settings_ui()

    def setup_timer_ui(self):
        set_frame = tk.LabelFrame(self.tab_timer, text="任务设置", padx=10, pady=10)
        set_frame.pack(fill="x")
        
        f1 = tk.Frame(set_frame)
        f1.pack(fill="x", pady=5)
        tk.Label(f1, text="倒计时(分钟):", width=12, anchor="e").pack(side=tk.LEFT)
        self.entry_time = ttk.Entry(f1, width=8, justify="center")
        self.entry_time.pack(side=tk.LEFT, padx=5)
        self.entry_time.insert(0, str(self.cfg.get("timer_minutes")))
        
        f2 = tk.Frame(set_frame)
        f2.pack(fill="x", pady=5)
        tk.Label(f2, text="执行前缓冲(秒):", width=12, anchor="e").pack(side=tk.LEFT)
        self.entry_grace = ttk.Entry(f2, width=8, justify="center")
        self.entry_grace.pack(side=tk.LEFT, padx=5)
        self.entry_grace.insert(0, str(self.cfg.get("grace_seconds")))
        tk.Label(f2, text="(缓冲期内动鼠标可取消)", fg="gray", font=("微软雅黑", 8)).pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(self.tab_timer, pady=10)
        btn_frame.pack(fill="x")
        
        self.btn_shutdown = tk.Button(btn_frame, text="启动关机", bg="#ffebee", fg="#c0392b", relief="groove",
                                      command=lambda: self.start_timer("shutdown"))
        self.btn_shutdown.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        
        self.btn_sleep = tk.Button(btn_frame, text="启动睡眠", bg="#e8f5e9", fg="#27ae60", relief="groove",
                                   command=lambda: self.start_timer("sleep"))
        self.btn_sleep.pack(side=tk.LEFT, fill="x", expand=True, padx=(5, 0))

        self.lbl_status = tk.Label(self.tab_timer, text="状态: 准备就绪", fg="gray")
        self.lbl_status.pack(pady=(10, 0))
        
        self.lbl_countdown = tk.Label(self.tab_timer, text="00:00:00", font=("Arial", 28, "bold"), fg="#ccc")
        self.lbl_countdown.pack(pady=5)
        
        self.progress = ttk.Progressbar(self.tab_timer, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=10)
        
        self.btn_cancel = tk.Button(self.tab_timer, text="取消当前任务", state=tk.DISABLED, command=self.cancel_timer_manual)
        self.btn_cancel.pack(fill="x")

    def setup_stealth_ui(self):
        pwd_frame = tk.Frame(self.tab_stealth)
        pwd_frame.pack(pady=10)
        tk.Label(pwd_frame, text="恢复密码 (纯数字):").pack(side=tk.LEFT)
        self.entry_pwd = ttk.Entry(pwd_frame, width=12, justify="center", show="*")
        self.entry_pwd.pack(side=tk.LEFT, padx=5)
        self.entry_pwd.insert(0, str(self.cfg.get("password")))
        
        # 显示/隐藏密码切换按钮
        self.show_pwd_btn = tk.Button(pwd_frame, text="👁️", width=3, relief="groove",
                                       command=self.toggle_password_visibility)
        self.show_pwd_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Label(self.tab_stealth, text="⚡ 系统优化", font=("微软雅黑", 14, "bold"), fg="#2980b9").pack(pady=10)
        
        # 显示当前快捷键
        hotkey_text = self.get_hotkey_display()
        self.lbl_hotkey = tk.Label(self.tab_stealth, text=f"快捷键：{hotkey_text}", fg="#555", font=("微软雅黑", 10))
        self.lbl_hotkey.pack(pady=5)
        
        info = (
            "✅ 优化系统性能\n"
            "✅ 清理内存碎片\n"
            "✅ 支持全局快捷键\n\n"
            "优化期间系统将进入深度优化模式\n"
            "完成后输入密码即可恢复正常"
        )
        tk.Label(self.tab_stealth, text=info, justify="left", bg="#f0f0f0", padx=15, pady=15, relief="sunken").pack(fill="both", expand=True)
        tk.Button(self.tab_stealth, text="🚀 立即优化系统", bg="#27ae60", fg="white",
                  font=("微软雅黑", 12, "bold"), height=2,
                  command=self.lock_system).pack(side=tk.BOTTOM, fill="x", pady=20)
    
    def setup_settings_ui(self):
        """设置界面"""
        # 快捷键设置
        hotkey_frame = tk.LabelFrame(self.tab_settings, text="快捷键设置", padx=15, pady=15)
        hotkey_frame.pack(fill="x", pady=10)
        
        # 快捷键开关
        self.var_hotkey_enabled = tk.BooleanVar(value=self.cfg.get("hotkey_enabled"))
        tk.Checkbutton(hotkey_frame, text="启用全局快捷键", variable=self.var_hotkey_enabled,
                      command=self.on_hotkey_settings_change).pack(anchor="w", pady=5)
        
        # 修饰键
        mod_frame = tk.Frame(hotkey_frame)
        mod_frame.pack(fill="x", pady=5)
        tk.Label(mod_frame, text="修饰键：", width=10, anchor="e").pack(side=tk.LEFT)
        
        self.var_ctrl = tk.BooleanVar(value=self.cfg.get("hotkey_ctrl"))
        tk.Checkbutton(mod_frame, text="Ctrl", variable=self.var_ctrl,
                      command=self.on_hotkey_settings_change).pack(side=tk.LEFT, padx=5)
        
        self.var_alt = tk.BooleanVar(value=self.cfg.get("hotkey_alt"))
        tk.Checkbutton(mod_frame, text="Alt", variable=self.var_alt,
                      command=self.on_hotkey_settings_change).pack(side=tk.LEFT, padx=5)
        
        self.var_shift = tk.BooleanVar(value=self.cfg.get("hotkey_shift"))
        tk.Checkbutton(mod_frame, text="Shift", variable=self.var_shift,
                      command=self.on_hotkey_settings_change).pack(side=tk.LEFT, padx=5)
        
        # 主键
        key_frame = tk.Frame(hotkey_frame)
        key_frame.pack(fill="x", pady=5)
        tk.Label(key_frame, text="主键：", width=10, anchor="e").pack(side=tk.LEFT)
        
        self.entry_hotkey = ttk.Entry(key_frame, width=8, justify="center")
        self.entry_hotkey.pack(side=tk.LEFT, padx=5)
        self.entry_hotkey.insert(0, str(self.cfg.get("hotkey_key")))
        self.entry_hotkey.bind("<KeyRelease>", lambda e: self.on_hotkey_settings_change())
        
        tk.Label(key_frame, text="(单个字母或F1-F12)", fg="gray", font=("微软雅黑", 8)).pack(side=tk.LEFT, padx=5)
        
        # 当前快捷键显示
        preview_frame = tk.Frame(hotkey_frame)
        preview_frame.pack(fill="x", pady=10)
        tk.Label(preview_frame, text="当前快捷键：", width=10, anchor="e").pack(side=tk.LEFT)
        self.lbl_hotkey_preview = tk.Label(preview_frame, text=self.get_hotkey_display(), 
                                           fg="#2980b9", font=("微软雅黑", 11, "bold"))
        self.lbl_hotkey_preview.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        tk.Button(hotkey_frame, text="💾 保存快捷键设置", bg="#3498db", fg="white",
                 command=self.save_hotkey_settings).pack(fill="x", pady=10)
        
        # 说明
        info = (
            "💡 提示：\n"
            "• 修改后需点击保存按钮\n"
            "• 建议至少选择一个修饰键\n"
            "• 主键支持A-Z和F1-F12\n"
            "• 保存后会自动重启快捷键"
        )
        tk.Label(self.tab_settings, text=info, justify="left", bg="#ecf0f1", 
                padx=15, pady=15, relief="sunken").pack(fill="x", pady=10)
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        current_show = self.entry_pwd.cget('show')
        if current_show == '*':
            self.entry_pwd.config(show="")
            self.show_pwd_btn.config(text="🙈")
        else:
            self.entry_pwd.config(show="*")
            self.show_pwd_btn.config(text="👁️")
    
    def get_hotkey_display(self):
        """获取快捷键显示文本"""
        parts = []
        if self.cfg.get("hotkey_ctrl"):
            parts.append("Ctrl")
        if self.cfg.get("hotkey_alt"):
            parts.append("Alt")
        if self.cfg.get("hotkey_shift"):
            parts.append("Shift")
        parts.append(self.cfg.get("hotkey_key"))
        return "+".join(parts)
    
    def on_hotkey_settings_change(self):
        """快捷键设置变化时更新预览"""
        try:
            # 更新预览
            parts = []
            if self.var_ctrl.get():
                parts.append("Ctrl")
            if self.var_alt.get():
                parts.append("Alt")
            if self.var_shift.get():
                parts.append("Shift")
            key = self.entry_hotkey.get().strip().upper()
            if key:
                parts.append(key)
            self.lbl_hotkey_preview.config(text="+".join(parts) if parts else "未设置")
        except:
            pass
    
    def save_hotkey_settings(self):
        """保存快捷键设置"""
        try:
            key = self.entry_hotkey.get().strip().upper()
            if not key:
                messagebox.showwarning("警告", "请输入主键（如 L 或 F1）")
                return
            
            # 验证主键
            if len(key) == 1 and not key.isalpha():
                messagebox.showwarning("警告", "主键必须是字母A-Z")
                return
            
            if key.startswith("F") and len(key) > 1:
                try:
                    fn = int(key[1:])
                    if fn < 1 or fn > 12:
                        raise ValueError()
                except:
                    messagebox.showwarning("警告", "功能键必须是F1-F12")
                    return
            
            # 保存设置
            self.cfg.set("hotkey_enabled", self.var_hotkey_enabled.get())
            self.cfg.set("hotkey_ctrl", self.var_ctrl.get())
            self.cfg.set("hotkey_alt", self.var_alt.get())
            self.cfg.set("hotkey_shift", self.var_shift.get())
            self.cfg.set("hotkey_key", key)
            self.cfg.save()
            
            # 重新安装快捷键
            self.uninstall_global_hotkey()
            self.hotkey_enabled = self.var_hotkey_enabled.get()
            self.install_global_hotkey()
            
            # 更新显示
            hotkey_text = self.get_hotkey_display()
            self.lbl_hotkey.config(text=f"快捷键：{hotkey_text}")
            
            messagebox.showinfo("成功", f"快捷键已更新为：{hotkey_text}")
            logger.info(f"快捷键已更新：{hotkey_text}")
            
        except Exception as e:
            logger.error(f"保存快捷键设置失败: {e}")
            messagebox.showerror("错误", f"保存失败：{e}")

    # --- 定时与缓冲逻辑 ---
    def start_timer(self, action):
        if self.timer_running: 
            messagebox.showwarning("提示", "已有任务在运行，请先取消")
            return
        try:
            m = float(self.entry_time.get())
            g = int(self.entry_grace.get())
            if m <= 0 or m > 1440:  # 最多24小时
                raise ValueError("时间必须在0-1440分钟之间")
            if g < 0 or g > 3600:  # 最多1小时缓冲
                raise ValueError("缓冲时间必须在0-3600秒之间")
        except ValueError as e:
            messagebox.showwarning("提示", f"输入无效: {e}")
            return
        except Exception as e:
            logger.error(f"定时器输入解析错误: {e}")
            messagebox.showwarning("提示", "输入解析失败")
            return
        
        # 运行时保存一下设置
        self.cfg.set("timer_minutes", m)
        self.cfg.set("grace_seconds", g)
        self.cfg.save()

        self.action_executed = False  # 重置执行标志
        self.timer_action = action
        self.total_seconds = int(m * 60)
        self.grace_seconds = g
        self.target_timestamp = time.time() + self.total_seconds
        self.timer_running = True
        self.in_grace_period = False
        
        self.update_ui_state(running=True)
        self.lbl_status.config(text=f"正在运行 - {action}倒计时", fg="#2980b9")
        self.progress["maximum"] = self.total_seconds
        logger.info(f"启动{action}倒计时，时长{m}分钟，缓冲{g}秒")
        self.update_clock()

    def update_clock(self):
        if not self.timer_running: return
        if self.in_grace_period: return

        remaining = self.target_timestamp - time.time()
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            h, m = divmod(m, 60)
            self.lbl_countdown.config(text=f"{h:02d}:{m:02d}:{s:02d}", fg="#e74c3c" if remaining < 60 else "#333")
            self.progress["value"] = remaining
            self.timer_job = self.root.after(500, self.update_clock)
        else:
            self.enter_grace_period()

    def enter_grace_period(self):
        self.in_grace_period = True
        self.grace_remaining = self.grace_seconds
        self.start_mouse_pos = self.get_cursor_pos()
        self.last_input_tick = self.get_last_input_tick()
        self.mouse_threshold = self.cfg.get("mouse_threshold")
        
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.lbl_status.config(text="⚠️ 准备执行！移动鼠标以取消！", fg="red", font=("微软雅黑", 10, "bold"))
        self.progress["maximum"] = self.grace_seconds
        self.grace_loop()

    def grace_loop(self):
        if not self.timer_running: return
        
        curr_pos = self.get_cursor_pos()
        dist = math.hypot(curr_pos[0] - self.start_mouse_pos[0], curr_pos[1] - self.start_mouse_pos[1])
        curr_tick = self.get_last_input_tick()
        
        input_changed = (curr_tick > self.last_input_tick)
        mouse_moved_significantly = (dist > self.mouse_threshold)
        
        if mouse_moved_significantly or (input_changed and not mouse_moved_significantly):
            self.cancel_timer_manual(show_msg=True, msg="检测到活动，任务自动取消！")
            return

        if self.grace_remaining > 0:
            self.lbl_countdown.config(text=f"执行中: {self.grace_remaining}s", fg="red")
            self.progress["value"] = self.grace_remaining
            self.grace_remaining -= 1
            self.grace_job = self.root.after(1000, self.grace_loop)
        else:
            self.execute_action()

    def execute_action(self):
        """执行关机/睡眠操作 - 仅执行一次"""
        if self.action_executed:
            logger.warning("操作已执行，忽略重复请求")
            return
        
        self.action_executed = True
        self.cancel_timer_manual(show_msg=False)
        self.reset_ui_after_action()  # 重置UI
        
        try:
            if self.timer_action == "shutdown":
                logger.info("执行系统关机")
                # shutdown /s /f /t 0 会立即关机
                os.system("shutdown /s /f /t 0")
            elif self.timer_action == "sleep":
                logger.info("执行系统睡眠")
                # SetSuspendState(bSuspend, bForce, bWakeupEventsDisabled)
                ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        except Exception as e:
            logger.error(f"执行{self.timer_action}失败: {e}")
            messagebox.showerror("错误", f"执行失败: {e}")

    def cancel_timer_manual(self, show_msg=False, msg=""):
        """取消定时器 - 确保任何情况下都能清理资源"""
        try:
            if self.timer_job: 
                self.root.after_cancel(self.timer_job)
                self.timer_job = None
        except Exception as e:
            logger.warning(f"取消timer_job失败: {e}")
        
        try:
            if self.grace_job: 
                self.root.after_cancel(self.grace_job)
                self.grace_job = None
        except Exception as e:
            logger.warning(f"取消grace_job失败: {e}")
        
        self.timer_running = False
        self.in_grace_period = False
        
        try:
            self.root.attributes("-topmost", False)
        except:
            pass
        
        self.update_ui_state(running=False)
        self.lbl_countdown.config(text="00:00:00", fg="#ccc")
        self.lbl_status.config(text=msg if msg else "状态: 任务已取消", fg="gray")
        self.progress["value"] = 0
        
        if show_msg:
            messagebox.showinfo("提示", msg if msg else "任务已取消")
        
        logger.info(f"定时器已取消: {msg if msg else '手动取消'}")

    def update_ui_state(self, running):
        state_inv = tk.DISABLED if running else tk.NORMAL
        state_run = tk.NORMAL if running else tk.DISABLED
        self.entry_time.config(state=state_inv)
        self.entry_grace.config(state=state_inv)
        self.btn_shutdown.config(state=state_inv)
        self.btn_sleep.config(state=state_inv)
        self.btn_cancel.config(state=state_run)
    
    def reset_ui_after_action(self):
        """执行完操作后重置UI到初始状态"""
        try:
            # 重置倒计时显示
            self.lbl_countdown.config(text="00:00:00", fg="#ccc")
            self.lbl_status.config(text="状态: 准备就绪", fg="gray")
            self.progress["value"] = 0
            
            # 重置输入框
            self.entry_time.delete(0, tk.END)
            self.entry_time.insert(0, str(self.cfg.get("timer_minutes")))
            self.entry_grace.delete(0, tk.END)
            self.entry_grace.insert(0, str(self.cfg.get("grace_seconds")))
            
            # 重置按钮状态
            self.update_ui_state(running=False)
            
            # 重置内部状态
            self.timer_running = False
            self.in_grace_period = False
            self.action_executed = False
            
            logger.info("UI已重置")
        except Exception as e:
            logger.error(f"UI重置失败: {e}")

    def get_cursor_pos(self):
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)

    def get_last_input_tick(self):
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        user32.GetLastInputInfo(ctypes.byref(lii))
        return lii.dwTime

    # --- 隐形锁 ---
    def lock_system(self):
        pwd = self.entry_pwd.get().strip()
        if not pwd.isdigit():
            messagebox.showerror("错误", "密码只能包含数字！")
            return
        
        if len(pwd) < 3:
            messagebox.showerror("错误", "密码长度不能少于3位！")
            return
        
        self.cfg.set("password", pwd)
        self.cfg.save()
        
        self.unlock_code = pwd
        self.is_locked = True
        self.root.withdraw()  # 隐藏主窗口
        self.prevent_sleep(True)
        self.create_blocker()
        self.install_hooks()
        self.trap_mouse()
        logger.info("系统优化已激活")

    def create_blocker(self):
        self.blocker_window = tk.Toplevel(self.root)
        vx = user32.GetSystemMetrics(76)
        vy = user32.GetSystemMetrics(77)
        vw = user32.GetSystemMetrics(78)
        vh = user32.GetSystemMetrics(79)
        self.blocker_window.geometry(f"{vw}x{vh}+{vx}+{vy}")
        self.blocker_window.overrideredirect(True)
        self.blocker_window.attributes("-topmost", True)
        self.blocker_window.configure(bg="black", cursor="none")
        self.blocker_window.attributes("-alpha", 0.01)
        self.input_buffer = ""
        self.blocker_window.bind("<Key>", lambda e: "break")
        self.blocker_window.focus_force()
        self.force_focus_loop()

    def force_focus_loop(self):
        """强制维持焦点 - 优化CPU占用"""
        if self.is_locked and self.blocker_window:
            try:
                self.blocker_window.focus_force()
            except Exception as e:
                logger.warning(f"焦点设置失败: {e}")
            # 改为200ms而不是50ms，降低CPU占用
            self.root.after(200, self.force_focus_loop)
        else:
            # 停止循环
            return

    def trap_mouse(self):
        """困禁鼠标到指定区域 - 使用屏幕中心的小区域"""
        if not self.is_locked: 
            return
        
        try:
            # 获取屏幕中心坐标并创建1x1像素的矩形
            sw = user32.GetSystemMetrics(0)  # SM_CXSCREEN
            sh = user32.GetSystemMetrics(1)  # SM_CYSCREEN
            cx, cy = sw // 2, sh // 2
            
            rect = RECT(cx, cy, cx + 1, cy + 1)
            user32.ClipCursor(ctypes.byref(rect))
        except Exception as e:
            logger.warning(f"鼠标困禁失败: {e}")
        
        # 改为500ms而不是100ms，降低CPU占用
        self.root.after(500, self.trap_mouse)

    def process_key_input(self, char):
        """处理键盘输入"""
        if not self.is_locked:
            return
        
        try:
            self.input_buffer += char
            # 只保留最后N个字符（N = 密码长度）
            self.input_buffer = self.input_buffer[-len(self.unlock_code):]
            
            if self.input_buffer == self.unlock_code:
                self.unlock_success()
        except Exception as e:
            logger.error(f"键盘输入处理错误: {e}")

    def unlock_success(self):
        """解锁成功处理"""
        logger.info("系统优化已完成")
        self.is_locked = False
        
        try:
            user32.ClipCursor(None)
        except Exception as e:
            logger.warning(f"释放鼠标困禁失败: {e}")
        
        self.uninstall_hooks()
        self.prevent_sleep(False)
        
        if self.blocker_window:
            try:
                self.blocker_window.destroy()
            except:
                pass
            self.blocker_window = None
        
        # 不再弹出窗口或显示成功消息
        logger.info("系统已恢复正常，保持静默")

    def install_hooks(self):
        """安装全局键盘和鼠标钩子"""
        def kb_callback(nCode, wParam, lParam):
            try:
                if nCode == 0 and (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN):
                    kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk = kb.vkCode
                    
                    # 主键盘区数字: VK 48-57 对应 '0'-'9'
                    # 小键盘区数字: VK 96-105 对应数字0-9
                    if 48 <= vk <= 57:
                        # 主键盘区
                        char = chr(vk)
                        self.process_key_input(char)
                        return 1
                    elif 96 <= vk <= 105:
                        # 小键盘区
                        char = str(vk - 96)
                        self.process_key_input(char)
                        return 1
                    
                    # 屏蔽所有其他按键
                    return 1
                return user32.CallNextHookEx(self.h_kb_hook, nCode, wParam, lParam)
            except Exception as e:
                logger.error(f"键盘钩子异常: {e}")
                return user32.CallNextHookEx(self.h_kb_hook, nCode, wParam, lParam)

        def ms_callback(nCode, wParam, lParam):
            try:
                if nCode >= 0:
                    return 1  # 屏蔽所有鼠标事件
                return user32.CallNextHookEx(self.h_ms_hook, nCode, wParam, lParam)
            except Exception as e:
                logger.error(f"鼠标钩子异常: {e}")
                return user32.CallNextHookEx(self.h_ms_hook, nCode, wParam, lParam)

        try:
            self.kb_proc_ref = HOOKPROC(kb_callback)
            self.ms_proc_ref = HOOKPROC(ms_callback)
            self.h_kb_hook = user32.SetWindowsHookExA(WH_KEYBOARD_LL, self.kb_proc_ref, 0, 0)
            self.h_ms_hook = user32.SetWindowsHookExA(WH_MOUSE_LL, self.ms_proc_ref, 0, 0)
            
            if self.h_kb_hook == 0 or self.h_ms_hook == 0:
                logger.error("钩子安装失败")
            else:
                logger.info("钩子已安装")
        except Exception as e:
            logger.error(f"钩子安装异常: {e}")

    def uninstall_hooks(self):
        """卸载全局钩子 - 确保安全释放"""
        try:
            if self.h_kb_hook:
                result = user32.UnhookWindowsHookEx(self.h_kb_hook)
                if result:
                    logger.info("键盘钩子已卸载")
                else:
                    logger.warning("键盘钩子卸载失败")
                self.h_kb_hook = None
        except Exception as e:
            logger.error(f"键盘钩子卸载异常: {e}")
        
        try:
            if self.h_ms_hook:
                result = user32.UnhookWindowsHookEx(self.h_ms_hook)
                if result:
                    logger.info("鼠标钩子已卸载")
                else:
                    logger.warning("鼠标钩子卸载失败")
                self.h_ms_hook = None
        except Exception as e:
            logger.error(f"鼠标钩子卸载异常: {e}")
        
        # 清除回调引用
        self.kb_proc_ref = None
        self.ms_proc_ref = None

    def prevent_sleep(self, enable):
        f = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED if enable else ES_CONTINUOUS
        kernel32.SetThreadExecutionState(f)

    # ==========================================
    #      清理与退出逻辑
    # ==========================================
    def cleanup_on_exit(self):
        """程序退出时的清理 - 确保定时器被取消"""
        logger.info("程序正在清理资源...")
        
        # 强制取消所有定时器
        if self.timer_running or self.in_grace_period:
            logger.warning("退出时发现正在运行的定时器，强制取消")
            self.action_executed = True  # 标记已执行，防止关机
            self.timer_running = False
            self.in_grace_period = False
            
            # 取消所有待处理的任务
            try:
                if self.timer_job:
                    self.root.after_cancel(self.timer_job)
                if self.grace_job:
                    self.root.after_cancel(self.grace_job)
            except:
                pass
        
        # 解锁系统（如果处于锁定状态）
        if self.is_locked:
            logger.warning("退出时系统仍处于锁定状态，强制解锁")
            self.is_locked = False
            try:
                user32.ClipCursor(None)
                self.uninstall_hooks()
                self.prevent_sleep(False)
                if self.blocker_window:
                    self.blocker_window.destroy()
            except:
                pass
        
        # 保存配置
        try:
            self.cfg.set("win_w", self.root.winfo_width())
            self.cfg.set("win_h", self.root.winfo_height())
            self.cfg.set("win_x", self.root.winfo_x())
            self.cfg.set("win_y", self.root.winfo_y())
            self.cfg.save()
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
        
        logger.info("清理完成，应用正在退出")

    def on_closing(self):
        """窗口关闭事件处理 - 隐藏而非退出"""
        # 如果系统被锁定，不允许操作
        if self.is_locked:
            return
        
        # 隐藏窗口而不是退出
        self.root.withdraw()
        logger.info("窗口已隐藏到托盘")
    
    # ==========================================
    #      系统托盘功能
    # ==========================================
    def create_tray_icon(self):
        """创建托盘图标"""
        # 创建简单的图标（蓝色圆圈）
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.ellipse((8, 8, 56, 56), fill=(41, 128, 185))
        
        return image
    
    def setup_tray_and_hide(self):
        """设置系统托盘并隐藏主窗口"""
        try:
            icon_image = self.create_tray_icon()
            
            menu = pystray.Menu(
                pystray.MenuItem("进入", self.show_window),
                pystray.MenuItem(
                    lambda text: f"快捷键: {'✓ 开启' if self.hotkey_enabled else '✗ 关闭'}",
                    self.toggle_hotkey
                ),
                pystray.MenuItem("关闭", self.quit_app)
            )
            
            self.tray_icon = pystray.Icon("system_optimizer", icon_image, "系统优化助手", menu)
            
            # 在单独线程中运行托盘图标
            import threading
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            
            # 隐藏主窗口
            self.root.withdraw()
            logger.info("系统托盘已创建，主窗口已隐藏")
            
        except Exception as e:
            logger.error(f"托盘创建失败: {e}")
    
    def show_window(self):
        """从托盘显示主窗口"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        logger.info("主窗口已显示")
    
    def toggle_hotkey(self):
        """切换快捷键开关"""
        self.hotkey_enabled = not self.hotkey_enabled
        self.cfg.data["hotkey_enabled"] = self.hotkey_enabled
        self.cfg.save()
        logger.info(f"快捷键已{'开启' if self.hotkey_enabled else '关闭'}")
    
    def quit_app(self):
        """从托盘退出应用"""
        if self.is_locked:
            logger.warning("系统锁定中，无法退出")
            return
        
        logger.info("用户从托盘退出")
        
        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()
        
        # 卸载全局快捷键
        self.uninstall_global_hotkey()
        
        # 执行清理
        self.cleanup_on_exit()
        self.root.quit()
    
    # ==========================================
    #      全局快捷键功能 (可自定义)
    # ==========================================
    def install_global_hotkey(self):
        """安装全局快捷键（使用pynput）"""
        if not self.hotkey_enabled:
            logger.info("快捷键已禁用，跳过安装")
            return
        
        # 获取配置的快捷键
        key_str = self.cfg.get("hotkey_key").lower()
        need_ctrl = self.cfg.get("hotkey_ctrl")
        need_alt = self.cfg.get("hotkey_alt")
        need_shift = self.cfg.get("hotkey_shift")
        
        try:
            # 先卸载旧的
            self.uninstall_global_hotkey()
            
            # 当前按下的键
            current_keys = set()
            
            # 记录需要的主键虚拟键码
            main_key_vk = None
            if len(key_str) == 1 and key_str.isalpha():
                # 字母键的虚拟键码就是大写字母的ASCII码
                main_key_vk = ord(key_str.upper())
            elif key_str.startswith('f') and len(key_str) > 1:
                # 功能键 F1-F12
                try:
                    fn = int(key_str[1:])
                    if 1 <= fn <= 12:
                        main_key_vk = getattr(keyboard.Key, f'f{fn}')
                except:
                    logger.error(f"无效的功能键: {key_str}")
                    return
            else:
                logger.error(f"无效的快捷键配置: {key_str}")
                return
            
            def is_modifier_pressed(key, modifier_type):
                """检查修饰键是否按下（支持左右）"""
                if modifier_type == 'ctrl':
                    return key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl)
                elif modifier_type == 'alt':
                    return key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt)
                elif modifier_type == 'shift':
                    return key in (keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.shift)
                return False
            
            def check_hotkey():
                """检查当前按键是否匹配快捷键"""
                # 检查修饰键 - 如果需要则必须按下，如果不需要则必须没按下
                has_ctrl = any(is_modifier_pressed(k, 'ctrl') for k in current_keys)
                has_alt = any(is_modifier_pressed(k, 'alt') for k in current_keys)
                has_shift = any(is_modifier_pressed(k, 'shift') for k in current_keys)
                
                ctrl_ok = (need_ctrl and has_ctrl) or (not need_ctrl and not has_ctrl)
                alt_ok = (need_alt and has_alt) or (not need_alt and not has_alt)
                shift_ok = (need_shift and has_shift) or (not need_shift and not has_shift)
                
                # 检查主键 - 匹配虚拟键码
                main_key_pressed = False
                for key in current_keys:
                    if hasattr(key, 'vk') and key.vk == main_key_vk:
                        main_key_pressed = True
                        break
                    elif key == main_key_vk:  # 功能键的情况
                        main_key_pressed = True
                        break
                
                # 调试日志
                logger.info(f"[热键检查] Ctrl={ctrl_ok}({has_ctrl}), Alt={alt_ok}({has_alt}), Shift={shift_ok}({has_shift}), Main={main_key_pressed}, Keys={len(current_keys)}")
                
                return ctrl_ok and alt_ok and shift_ok and main_key_pressed
            
            def on_press(key):
                """按键按下事件"""
                current_keys.add(key)
                logger.info(f"[pynput] 按键按下: {key}")
                
                # 检查是否匹配快捷键
                if check_hotkey():
                    hotkey_str = self.get_hotkey_display()
                    logger.info(f"快捷键 {hotkey_str} 被触发")
                    # 在主线程中执行锁定
                    self.root.after(0, self.trigger_lock_from_hotkey)
            
            def on_release(key):
                """按键释放事件"""
                try:
                    current_keys.discard(key)
                    logger.info(f"[pynput] 按键释放: {key}")
                except:
                    pass
            
            # 启动监听器
            logger.info("正在启动 pynput 监听器...")
            self.hotkey_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.hotkey_listener.start()
            
            # 等待一下确保线程启动
            import time
            time.sleep(0.1)
            
            if self.hotkey_listener.is_alive():
                hotkey_str = self.get_hotkey_display()
                logger.info(f"全局快捷键 {hotkey_str} 已安装 (pynput) - 监听器运行中")
            else:
                logger.error("pynput 监听器启动失败！")
            
        except Exception as e:
            logger.error(f"快捷键安装异常: {e}", exc_info=True)
    
    def uninstall_global_hotkey(self):
        """卸载全局快捷键"""
        try:
            if self.hotkey_listener:
                self.hotkey_listener.stop()
                self.hotkey_listener = None
                logger.info("全局快捷键已注销")
        except Exception as e:
            logger.error(f"快捷键卸载异常: {e}")
    
    def trigger_lock_from_hotkey(self):
        """从快捷键触发锁定"""
        if self.is_locked:
            logger.warning("系统已处于锁定状态")
            return
        
        # 使用当前保存的密码
        pwd = self.cfg.get("password")
        self.unlock_code = pwd
        self.is_locked = True
        self.root.withdraw()
        self.prevent_sleep(True)
        self.create_blocker()
        self.install_hooks()
        self.trap_mouse()
        logger.info("通过快捷键激活系统优化")

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("系统优化助手 - 启动")
    logger.info("=" * 50)
    
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        logger.debug("DPI感知已设置")
    except Exception as e:
        logger.warning(f"DPI感知设置失败: {e}")
    
    try:
        root = tk.Tk()
        app = OfficeGuardApp(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
        messagebox.showerror("严重错误", f"应用异常：{e}\n请查看日志文件")
    finally:
        logger.info("应用已关闭")