"""
主题和颜色配置
现代简洁风格 - 参考 shadcn/ui
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorScheme:
    """颜色方案"""
    # 背景色
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_card: str
    
    # 文字色
    text_primary: str
    text_secondary: str
    text_muted: str
    
    # 强调色
    accent: str
    accent_hover: str
    accent_light: str
    
    # 功能色
    success: str
    warning: str
    danger: str
    info: str
    
    # 边框
    border: str
    border_light: str
    
    # 输入框
    input_bg: str
    input_border: str
    input_focus: str
    
    # 按钮
    btn_primary_bg: str
    btn_primary_fg: str
    btn_secondary_bg: str
    btn_secondary_fg: str
    btn_danger_bg: str
    btn_danger_fg: str
    btn_outline_bg: str
    btn_outline_fg: str
    btn_outline_border: str


# 浅色主题 - shadcn/ui 风格
LIGHT_THEME = ColorScheme(
    # 背景 - 纯净白色系
    bg_primary="#ffffff",
    bg_secondary="#fafafa",
    bg_tertiary="#f4f4f5",
    bg_card="#ffffff",
    
    # 文字 - 高对比度
    text_primary="#09090b",
    text_secondary="#3f3f46",
    text_muted="#71717a",
    
    # 强调色 - 简洁黑色
    accent="#18181b",
    accent_hover="#27272a",
    accent_light="#f4f4f5",
    
    # 功能色 - 柔和色调
    success="#22c55e",
    warning="#f59e0b",
    danger="#ef4444",
    info="#3b82f6",
    
    # 边框 - 淡灰色
    border="#e4e4e7",
    border_light="#f4f4f5",
    
    # 输入框
    input_bg="#ffffff",
    input_border="#e4e4e7",
    input_focus="#18181b",
    
    # 按钮
    btn_primary_bg="#18181b",
    btn_primary_fg="#fafafa",
    btn_secondary_bg="#f4f4f5",
    btn_secondary_fg="#18181b",
    btn_danger_bg="#ef4444",
    btn_danger_fg="#ffffff",
    btn_outline_bg="#ffffff",
    btn_outline_fg="#18181b",
    btn_outline_border="#e4e4e7",
)


# 深色主题 - 现代暗色
DARK_THEME = ColorScheme(
    # 背景
    bg_primary="#09090b",
    bg_secondary="#18181b",
    bg_tertiary="#27272a",
    bg_card="#18181b",
    
    # 文字
    text_primary="#fafafa",
    text_secondary="#a1a1aa",
    text_muted="#71717a",
    
    # 强调色
    accent="#fafafa",
    accent_hover="#e4e4e7",
    accent_light="#27272a",
    
    # 功能色
    success="#22c55e",
    warning="#f59e0b",
    danger="#ef4444",
    info="#3b82f6",
    
    # 边框
    border="#27272a",
    border_light="#3f3f46",
    
    # 输入框
    input_bg="#18181b",
    input_border="#27272a",
    input_focus="#fafafa",
    
    # 按钮
    btn_primary_bg="#fafafa",
    btn_primary_fg="#18181b",
    btn_secondary_bg="#27272a",
    btn_secondary_fg="#fafafa",
    btn_danger_bg="#ef4444",
    btn_danger_fg="#ffffff",
    btn_outline_bg="#09090b",
    btn_outline_fg="#fafafa",
    btn_outline_border="#27272a",
)


# 字体配置
class Fonts:
    """字体配置 - 根据 DPI 自动调整"""
    FAMILY = "Microsoft YaHei UI"  # 微软雅黑，Windows 上显示效果好
    FAMILY_MONO = "Consolas"
    
    # 获取 DPI 缩放因子
    _scale = 1.0
    
    @classmethod
    def init_scale(cls, root):
        """初始化 DPI 缩放因子"""
        try:
            # 获取实际 DPI
            dpi = root.winfo_fpixels('1i')
            cls._scale = dpi / 96.0  # 96 是标准 DPI
            if cls._scale < 1.0:
                cls._scale = 1.0
        except:
            cls._scale = 1.0
    
    @classmethod
    def scaled(cls, size: int) -> int:
        """根据 DPI 缩放字体大小"""
        return int(size * cls._scale)
    
    # 字体大小 - 完整名称
    SIZE_XS = 9
    SIZE_SM = 10
    SIZE_BASE = 11
    SIZE_LG = 12
    SIZE_XL = 14
    SIZE_2XL = 16
    SIZE_3XL = 18
    SIZE_4XL = 24
    
    # 字体大小 - 简短别名
    XS = 9
    SM = 10
    BASE = 11
    LG = 12
    XL = 14
    XL2 = 16
    XL3 = 18
    XL4 = 24
    
    @classmethod
    def get(cls, size: str = "base", weight: str = "normal"):
        """获取字体元组"""
        size_map = {
            "xs": cls.SIZE_XS,
            "sm": cls.SIZE_SM,
            "base": cls.SIZE_BASE,
            "lg": cls.SIZE_LG,
            "xl": cls.SIZE_XL,
            "2xl": cls.SIZE_2XL,
            "3xl": cls.SIZE_3XL,
            "4xl": cls.SIZE_4XL,
        }
        font_size = size_map.get(size, cls.SIZE_BASE)
        return (cls.FAMILY, font_size, weight) if weight != "normal" else (cls.FAMILY, font_size)


class Theme:
    """主题管理器"""
    
    def __init__(self, mode: str = "light"):
        self.mode = mode
        self.colors = LIGHT_THEME if mode == "light" else DARK_THEME
        self.fonts = Fonts
        
    @property
    def bg(self) -> str:
        return self.colors.bg_primary
    
    @property
    def bg2(self) -> str:
        return self.colors.bg_secondary
    
    @property
    def bg3(self) -> str:
        return self.colors.bg_tertiary
    
    @property
    def card(self) -> str:
        return self.colors.bg_card
    
    @property
    def fg(self) -> str:
        return self.colors.text_primary
    
    @property
    def fg2(self) -> str:
        return self.colors.text_secondary
    
    @property
    def muted(self) -> str:
        return self.colors.text_muted
    
    @property
    def accent(self) -> str:
        return self.colors.accent
    
    @property
    def border(self) -> str:
        return self.colors.border
    
    def toggle(self):
        """切换主题"""
        self.mode = "dark" if self.mode == "light" else "light"
        self.colors = LIGHT_THEME if self.mode == "light" else DARK_THEME
