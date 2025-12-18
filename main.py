"""
OfficeGuard - 系统优化助手
主入口文件
"""

import sys
import ctypes
import tkinter as tk

# 添加项目路径
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import setup_logging
from src.ui.app import ModernApp


def setup_dpi():
    """设置 DPI 感知
    
    注意：对于 Tkinter 应用，不设置 DPI 感知反而效果更好
    让 Windows 自动处理缩放，避免在高 DPI 屏幕上出现问题
    """
    # 不设置 DPI 感知，让 Windows 自动缩放
    # 这样在 4K 200% 缩放等高 DPI 环境下也能正常显示
    pass


def main():
    """主函数"""
    # 设置 DPI 感知 (必须在创建 Tk 窗口前)
    setup_dpi()
    
    # 初始化日志
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("OfficeGuard v2.0.0 - 启动")
    logger.info("=" * 50)
    
    try:
        # 创建主窗口
        root = tk.Tk()
        
        # 创建应用
        app = ModernApp(root)
        
        # 运行
        app.run()
        
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
        from tkinter import messagebox
        messagebox.showerror("错误", f"应用异常：{e}\n请查看日志文件")
    finally:
        logger.info("应用已关闭")


if __name__ == "__main__":
    main()
