"""
路径管理模块
处理应用程序数据目录、可执行文件路径等
"""

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    """
    检测是否运行在打包的exe环境中
    PyInstaller: hasattr(sys, '_MEIPASS')
    cx_Freeze: hasattr(sys, 'frozen')
    """
    return getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS')


def get_app_data_dir() -> Path:
    """
    获取应用数据目录
    打包为exe后使用: C:\\Users\\{用户}\\AppData\\Local\\OfficeGuard
    开发环境也使用相同路径，确保行为一致
    """
    base_dir = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~')))
    app_dir = base_dir / 'OfficeGuard'
    
    try:
        app_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # 如果创建失败，降级到用户目录
        app_dir = Path(os.path.expanduser('~')) / '.OfficeGuard'
        app_dir.mkdir(parents=True, exist_ok=True)
    
    return app_dir


def get_executable_dir() -> Path:
    """
    获取exe所在目录（打包后）或脚本所在目录（开发环境）
    """
    if is_frozen():
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent.parent


def get_config_dir() -> Path:
    """获取配置文件目录"""
    config_dir = get_app_data_dir() / 'config'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_log_dir() -> Path:
    """获取日志目录"""
    log_dir = get_app_data_dir() / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_tools_dir() -> Path:
    """获取工具目录"""
    tools_dir = get_app_data_dir() / 'tools'
    tools_dir.mkdir(parents=True, exist_ok=True)
    return tools_dir


def get_assets_dir() -> Path:
    """获取资源文件目录"""
    if is_frozen():
        # 打包后资源在exe同级目录的assets文件夹
        return Path(sys.executable).parent / 'assets'
    else:
        return Path(__file__).parent.parent / 'assets'
