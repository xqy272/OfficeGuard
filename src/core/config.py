"""
配置管理模块
处理应用程序配置的加载、保存和管理
"""

import json
from pathlib import Path
from typing import Any

from ..utils.paths import get_config_dir
from ..utils.crypto import encrypt_data, decrypt_data
from ..utils.logger import get_logger

logger = get_logger('config')


class ConfigManager:
    """配置管理器"""
    
    # 默认配置
    DEFAULTS = {
        # 密码设置
        "password": "000",
        
        # 定时器设置
        "timer_minutes": 60,
        "grace_seconds": 30,
        "mouse_threshold": 15,
        
        # 窗口设置
        "win_w": 1000,
        "win_h": 700,
        "win_x": -1,
        "win_y": -1,
        
        # 首次运行
        "first_run": True,
        
        # 快捷键设置
        "hotkey_enabled": True,
        "hotkey_ctrl": True,
        "hotkey_alt": True,
        "hotkey_shift": False,
        "hotkey_key": "L",
        
        # 开机自启动
        "autostart_enabled": False,
        
        # 自动登录
        "autologon_enabled": False,
        "autologon_username": "",
        "autologon_password": "",
        "autologon_domain": ".",
        
        # 启动软件列表
        "startup_apps": [],
        
        # UI主题
        "theme": "dark",
        "accent_color": "#3498db",
    }
    
    def __init__(self, filename: Path = None):
        """
        初始化配置管理器
        
        :param filename: 配置文件路径，默认为用户数据目录下的 config/guard_config.json
        """
        if filename is None:
            filename = get_config_dir() / 'guard_config.json'
        
        self.filename = Path(filename)
        self.data = self._load()
        self.is_first_run = self.data.get("first_run", True)
    
    def _load(self) -> dict:
        """加载配置文件"""
        if not self.filename.exists():
            logger.info("配置文件不存在，使用默认配置")
            return self.DEFAULTS.copy()
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # 检查是否是加密的配置文件
                if content.startswith('ENCRYPTED:'):
                    encrypted_data = content[10:]
                    decrypted_json = decrypt_data(encrypted_data)
                    
                    if decrypted_json:
                        saved = json.loads(decrypted_json)
                        logger.debug(f"加密配置已从 {self.filename} 加载并解密")
                    else:
                        logger.error("配置文件解密失败，使用默认配置")
                        return self.DEFAULTS.copy()
                else:
                    # 兼容旧的未加密配置文件
                    saved = json.loads(content)
                    logger.debug(f"配置已从 {self.filename} 加载（未加密）")
                    logger.info("检测到未加密的配置文件，将在下次保存时自动加密")
                
                # 合并缺省值
                for k, v in self.DEFAULTS.items():
                    if k not in saved:
                        saved[k] = v
                
                return saved
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            return self.DEFAULTS.copy()
    
    def save(self, encrypt: bool = True) -> bool:
        """
        保存配置文件
        
        :param encrypt: 是否加密保存
        :return: 是否保存成功
        """
        try:
            # 确保目录存在
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            
            # 将配置转换为JSON字符串
            json_str = json.dumps(self.data, indent=4, ensure_ascii=False)
            
            if encrypt:
                encrypted_data = encrypt_data(json_str)
                
                if encrypted_data:
                    with open(self.filename, 'w', encoding='utf-8') as f:
                        f.write(f"ENCRYPTED:{encrypted_data}")
                    logger.debug("配置已加密保存")
                    return True
                else:
                    logger.error("配置加密失败，保存为未加密格式")
                    with open(self.filename, 'w', encoding='utf-8') as f:
                        f.write(json_str)
                    return True
            else:
                with open(self.filename, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                logger.debug("配置已保存（未加密）")
                return True
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.data.get(key, self.DEFAULTS.get(key, default))
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.data[key] = value
    
    def mark_first_run_complete(self) -> None:
        """标记首次运行已完成"""
        self.set("first_run", False)
        self.save()
    
    def get_hotkey_display(self) -> str:
        """获取快捷键显示文本"""
        parts = []
        if self.get("hotkey_ctrl"):
            parts.append("Ctrl")
        if self.get("hotkey_alt"):
            parts.append("Alt")
        if self.get("hotkey_shift"):
            parts.append("Shift")
        parts.append(self.get("hotkey_key"))
        return "+".join(parts)
