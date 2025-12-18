# 标准库导入
import os
import sys
import time
import json
import math
import logging
import atexit
import base64
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
#      3. 配置文件加密
# ==========================================
def encrypt_data(data_str):
    """
    使用Windows DPAPI加密数据
    DPAPI（Data Protection API）使用用户凭据加密，只有当前用户可以解密
    :param data_str: 要加密的字符串
    :return: Base64编码的加密数据
    """
    try:
        import ctypes
        from ctypes import wintypes
        
        # 定义DPAPI结构
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [
                ('cbData', wintypes.DWORD),
                ('pbData', ctypes.POINTER(ctypes.c_char))
            ]
        
        # 转换为字节
        data_bytes = data_str.encode('utf-8')
        
        # 输入数据
        blob_in = DATA_BLOB()
        blob_in.cbData = len(data_bytes)
        blob_in.pbData = ctypes.cast(ctypes.c_char_p(data_bytes), ctypes.POINTER(ctypes.c_char))
        
        # 输出数据
        blob_out = DATA_BLOB()
        
        # 调用CryptProtectData
        crypt32 = ctypes.windll.crypt32
        if crypt32.CryptProtectData(
            ctypes.byref(blob_in),
            None,  # 描述
            None,  # 可选熵
            None,  # 保留
            None,  # 提示结构
            0,     # 标志
            ctypes.byref(blob_out)
        ):
            # 获取加密数据
            encrypted_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            # 释放内存
            kernel32.LocalFree(blob_out.pbData)
            # Base64编码
            return base64.b64encode(encrypted_bytes).decode('ascii')
        else:
            logger.error("加密失败")
            return None
    except Exception as e:
        logger.error(f"数据加密异常: {e}")
        return None

def decrypt_data(encrypted_str):
    """
    使用Windows DPAPI解密数据
    :param encrypted_str: Base64编码的加密数据
    :return: 解密后的字符串
    """
    try:
        import ctypes
        from ctypes import wintypes
        
        # 定义DPAPI结构
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [
                ('cbData', wintypes.DWORD),
                ('pbData', ctypes.POINTER(ctypes.c_char))
            ]
        
        # Base64解码
        encrypted_bytes = base64.b64decode(encrypted_str)
        
        # 输入数据
        blob_in = DATA_BLOB()
        blob_in.cbData = len(encrypted_bytes)
        blob_in.pbData = ctypes.cast(ctypes.c_char_p(encrypted_bytes), ctypes.POINTER(ctypes.c_char))
        
        # 输出数据
        blob_out = DATA_BLOB()
        
        # 调用CryptUnprotectData
        crypt32 = ctypes.windll.crypt32
        if crypt32.CryptUnprotectData(
            ctypes.byref(blob_in),
            None,  # 描述
            None,  # 可选熵
            None,  # 保留
            None,  # 提示结构
            0,     # 标志
            ctypes.byref(blob_out)
        ):
            # 获取解密数据
            decrypted_bytes = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            # 释放内存
            kernel32.LocalFree(blob_out.pbData)
            # 转换为字符串
            return decrypted_bytes.decode('utf-8')
        else:
            logger.error("解密失败")
            return None
    except Exception as e:
        logger.error(f"数据解密异常: {e}")
        return None

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
            "hotkey_key": "L",  # 主键
            "autostart_enabled": False,  # 开机自启动
            "autologon_enabled": False,  # 自动登录
            "autologon_username": "",  # 自动登录用户名
            "autologon_password": "",  # 自动登录密码
            "autologon_domain": ".",  # 自动登录域名（.表示本机）
            "startup_apps": []  # 开机启动的软件列表 [{"name": "软件名", "path": "路径", "enabled": True}]
        }
        self.data = self.load()
        
        # 检查是否首次运行
        self.is_first_run = self.data.get("first_run", True)
    
    def mark_first_run_complete(self):
        """标记首次运行已完成"""
        self.set("first_run", False)
        self.save()

    def load(self):
        """加载配置文件（支持加密）"""
        if not os.path.exists(self.filename):
            logger.info("配置文件不存在，使用默认配置")
            return self.defaults.copy()
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # 检查是否是加密的配置文件
                if content.startswith('ENCRYPTED:'):
                    # 加密格式：ENCRYPTED:base64_encrypted_data
                    encrypted_data = content[10:]  # 去掉"ENCRYPTED:"前缀
                    decrypted_json = decrypt_data(encrypted_data)
                    
                    if decrypted_json:
                        saved = json.loads(decrypted_json)
                        logger.debug(f"加密配置已从 {self.filename} 加载并解密")
                    else:
                        logger.error("配置文件解密失败，使用默认配置")
                        return self.defaults.copy()
                else:
                    # 兼容旧的未加密配置文件
                    saved = json.loads(content)
                    logger.debug(f"配置已从 {self.filename} 加载（未加密）")
                    # 标记需要升级为加密格式
                    logger.info("检测到未加密的配置文件，将在下次保存时自动加密")
                
                # 合并缺省值
                for k, v in self.defaults.items():
                    if k not in saved:
                        saved[k] = v
                
                return saved
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            return self.defaults.copy()

    def save(self, encrypt=True):
        """
        保存配置文件
        :param encrypt: 是否加密保存（默认True）
        """
        try:
            # 将配置转换为JSON字符串
            json_str = json.dumps(self.data, indent=4, ensure_ascii=False)
            
            if encrypt:
                # 加密配置数据
                encrypted_data = encrypt_data(json_str)
                
                if encrypted_data:
                    # 保存加密数据（添加标识前缀）
                    with open(self.filename, 'w', encoding='utf-8') as f:
                        f.write(f"ENCRYPTED:{encrypted_data}")
                    logger.debug("配置已加密保存")
                else:
                    logger.error("配置加密失败，保存为未加密格式")
                    # 降级为未加密保存
                    with open(self.filename, 'w', encoding='utf-8') as f:
                        f.write(json_str)
            else:
                # 未加密保存（仅用于调试）
                with open(self.filename, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                logger.debug("配置已保存（未加密）")
                
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
#      开机检测与自启动管理
# ==========================================
def is_system_boot():
    """
    判断是否是系统开机启动（而非睡眠唤醒或正常启动）
    方法1：检查是否设置了 --boot-startup 命令行参数（由注册表启动）
    方法2：检查系统运行时间，如果小于3分钟，认为是开机（降级方案）
    """
    try:
        # 方法1：检查命令行参数标志（最准确）
        # 当通过注册表开机启动时，使用 --boot-startup 参数启动
        if '--boot-startup' in sys.argv:
            logger.info("检测到开机启动标志（命令行参数: --boot-startup）")
            return True
        
        # 方法2：检查系统运行时间（备用方案）
        tick_count = kernel32.GetTickCount64()
        uptime_minutes = tick_count / 1000 / 60
        logger.info(f"系统运行时间: {uptime_minutes:.2f} 分钟")
        
        # 系统运行时间小于3分钟，认为是开机
        if uptime_minutes < 3:
            logger.info("检测到开机启动（运行时间<3分钟）")
            return True
        
        logger.info("检测为正常启动（非开机启动）")
        return False
    except Exception as e:
        logger.error(f"检测系统启动时间失败: {e}")
        return False

def set_autostart(enable, app_path=None):
    """
    使用Windows任务计划程序设置开机自启动（绕过UAC限制）
    :param enable: True=启用, False=禁用
    :param app_path: 应用程序路径，如果为None则使用当前exe路径
    """
    try:
        import subprocess
        
        # 获取应用程序路径
        if app_path is None:
            if is_frozen():
                app_path = sys.executable
            else:
                app_path = os.path.abspath(__file__)
        
        # 验证路径是否存在
        if not os.path.exists(app_path):
            logger.error(f"应用程序路径不存在: {app_path}")
            return False
        
        # 转换为规范路径
        app_path = os.path.abspath(app_path)
        task_name = "OfficeGuard_AutoStart"
        
        if enable:
            # 创建任务计划程序
            logger.info(f"正在创建任务计划: {task_name}")
            
            # 先删除旧任务（如果存在）
            try:
                subprocess.run(
                    ['schtasks', '/Delete', '/TN', task_name, '/F'],
                    capture_output=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except:
                pass
            
            # 创建新任务
            # /SC ONLOGON: 用户登录时触发
            # /TR: 要执行的程序和参数
            # /RL HIGHEST: 使用最高权限运行
            # /F: 强制创建（覆盖已存在的任务）
            cmd = [
                'schtasks',
                '/Create',
                '/TN', task_name,
                '/TR', f'"{app_path}" --boot-startup',
                '/SC', 'ONLOGON',
                '/RL', 'HIGHEST',
                '/F'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                logger.info(f"任务计划创建成功: {task_name}")
                logger.info(f"启动命令: {app_path} --boot-startup")
                return True
            else:
                logger.error(f"创建任务计划失败: {result.stderr}")
                return False
        else:
            # 删除任务计划
            logger.info(f"正在删除任务计划: {task_name}")
            
            cmd = [
                'schtasks',
                '/Delete',
                '/TN', task_name,
                '/F'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                logger.info(f"任务计划已删除: {task_name}")
                return True
            elif 'ERROR: The system cannot find' in result.stderr:
                logger.info("任务计划不存在，无需删除")
                return True
            else:
                logger.warning(f"删除任务计划时出现警告: {result.stderr}")
                return True  # 即使出错也返回True，因为目标是禁用
    except Exception as e:
        logger.error(f"设置开机自启动失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def check_autostart_status():
    """
    检查任务计划程序中的开机自启动状态
    返回: (是否启用, 任务信息, 问题列表)
    """
    try:
        import subprocess
        
        task_name = "OfficeGuard_AutoStart"
        problems = []
        
        # 查询任务计划
        cmd = [
            'schtasks',
            '/Query',
            '/TN', task_name,
            '/FO', 'LIST',
            '/V'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            # 任务存在，解析输出
            output = result.stdout
            
            # 提取任务状态
            task_info = f"任务计划: {task_name}"
            
            # 检查是否启用
            if '已禁用' in output or 'Disabled' in output:
                problems.append("任务已创建但被禁用")
            
            # 检查执行路径
            import re
            match = re.search(r'要执行的操作:.*?([A-Za-z]:\\[^\r\n]+)', output)
            if not match:
                match = re.search(r'Task To Run:.*?([A-Za-z]:\\[^\r\n]+)', output)
            
            if match:
                exe_path = match.group(1).strip()
                task_info = exe_path
                
                # 检查文件是否存在
                if '"' in exe_path:
                    exe_path = exe_path.split('"')[1]
                else:
                    exe_path = exe_path.split()[0]
                
                if not os.path.exists(exe_path):
                    problems.append(f"EXE文件不存在: {exe_path}")
                
                # 检查是否有--boot-startup参数
                if "--boot-startup" not in match.group(1):
                    problems.append("缺少--boot-startup参数")
            
            return (True, task_info, problems)
        else:
            # 任务不存在
            return (False, None, ["任务计划不存在"])
            
    except Exception as e:
        logger.error(f"检查任务计划状态失败: {e}")
        return (False, None, [f"检查失败: {e}"])

def download_autologon():
    """
    下载Sysinternals Autologon工具
    返回Autologon.exe的路径
    """
    try:
        import urllib.request
        import zipfile
        import tempfile
        
        app_dir = get_app_data_dir()
        tools_dir = app_dir / 'tools'
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        autologon_exe = tools_dir / 'Autologon.exe'
        
        # 如果已存在，直接返回
        if autologon_exe.exists():
            logger.info(f"Autologon工具已存在: {autologon_exe}")
            return str(autologon_exe)
        
        # 下载Autologon
        logger.info("正在下载Sysinternals Autologon...")
        url = "https://live.sysinternals.com/Autologon.exe"
        
        # 下载到临时文件
        temp_file = tools_dir / 'Autologon.exe.tmp'
        urllib.request.urlretrieve(url, str(temp_file))
        
        # 重命名为正式文件
        temp_file.rename(autologon_exe)
        
        logger.info(f"Autologon工具下载完成: {autologon_exe}")
        return str(autologon_exe)
        
    except Exception as e:
        logger.error(f"下载Autologon工具失败: {e}")
        return None

def set_autologon(enable, username="", password="", domain="."):
    """
    使用Sysinternals Autologon设置Windows自动登录
    使用LSA加密存储密码，比直接写注册表更安全
    需要管理员权限
    :param enable: True=启用, False=禁用
    :param username: 用户名
    :param password: 密码
    :param domain: 域名，默认为本机（.）
    """
    try:
        import subprocess
        
        # 获取或下载Autologon工具
        autologon_path = download_autologon()
        
        if not autologon_path:
            logger.error("无法获取Autologon工具")
            return False
        
        if enable:
            # 启用自动登录
            # Autologon.exe username domain password /accepteula
            cmd = [
                autologon_path,
                username,
                domain,
                password,
                '/accepteula'  # 自动接受许可协议
            ]
            
            logger.info(f"正在配置自动登录，用户名: {username}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW  # 不显示窗口
            )
            
            if result.returncode == 0:
                logger.info("自动登录已启用（使用LSA加密）")
                return True
            else:
                logger.error(f"Autologon执行失败: {result.stderr}")
                return False
        else:
            # 禁用自动登录
            # 方法1: 使用Autologon工具禁用
            logger.info("正在禁用自动登录")
            
            # Autologon.exe /delete 可以删除所有自动登录设置
            cmd = [autologon_path, '/delete', '/accepteula']
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                logger.info("已使用Autologon禁用自动登录")
            except Exception as e:
                logger.warning(f"Autologon禁用失败: {e}，尝试手动清理")
            
            # 方法2: 手动清理注册表（确保完全清除）
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
            
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
                )
                
                # 禁用自动登录
                winreg.SetValueEx(key, "AutoAdminLogon", 0, winreg.REG_SZ, "0")
                
                # 清理可能存在的明文密码
                try:
                    winreg.DeleteValue(key, "DefaultPassword")
                except:
                    pass
                
                winreg.CloseKey(key)
                logger.info("自动登录已禁用")
                return True
            except Exception as e:
                logger.error(f"禁用自动登录失败: {e}")
                return False
        
    except Exception as e:
        logger.error(f"设置自动登录失败: {e}")
        return False

def launch_startup_apps(app_list):
    """
    启动指定的应用程序列表
    仅在开机启动时执行，普通启动不生效
    :param app_list: 应用程序列表 [{"name": "软件名", "path": "路径", "enabled": True}]
    """
    import subprocess
    
    launched = []
    failed = []
    
    for app in app_list:
        if not app.get("enabled", True):
            continue
        
        app_path = app.get("path", "")
        app_name = app.get("name", "未知")
        
        if not app_path or not os.path.exists(app_path):
            logger.warning(f"应用程序不存在: {app_name} - {app_path}")
            failed.append(app_name)
            continue
        
        try:
            # 启动应用程序
            subprocess.Popen([app_path], shell=True)
            logger.info(f"已启动应用程序: {app_name}")
            launched.append(app_name)
            # 延迟一下，避免同时启动太多程序
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"启动应用程序失败: {app_name} - {e}")
            failed.append(app_name)
    
    return launched, failed

def remove_boot_startup_args():
    """
    清除启动参数中的 --boot-startup 标志
    防止在重新启动或重新打开窗口时误认为是开机启动
    """
    try:
        if '--boot-startup' in sys.argv:
            sys.argv.remove('--boot-startup')
            logger.info("已清除 --boot-startup 参数")
    except Exception as e:
        logger.debug(f"清除启动参数时出错: {e}")

# ==========================================
#      主程序逻辑
# ==========================================
class OfficeGuardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("系统优化助手 v1.3.2")
        
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
        
        # 清除启动参数，防止后续重新启动时误判
        remove_boot_startup_args()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 安装全局快捷键
        self.install_global_hotkey()
        
        # 创建系统托盘并隐藏窗口
        self.root.after(100, self.setup_tray_and_hide)
        
        # 检测是否是开机启动
        self.is_boot_startup = is_system_boot()
        
        # 首次运行引导（在托盘创建后显示）
        if self.cfg.is_first_run:
            self.root.after(1000, self.show_first_run_guide)
        
        # 如果是开机启动，执行开机任务
        if self.is_boot_startup:
            self.root.after(2000, self.on_boot_startup)

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
                f"  • 配置文件已使用DPAPI加密保护\n"
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
        # 创建滚动区域
        canvas = tk.Canvas(self.tab_settings)
        scrollbar = ttk.Scrollbar(self.tab_settings, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 开机自启动设置
        autostart_frame = tk.LabelFrame(scrollable_frame, text="开机设置", padx=15, pady=15)
        autostart_frame.pack(fill="x", pady=10, padx=10)
        
        self.var_autostart = tk.BooleanVar(value=self.cfg.get("autostart_enabled"))
        tk.Checkbutton(autostart_frame, text="开机自动启动本程序", variable=self.var_autostart).pack(anchor="w", pady=5)
        
        # AutoLogon设置
        autologon_frame = tk.LabelFrame(autostart_frame, text="自动登录设置（需管理员权限）", padx=10, pady=10)
        autologon_frame.pack(fill="x", pady=10)
        
        self.var_autologon = tk.BooleanVar(value=self.cfg.get("autologon_enabled"))
        tk.Checkbutton(autologon_frame, text="启用开机自动登录（使用Sysinternals Autologon）", 
                      variable=self.var_autologon).pack(anchor="w", pady=5)
        
        # 用户名
        user_frame = tk.Frame(autologon_frame)
        user_frame.pack(fill="x", pady=5)
        tk.Label(user_frame, text="用户名:", width=10, anchor="e").pack(side=tk.LEFT)
        self.entry_autologon_user = ttk.Entry(user_frame, width=20)
        self.entry_autologon_user.pack(side=tk.LEFT, padx=5)
        self.entry_autologon_user.insert(0, self.cfg.get("autologon_username"))
        
        # 密码
        pwd_frame = tk.Frame(autologon_frame)
        pwd_frame.pack(fill="x", pady=5)
        tk.Label(pwd_frame, text="密码:", width=10, anchor="e").pack(side=tk.LEFT)
        self.entry_autologon_pwd = ttk.Entry(pwd_frame, width=20, show="*")
        self.entry_autologon_pwd.pack(side=tk.LEFT, padx=5)
        self.entry_autologon_pwd.insert(0, self.cfg.get("autologon_password"))
        
        # 域名（可选）
        domain_frame = tk.Frame(autologon_frame)
        domain_frame.pack(fill="x", pady=5)
        tk.Label(domain_frame, text="域名:", width=10, anchor="e").pack(side=tk.LEFT)
        self.entry_autologon_domain = ttk.Entry(domain_frame, width=20)
        self.entry_autologon_domain.pack(side=tk.LEFT, padx=5)
        domain_value = self.cfg.get("autologon_domain")
        if not domain_value:
            domain_value = "."
        self.entry_autologon_domain.insert(0, domain_value)
        tk.Label(domain_frame, text="(本机用户填 . 即可)", fg="gray", font=("微软雅黑", 8)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(autologon_frame, text="✅ 使用LSA加密存储密码，安全可靠\n⚠️ 首次使用会自动下载Sysinternals Autologon工具", 
                fg="green", font=("微软雅黑", 8), justify="left").pack(anchor="w", pady=5)
        
        # 保存开机设置按钮
        tk.Button(autostart_frame, text="💾 保存开机设置", bg="#27ae60", fg="white",
                 command=self.save_autostart_settings).pack(fill="x", pady=10)
        
        # 启动软件列表管理
        startup_apps_frame = tk.LabelFrame(scrollable_frame, text="开机启动软件管理", padx=15, pady=15)
        startup_apps_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        # 软件列表
        list_frame = tk.Frame(startup_apps_frame)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # 创建列表和滚动条
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical")
        self.startup_apps_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=list_scroll.set)
        list_scroll.config(command=self.startup_apps_listbox.yview)
        self.startup_apps_listbox.pack(side="left", fill="both", expand=True)
        list_scroll.pack(side="right", fill="y")
        
        # 加载已有的软件列表
        self.refresh_startup_apps_list()
        
        # 按钮区域
        btn_frame = tk.Frame(startup_apps_frame)
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="➕ 添加软件", command=self.add_startup_app).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="✏️ 编辑", command=self.edit_startup_app).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="🗑️ 删除", command=self.remove_startup_app).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="🔄 切换启用/禁用", command=self.toggle_startup_app).pack(side=tk.LEFT, padx=2)
        
        # 快捷键设置
        hotkey_frame = tk.LabelFrame(scrollable_frame, text="快捷键设置", padx=15, pady=15)
        hotkey_frame.pack(fill="x", pady=10, padx=10)
        
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
                # 不处理的情况，传递给下一个钩子
                return 0
            except Exception as e:
                logger.error(f"键盘钩子异常: {e}")
                # 发生错误时也要返回0而不是调用CallNextHookEx
                return 0

        def ms_callback(nCode, wParam, lParam):
            try:
                if nCode >= 0:
                    return 1  # 屏蔽所有鼠标事件
                return 0
            except Exception as e:
                logger.error(f"鼠标钩子异常: {e}")
                return 0

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
    
    def on_boot_startup(self):
        """处理开机启动任务"""
        logger.info("检测到系统开机，执行开机任务...")
        
        try:
            # 检查开机自启动是否启用
            autostart_enabled = self.cfg.get("autostart_enabled")
            if not autostart_enabled:
                logger.info("开机自启动已禁用，跳过开机任务")
                return
            
            # 获取启动软件列表
            startup_apps = self.cfg.get("startup_apps")
            
            if startup_apps:
                logger.info(f"准备启动 {len(startup_apps)} 个应用程序...")
                launched, failed = launch_startup_apps(startup_apps)
                
                # 显示启动结果（可选）
                if launched or failed:
                    msg = ""
                    if launched:
                        msg += f"✅ 已启动: {', '.join(launched)}\n"
                    if failed:
                        msg += f"❌ 启动失败: {', '.join(failed)}"
                    
                    logger.info(f"开机启动结果: {msg}")
            else:
                logger.info("没有配置开机启动软件")
        except Exception as e:
            logger.error(f"开机启动任务执行失败: {e}")
    
    def save_autostart_settings(self):
        """保存开机设置"""
        try:
            # 保存开机自启动
            autostart_enabled = self.var_autostart.get()
            result = set_autostart(autostart_enabled)
            
            if result:
                self.cfg.set("autostart_enabled", autostart_enabled)
                
                # 诊断开机自启动状态
                if autostart_enabled:
                    enabled, reg_value, problems = check_autostart_status()
                    if problems:
                        warning_msg = "⚠️ 开机自启动可能存在问题：\n\n"
                        for problem in problems:
                            warning_msg += f"• {problem}\n"
                        warning_msg += f"\n注册表值: {reg_value}\n\n"
                        warning_msg += "建议：\n"
                        warning_msg += "1. 将程序复制到非OneDrive路径（如C:\\Program Files）\n"
                        warning_msg += "2. 避免使用中文路径\n"
                        warning_msg += "3. 重新设置开机自启动"
                        logger.warning(f"开机自启动问题: {problems}")
                        messagebox.showwarning("开机自启动警告", warning_msg)
                
                # 保存AutoLogon设置
                autologon_enabled = self.var_autologon.get()
                username = self.entry_autologon_user.get().strip()
                password = self.entry_autologon_pwd.get().strip()
                domain = self.entry_autologon_domain.get().strip() or "."
                
                if autologon_enabled:
                    if not username:
                        messagebox.showwarning("警告", "请输入用户名")
                        return
                    
                    if not password:
                        messagebox.showwarning("警告", "请输入密码")
                        return
                    
                    # 显示进度提示
                    progress_msg = messagebox.showinfo("提示", "正在配置自动登录...\n首次使用会下载Autologon工具（约200KB）")
                    
                    result = set_autologon(True, username, password, domain)
                    if result:
                        self.cfg.set("autologon_enabled", True)
                        self.cfg.set("autologon_username", username)
                        self.cfg.set("autologon_password", password)
                        self.cfg.set("autologon_domain", domain)
                        messagebox.showinfo("成功", "开机设置已保存！\n自动登录已启用（LSA加密存储）。")
                    else:
                        messagebox.showerror("错误", "自动登录设置失败！\n请确保：\n1. 以管理员权限运行\n2. 网络连接正常（首次需下载工具）\n3. 用户名和密码正确")
                        return
                else:
                    # 禁用自动登录
                    set_autologon(False)
                    self.cfg.set("autologon_enabled", False)
                    messagebox.showinfo("成功", "开机设置已保存！\n自动登录已禁用。")
                
                self.cfg.save()
                logger.info(f"开机设置已保存: 自启动={autostart_enabled}, 自动登录={autologon_enabled}")
            else:
                messagebox.showerror("错误", "开机自启动设置失败！")
        except Exception as e:
            logger.error(f"保存开机设置失败: {e}")
            messagebox.showerror("错误", f"保存失败：{e}")
    
    def refresh_startup_apps_list(self):
        """刷新启动软件列表显示"""
        self.startup_apps_listbox.delete(0, tk.END)
        startup_apps = self.cfg.get("startup_apps")
        
        for app in startup_apps:
            name = app.get("name", "未知")
            enabled = app.get("enabled", True)
            status = "✓" if enabled else "✗"
            self.startup_apps_listbox.insert(tk.END, f"{status} {name}")
    
    def add_startup_app(self):
        """添加启动软件"""
        from tkinter import filedialog
        
        # 选择文件
        file_path = filedialog.askopenfilename(
            title="选择要启动的软件",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        
        if file_path:
            # 获取文件名
            name = os.path.basename(file_path)
            
            # 添加到列表
            startup_apps = self.cfg.get("startup_apps")
            startup_apps.append({
                "name": name,
                "path": file_path,
                "enabled": True
            })
            
            self.cfg.set("startup_apps", startup_apps)
            self.cfg.save()
            
            self.refresh_startup_apps_list()
            logger.info(f"已添加启动软件: {name}")
    
    def edit_startup_app(self):
        """编辑启动软件"""
        selection = self.startup_apps_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要编辑的软件")
            return
        
        index = selection[0]
        startup_apps = self.cfg.get("startup_apps")
        app = startup_apps[index]
        
        # 创建编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑启动软件")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="软件名称:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        entry_name = ttk.Entry(dialog, width=30)
        entry_name.grid(row=0, column=1, padx=10, pady=10)
        entry_name.insert(0, app.get("name", ""))
        
        tk.Label(dialog, text="软件路径:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        entry_path = ttk.Entry(dialog, width=30)
        entry_path.grid(row=1, column=1, padx=10, pady=10)
        entry_path.insert(0, app.get("path", ""))
        
        def browse():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="选择软件",
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if file_path:
                entry_path.delete(0, tk.END)
                entry_path.insert(0, file_path)
        
        tk.Button(dialog, text="浏览", command=browse).grid(row=1, column=2, padx=5)
        
        def save():
            name = entry_name.get().strip()
            path = entry_path.get().strip()
            
            if not name or not path:
                messagebox.showwarning("警告", "名称和路径不能为空")
                return
            
            startup_apps[index]["name"] = name
            startup_apps[index]["path"] = path
            
            self.cfg.set("startup_apps", startup_apps)
            self.cfg.save()
            self.refresh_startup_apps_list()
            
            dialog.destroy()
            logger.info(f"已更新启动软件: {name}")
        
        tk.Button(dialog, text="保存", command=save, bg="#27ae60", fg="white").grid(row=2, column=1, pady=20)
    
    def remove_startup_app(self):
        """删除启动软件"""
        selection = self.startup_apps_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的软件")
            return
        
        index = selection[0]
        startup_apps = self.cfg.get("startup_apps")
        app = startup_apps[index]
        
        result = messagebox.askyesno("确认", f"确定要删除 {app.get('name', '未知')} 吗？")
        if result:
            startup_apps.pop(index)
            self.cfg.set("startup_apps", startup_apps)
            self.cfg.save()
            self.refresh_startup_apps_list()
            logger.info(f"已删除启动软件: {app.get('name', '未知')}")
    
    def toggle_startup_app(self):
        """切换启动软件的启用/禁用状态"""
        selection = self.startup_apps_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要切换的软件")
            return
        
        index = selection[0]
        startup_apps = self.cfg.get("startup_apps")
        app = startup_apps[index]
        
        # 切换状态
        app["enabled"] = not app.get("enabled", True)
        
        self.cfg.set("startup_apps", startup_apps)
        self.cfg.save()
        self.refresh_startup_apps_list()
        
        status = "启用" if app["enabled"] else "禁用"
        logger.info(f"已{status}启动软件: {app.get('name', '未知')}")

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