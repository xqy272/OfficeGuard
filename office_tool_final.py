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

# Windows API
import ctypes
from ctypes import wintypes

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
        level=logging.INFO,
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
            "first_run": True  # 首次运行标志
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
        self.root.title("OfficeGuard - 办公室全能卫士 v1.0.0")
        
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
        
        # 注册退出处理器
        atexit.register(self.cleanup_on_exit)

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 首次运行引导（在UI完成后显示）
        if self.cfg.is_first_run:
            self.root.after(500, self.show_first_run_guide)

    def show_first_run_guide(self):
        """显示首次运行引导"""
        try:
            app_dir = get_app_data_dir()
            msg = (
                f"🎉 欢迎使用办公室全能卫士！\n\n"
                f"📁 数据存储位置：\n{app_dir}\n\n"
                f"包含以下文件夹：\n"
                f"  • logs\\     - 日志文件\n"
                f"  • config\\   - 配置文件\n\n"
                f"💡 功能说明：\n"
                f"  • 定时任务：设置定时关机/睡眠\n"
                f"  • 隐形卫士：完全锁定键盘鼠标\n\n"
                f"⚠️ 安全提示：\n"
                f"  • 本软件需要管理员权限\n"
                f"  • 关机任务随时可取消\n"
                f"  • 锁定后必须输入密码解锁\n"
            )
            
            result = messagebox.showinfo(
                "首次运行引导",
                msg,
                parent=self.root
            )
            
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
        
        notebook.add(self.tab_timer, text=" ⏱️ 定时任务 ")
        notebook.add(self.tab_stealth, text=" 🛡️ 隐形卫士 ")
        
        self.setup_timer_ui()
        self.setup_stealth_ui()

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
        tk.Label(pwd_frame, text="解锁密码 (纯数字):").pack(side=tk.LEFT)
        self.entry_pwd = ttk.Entry(pwd_frame, width=12, justify="center", show="*")
        self.entry_pwd.pack(side=tk.LEFT, padx=5)
        self.entry_pwd.insert(0, str(self.cfg.get("password")))
        
        # 显示/隐藏密码切换按钮
        self.show_pwd_btn = tk.Button(pwd_frame, text="👁️", width=3, relief="groove",
                                       command=self.toggle_password_visibility)
        self.show_pwd_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Label(self.tab_stealth, text="🛡️ 内核级屏蔽", font=("微软雅黑", 14, "bold"), fg="#e74c3c").pack(pady=10)
        info = (
            "✅ 屏蔽 Win键 / Alt+Tab / Win+Tab\n"
            "✅ 物理限制鼠标范围\n"
            "激活后：屏幕常亮，键鼠“失灵”\n"
            "解锁方式：盲打上方设置的密码"
        )
        tk.Label(self.tab_stealth, text=info, justify="left", bg="#fff", padx=15, pady=15, relief="sunken").pack(fill="both", expand=True)
        tk.Button(self.tab_stealth, text="⚡ 立即锁死系统", bg="#2c3e50", fg="white", 
                  font=("微软雅黑", 12, "bold"), height=2,
                  command=self.lock_system).pack(side=tk.BOTTOM, fill="x", pady=20)
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        current_show = self.entry_pwd.cget('show')
        if current_show == '*':
            self.entry_pwd.config(show="")
            self.show_pwd_btn.config(text="🙈")
        else:
            self.entry_pwd.config(show="*")
            self.show_pwd_btn.config(text="👁️")

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
        self.root.withdraw()
        self.prevent_sleep(True)
        self.create_blocker()
        self.install_hooks()
        self.trap_mouse()
        logger.info("系统已锁定")

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
        logger.info("系统已解锁")
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
        
        try:
            self.root.deiconify()
        except:
            pass
        
        messagebox.showinfo("成功", "控制权已恢复")

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
        """窗口关闭事件处理"""
        # 如果有运行中的定时器，询问用户
        if self.timer_running or self.in_grace_period:
            result = messagebox.askokcancel(
                "退出确认", 
                "⚠️ 检测到正在运行的定时任务！\n\n"
                "确定要退出吗？任务将被取消。\n"
                "（关闭此程序可安全取消所有操作）"
            )
            if not result:
                return
            
            # 强制取消定时器
            logger.info("用户确认退出，取消所有任务")
            self.action_executed = True  # 防止执行关机/睡眠
            self.cancel_timer_manual()
        
        # 如果系统被锁定，不允许直接关闭
        if self.is_locked:
            messagebox.showwarning(
                "无法关闭",
                "系统已锁定，无法直接关闭窗口\n请使用密码解锁后再关闭"
            )
            return
        
        # 执行清理
        self.cleanup_on_exit()
        self.root.destroy()

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("办公室全能卫士 - 启动")
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