"""
全局快捷键模块
使用 pynput 实现全局快捷键监听
"""

from typing import Callable, Set
from pynput import keyboard
from ..utils.logger import get_logger

logger = get_logger('hotkey')


class HotkeyManager:
    """全局快捷键管理器"""
    
    def __init__(self):
        self.enabled = True
        self.listener = None
        self.current_keys: Set = set()
        
        # 快捷键配置
        self.need_ctrl = True
        self.need_alt = True
        self.need_shift = False
        self.main_key = "L"
        self.main_key_vk = None
        
        # 回调
        self._on_trigger: Callable[[], None] = None
    
    def set_callback(self, on_trigger: Callable):
        """设置触发回调"""
        self._on_trigger = on_trigger
    
    def configure(self, ctrl: bool, alt: bool, shift: bool, key: str):
        """
        配置快捷键
        
        :param ctrl: 是否需要 Ctrl
        :param alt: 是否需要 Alt
        :param shift: 是否需要 Shift
        :param key: 主键
        """
        self.need_ctrl = ctrl
        self.need_alt = alt
        self.need_shift = shift
        self.main_key = key.upper()
        
        # 计算主键虚拟键码
        key_lower = key.lower()
        if len(key_lower) == 1 and key_lower.isalpha():
            self.main_key_vk = ord(key_lower.upper())
        elif key_lower.startswith('f') and len(key_lower) > 1:
            try:
                fn = int(key_lower[1:])
                if 1 <= fn <= 12:
                    self.main_key_vk = getattr(keyboard.Key, f'f{fn}')
            except:
                logger.error(f"无效的功能键: {key}")
    
    def start(self) -> bool:
        """启动快捷键监听"""
        if not self.enabled:
            logger.info("快捷键已禁用")
            return False
        
        if self.main_key_vk is None:
            logger.error("快捷键未配置")
            return False
        
        try:
            self.stop()
            self.current_keys.clear()
            
            def on_press(key):
                self.current_keys.add(key)
                if self._check_hotkey():
                    logger.info(f"快捷键 {self.get_display()} 被触发")
                    if self._on_trigger:
                        self._on_trigger()
            
            def on_release(key):
                self.current_keys.discard(key)
            
            self.listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.listener.start()
            
            import time
            time.sleep(0.1)
            
            if self.listener.is_alive():
                logger.info(f"全局快捷键 {self.get_display()} 已启动")
                return True
            else:
                logger.error("快捷键监听器启动失败")
                return False
        except Exception as e:
            logger.error(f"快捷键启动异常: {e}")
            return False
    
    def stop(self):
        """停止快捷键监听"""
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
                logger.info("快捷键监听已停止")
        except Exception as e:
            logger.error(f"快捷键停止异常: {e}")
    
    def _check_hotkey(self) -> bool:
        """检查当前按键是否匹配快捷键"""
        
        def is_modifier(key, mod_type):
            if mod_type == 'ctrl':
                return key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl)
            elif mod_type == 'alt':
                return key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt)
            elif mod_type == 'shift':
                return key in (keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.shift)
            return False
        
        has_ctrl = any(is_modifier(k, 'ctrl') for k in self.current_keys)
        has_alt = any(is_modifier(k, 'alt') for k in self.current_keys)
        has_shift = any(is_modifier(k, 'shift') for k in self.current_keys)
        
        ctrl_ok = (self.need_ctrl and has_ctrl) or (not self.need_ctrl and not has_ctrl)
        alt_ok = (self.need_alt and has_alt) or (not self.need_alt and not has_alt)
        shift_ok = (self.need_shift and has_shift) or (not self.need_shift and not has_shift)
        
        # 检查主键
        main_key_pressed = False
        for key in self.current_keys:
            if hasattr(key, 'vk') and key.vk == self.main_key_vk:
                main_key_pressed = True
                break
            elif key == self.main_key_vk:
                main_key_pressed = True
                break
        
        return ctrl_ok and alt_ok and shift_ok and main_key_pressed
    
    def get_display(self) -> str:
        """获取快捷键显示文本"""
        parts = []
        if self.need_ctrl:
            parts.append("Ctrl")
        if self.need_alt:
            parts.append("Alt")
        if self.need_shift:
            parts.append("Shift")
        parts.append(self.main_key)
        return "+".join(parts)
