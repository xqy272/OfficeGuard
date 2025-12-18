"""
系统托盘模块
管理系统托盘图标和菜单
"""

import threading
from typing import Callable
from PIL import Image, ImageDraw
import pystray
from ..utils.logger import get_logger

logger = get_logger('tray')


class TrayManager:
    """系统托盘管理器"""
    
    def __init__(self):
        self.icon = None
        self.thread = None
        
        # 回调
        self._on_show: Callable[[], None] = None
        self._on_quit: Callable[[], None] = None
        self._on_toggle_hotkey: Callable[[], None] = None
        
        # 状态
        self.hotkey_enabled = True
    
    def set_callbacks(
        self,
        on_show: Callable = None,
        on_quit: Callable = None,
        on_toggle_hotkey: Callable = None
    ):
        """设置回调函数"""
        self._on_show = on_show
        self._on_quit = on_quit
        self._on_toggle_hotkey = on_toggle_hotkey
    
    def _create_icon_image(self, size: int = 64, color: str = "#3498db") -> Image.Image:
        """
        创建托盘图标
        
        :param size: 图标大小
        :param color: 图标颜色
        :return: PIL Image 对象
        """
        # 解析颜色
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            fill_color = (r, g, b)
        else:
            fill_color = (52, 152, 219)  # 默认蓝色
        
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制圆形背景
        margin = size // 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=fill_color
        )
        
        # 绘制盾牌图案
        shield_color = (255, 255, 255)
        center_x = size // 2
        center_y = size // 2
        
        # 简单的盾牌形状
        points = [
            (center_x, center_y - size // 4),  # 顶部
            (center_x + size // 5, center_y - size // 8),  # 右上
            (center_x + size // 5, center_y + size // 8),  # 右中
            (center_x, center_y + size // 4),  # 底部
            (center_x - size // 5, center_y + size // 8),  # 左中
            (center_x - size // 5, center_y - size // 8),  # 左上
        ]
        draw.polygon(points, fill=shield_color)
        
        return image
    
    def start(self, hotkey_enabled: bool = True):
        """
        启动系统托盘
        
        :param hotkey_enabled: 快捷键是否启用
        """
        self.hotkey_enabled = hotkey_enabled
        
        try:
            icon_image = self._create_icon_image()
            
            def get_hotkey_text(item):
                return f"快捷键: {'✓ 开启' if self.hotkey_enabled else '✗ 关闭'}"
            
            menu = pystray.Menu(
                pystray.MenuItem("显示主界面", self._on_show_click),
                pystray.MenuItem(get_hotkey_text, self._on_toggle_click),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("退出", self._on_quit_click)
            )
            
            self.icon = pystray.Icon(
                "office_guard",
                icon_image,
                "系统优化助手",
                menu
            )
            
            # 在单独线程中运行
            self.thread = threading.Thread(target=self.icon.run, daemon=True)
            self.thread.start()
            
            logger.info("系统托盘已启动")
        except Exception as e:
            logger.error(f"托盘启动失败: {e}")
    
    def stop(self):
        """停止系统托盘"""
        try:
            if self.icon:
                self.icon.stop()
                self.icon = None
            logger.info("系统托盘已停止")
        except Exception as e:
            logger.error(f"托盘停止失败: {e}")
    
    def _on_show_click(self):
        """显示主界面"""
        if self._on_show:
            self._on_show()
    
    def _on_toggle_click(self):
        """切换快捷键"""
        self.hotkey_enabled = not self.hotkey_enabled
        if self._on_toggle_hotkey:
            self._on_toggle_hotkey()
    
    def _on_quit_click(self):
        """退出应用"""
        if self._on_quit:
            self._on_quit()
    
    def update_hotkey_status(self, enabled: bool):
        """更新快捷键状态"""
        self.hotkey_enabled = enabled
        # pystray 会自动更新菜单文本
