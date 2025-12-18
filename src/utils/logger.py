"""
日志模块
配置并管理应用程序日志
"""

import logging
from logging.handlers import RotatingFileHandler
from .paths import get_log_dir, is_frozen

# 全局 logger 实例
_logger = None


def setup_logging() -> logging.Logger:
    """
    配置日志系统
    日志路径: C:\\Users\\{用户}\\AppData\\Local\\OfficeGuard\\logs\\guard.log
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    log_dir = get_log_dir()
    log_file = log_dir / 'guard.log'
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带日志轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器（仅在开发环境输出）
    handlers = [file_handler]
    if not is_frozen():
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        handlers.append(console_handler)
    
    # 配置根logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers
    )
    
    _logger = logging.getLogger('OfficeGuard')
    _logger.info("=" * 60)
    _logger.info(f"运行模式: {'打包EXE' if is_frozen() else '开发环境'}")
    _logger.info("=" * 60)
    
    return _logger


def get_logger(name: str = None) -> logging.Logger:
    """
    获取 logger 实例
    :param name: logger名称，默认为 'OfficeGuard'
    """
    global _logger
    
    if _logger is None:
        setup_logging()
    
    if name:
        return logging.getLogger(f'OfficeGuard.{name}')
    return _logger
