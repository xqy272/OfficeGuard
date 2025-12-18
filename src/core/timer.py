"""
定时器模块
处理定时关机/睡眠任务
"""

import os
import time
import math
import ctypes
from typing import Callable, Tuple
from ..utils.logger import get_logger

logger = get_logger('timer')


class TimerManager:
    """定时器管理器"""
    
    def __init__(self):
        self.running = False
        self.in_grace_period = False
        self.action = ""
        self.target_timestamp = 0.0
        self.total_seconds = 0
        self.grace_seconds = 0
        self.grace_remaining = 0
        self.action_executed = False
        
        # 鼠标检测相关
        self.start_mouse_pos = (0, 0)
        self.last_input_tick = 0
        self.mouse_threshold = 15
        
        # 回调函数
        self._on_tick: Callable[[int, int, int], None] = None  # (h, m, s)
        self._on_grace_tick: Callable[[int], None] = None  # remaining
        self._on_complete: Callable[[], None] = None
        self._on_cancel: Callable[[str], None] = None
        
        # Windows API
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def set_callbacks(
        self,
        on_tick: Callable = None,
        on_grace_tick: Callable = None,
        on_complete: Callable = None,
        on_cancel: Callable = None
    ):
        """设置回调函数"""
        self._on_tick = on_tick
        self._on_grace_tick = on_grace_tick
        self._on_complete = on_complete
        self._on_cancel = on_cancel
    
    def start(self, action: str, minutes: float, grace_seconds: int, mouse_threshold: int = 15) -> bool:
        """
        启动定时器
        
        :param action: 执行动作 ('shutdown' 或 'sleep')
        :param minutes: 倒计时分钟数
        :param grace_seconds: 缓冲期秒数
        :param mouse_threshold: 鼠标移动阈值
        :return: 是否启动成功
        """
        if self.running:
            logger.warning("定时器已在运行")
            return False
        
        if minutes <= 0 or minutes > 1440:
            logger.warning("时间必须在0-1440分钟之间")
            return False
        
        if grace_seconds < 0 or grace_seconds > 3600:
            logger.warning("缓冲时间必须在0-3600秒之间")
            return False
        
        self.action = action
        self.total_seconds = int(minutes * 60)
        self.grace_seconds = grace_seconds
        self.mouse_threshold = mouse_threshold
        self.target_timestamp = time.time() + self.total_seconds
        self.running = True
        self.in_grace_period = False
        self.action_executed = False
        
        logger.info(f"启动{action}倒计时，时长{minutes}分钟，缓冲{grace_seconds}秒")
        return True
    
    def update(self) -> Tuple[bool, bool]:
        """
        更新定时器状态
        
        :return: (是否继续运行, 是否进入缓冲期)
        """
        if not self.running:
            return False, False
        
        if self.in_grace_period:
            return True, True
        
        remaining = self.target_timestamp - time.time()
        
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            h, m = divmod(m, 60)
            
            if self._on_tick:
                self._on_tick(h, m, s)
            
            return True, False
        else:
            # 进入缓冲期
            self.enter_grace_period()
            return True, True
    
    def enter_grace_period(self):
        """进入缓冲期"""
        self.in_grace_period = True
        self.grace_remaining = self.grace_seconds
        self.start_mouse_pos = self._get_cursor_pos()
        self.last_input_tick = self._get_last_input_tick()
        logger.info("进入缓冲期")
    
    def update_grace(self) -> bool:
        """
        更新缓冲期状态
        
        :return: 是否应该取消（检测到用户活动）
        """
        if not self.running or not self.in_grace_period:
            return False
        
        # 检测用户活动
        curr_pos = self._get_cursor_pos()
        dist = math.hypot(
            curr_pos[0] - self.start_mouse_pos[0],
            curr_pos[1] - self.start_mouse_pos[1]
        )
        curr_tick = self._get_last_input_tick()
        
        input_changed = curr_tick > self.last_input_tick
        mouse_moved = dist > self.mouse_threshold
        
        if mouse_moved or (input_changed and not mouse_moved):
            logger.info("检测到用户活动，取消任务")
            return True
        
        if self.grace_remaining > 0:
            if self._on_grace_tick:
                self._on_grace_tick(self.grace_remaining)
            self.grace_remaining -= 1
            return False
        else:
            # 执行动作
            self.execute()
            return False
    
    def execute(self):
        """执行定时任务"""
        if self.action_executed:
            logger.warning("操作已执行，忽略重复请求")
            return
        
        self.action_executed = True
        self.running = False
        self.in_grace_period = False
        
        try:
            if self.action == "shutdown":
                logger.info("执行系统关机")
                os.system("shutdown /s /f /t 0")
            elif self.action == "sleep":
                logger.info("执行系统睡眠")
                ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
            
            if self._on_complete:
                self._on_complete()
        except Exception as e:
            logger.error(f"执行{self.action}失败: {e}")
    
    def cancel(self, message: str = ""):
        """取消定时器"""
        self.running = False
        self.in_grace_period = False
        
        if self._on_cancel:
            self._on_cancel(message)
        
        logger.info(f"定时器已取消: {message or '手动取消'}")
    
    def _get_cursor_pos(self) -> Tuple[int, int]:
        """获取鼠标位置"""
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        
        pt = POINT()
        self.user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)
    
    def _get_last_input_tick(self) -> int:
        """获取最后输入时间"""
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_uint)
            ]
        
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        self.user32.GetLastInputInfo(ctypes.byref(lii))
        return lii.dwTime
    
    @property
    def remaining_seconds(self) -> int:
        """获取剩余秒数"""
        if not self.running:
            return 0
        return max(0, int(self.target_timestamp - time.time()))
