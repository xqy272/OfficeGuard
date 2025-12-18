"""
系统锁定模块
实现系统锁定（隐形锁）功能
"""

import ctypes
from ctypes import wintypes
from typing import Callable
from ..utils.logger import get_logger

logger = get_logger('locker')

# Windows API 常量
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

# 钩子回调类型
HOOKPROC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)


class KBDLLHOOKSTRUCT(ctypes.Structure):
    """键盘钩子结构"""
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]


class RECT(ctypes.Structure):
    """矩形结构"""
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]


class SystemLocker:
    """系统锁定器"""
    
    def __init__(self):
        self.is_locked = False
        self.unlock_code = ""
        self.input_buffer = ""
        
        # Windows API
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # 钩子句柄
        self.h_kb_hook = None
        self.h_ms_hook = None
        self.kb_proc_ref = None
        self.ms_proc_ref = None
        
        # 回调
        self._on_unlock: Callable[[], None] = None
        self._on_key_input: Callable[[str], None] = None
    
    def set_callbacks(self, on_unlock: Callable = None, on_key_input: Callable = None):
        """设置回调函数"""
        self._on_unlock = on_unlock
        self._on_key_input = on_key_input
    
    def lock(self, password: str) -> bool:
        """
        锁定系统
        
        :param password: 解锁密码
        :return: 是否锁定成功
        """
        if self.is_locked:
            logger.warning("系统已处于锁定状态")
            return False
        
        if not password.isdigit() or len(password) < 3:
            logger.error("密码无效")
            return False
        
        self.unlock_code = password
        self.input_buffer = ""
        self.is_locked = True
        
        self._prevent_sleep(True)
        self._install_hooks()
        
        logger.info("系统已锁定")
        return True
    
    def unlock(self) -> bool:
        """解锁系统"""
        if not self.is_locked:
            return False
        
        self.is_locked = False
        
        # 释放鼠标
        self.user32.ClipCursor(None)
        
        # 卸载钩子
        self._uninstall_hooks()
        
        # 允许睡眠
        self._prevent_sleep(False)
        
        if self._on_unlock:
            self._on_unlock()
        
        logger.info("系统已解锁")
        return True
    
    def process_key(self, char: str):
        """
        处理按键输入
        
        :param char: 输入的字符
        """
        if not self.is_locked:
            return
        
        self.input_buffer += char
        self.input_buffer = self.input_buffer[-len(self.unlock_code):]
        
        if self._on_key_input:
            self._on_key_input(char)
        
        if self.input_buffer == self.unlock_code:
            self.unlock()
    
    def trap_mouse(self):
        """困禁鼠标到屏幕中心"""
        if not self.is_locked:
            return
        
        try:
            sw = self.user32.GetSystemMetrics(0)
            sh = self.user32.GetSystemMetrics(1)
            cx, cy = sw // 2, sh // 2
            
            rect = RECT(cx, cy, cx + 1, cy + 1)
            self.user32.ClipCursor(ctypes.byref(rect))
        except Exception as e:
            logger.warning(f"鼠标困禁失败: {e}")
    
    def _install_hooks(self):
        """安装全局钩子"""
        
        def kb_callback(nCode, wParam, lParam):
            try:
                if nCode == 0 and (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN):
                    kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                    vk = kb.vkCode
                    
                    # 数字键处理
                    if 48 <= vk <= 57:  # 主键盘 0-9
                        self.process_key(chr(vk))
                        return 1
                    elif 96 <= vk <= 105:  # 小键盘 0-9
                        self.process_key(str(vk - 96))
                        return 1
                    
                    return 1  # 屏蔽其他按键
                return 0
            except Exception as e:
                logger.error(f"键盘钩子异常: {e}")
                return 0
        
        def ms_callback(nCode, wParam, lParam):
            try:
                if nCode >= 0:
                    return 1  # 屏蔽鼠标
                return 0
            except Exception as e:
                logger.error(f"鼠标钩子异常: {e}")
                return 0
        
        try:
            self.kb_proc_ref = HOOKPROC(kb_callback)
            self.ms_proc_ref = HOOKPROC(ms_callback)
            
            self.h_kb_hook = self.user32.SetWindowsHookExA(
                WH_KEYBOARD_LL, self.kb_proc_ref, 0, 0
            )
            self.h_ms_hook = self.user32.SetWindowsHookExA(
                WH_MOUSE_LL, self.ms_proc_ref, 0, 0
            )
            
            if self.h_kb_hook and self.h_ms_hook:
                logger.info("钩子已安装")
            else:
                logger.error("钩子安装失败")
        except Exception as e:
            logger.error(f"钩子安装异常: {e}")
    
    def _uninstall_hooks(self):
        """卸载全局钩子"""
        try:
            if self.h_kb_hook:
                self.user32.UnhookWindowsHookEx(self.h_kb_hook)
                self.h_kb_hook = None
            
            if self.h_ms_hook:
                self.user32.UnhookWindowsHookEx(self.h_ms_hook)
                self.h_ms_hook = None
            
            self.kb_proc_ref = None
            self.ms_proc_ref = None
            
            logger.info("钩子已卸载")
        except Exception as e:
            logger.error(f"钩子卸载异常: {e}")
    
    def _prevent_sleep(self, enable: bool):
        """阻止/允许系统睡眠"""
        if enable:
            flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        else:
            flags = ES_CONTINUOUS
        
        self.kernel32.SetThreadExecutionState(flags)
    
    def cleanup(self):
        """清理资源"""
        if self.is_locked:
            self.unlock()
