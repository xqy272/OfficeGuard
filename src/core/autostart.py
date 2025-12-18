"""
开机自启动管理模块
使用 Windows 任务计划程序实现开机自启动
"""

import os
import sys
import subprocess
import winreg
import urllib.request
from typing import Tuple, List
from ..utils.paths import get_tools_dir, is_frozen
from ..utils.logger import get_logger

logger = get_logger('autostart')


def is_admin() -> bool:
    """检查是否具有管理员权限"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.warning(f"管理员权限检查失败: {e}")
        return False


def is_system_boot() -> bool:
    """
    判断是否是系统开机启动
    """
    try:
        import ctypes
        
        # 方法1：检查命令行参数
        if '--boot-startup' in sys.argv:
            logger.info("检测到开机启动标志")
            return True
        
        # 方法2：检查系统运行时间
        kernel32 = ctypes.windll.kernel32
        tick_count = kernel32.GetTickCount64()
        uptime_minutes = tick_count / 1000 / 60
        
        if uptime_minutes < 3:
            logger.info(f"检测到开机启动（运行时间<3分钟: {uptime_minutes:.2f}分钟）")
            return True
        
        return False
    except Exception as e:
        logger.error(f"检测系统启动时间失败: {e}")
        return False


def remove_boot_startup_args():
    """清除启动参数中的 --boot-startup 标志"""
    try:
        if '--boot-startup' in sys.argv:
            sys.argv.remove('--boot-startup')
            logger.info("已清除 --boot-startup 参数")
    except Exception as e:
        logger.debug(f"清除启动参数时出错: {e}")


class AutoStartManager:
    """开机自启动管理器"""
    
    TASK_NAME = "OfficeGuard_AutoStart"
    
    def __init__(self):
        self.app_path = self._get_app_path()
    
    def _get_app_path(self) -> str:
        """获取应用程序路径"""
        if is_frozen():
            return sys.executable
        else:
            return os.path.abspath(sys.argv[0])
    
    def set_autostart(self, enable: bool) -> bool:
        """
        设置开机自启动
        
        :param enable: 是否启用
        :return: 是否设置成功
        """
        try:
            # 清理旧版注册表项
            self._cleanup_old_registry()
            
            if enable:
                return self._create_task()
            else:
                return self._delete_task()
        except Exception as e:
            logger.error(f"设置开机自启动失败: {e}")
            return False
    
    def _cleanup_old_registry(self):
        """清理旧版本的注册表启动项"""
        for key_name in ["OfficeGuard", "SystemOptimizer", "系统优化助手"]:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.DeleteValue(key, key_name)
                winreg.CloseKey(key)
                logger.info(f"已清理旧版注册表启动项: {key_name}")
            except FileNotFoundError:
                pass
            except Exception as e:
                logger.debug(f"清理注册表项 {key_name} 时出错: {e}")
    
    def _create_task(self) -> bool:
        """创建任务计划"""
        logger.info(f"正在创建任务计划: {self.TASK_NAME}")
        
        # 如果不是管理员，尝试提权执行
        if not is_admin():
            logger.info("当前未拥有管理员权限，尝试提权执行...")
            try:
                import ctypes
                # 注意：/TR 参数内部的引号需要转义
                params = f'/Create /TN "{self.TASK_NAME}" /TR "\"{self.app_path}\" --boot-startup" /SC ONLOGON /RL HIGHEST /F'
                
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", "schtasks", params, None, 0
                )
                
                if ret > 32:
                    logger.info("已请求管理员权限")
                    return True
                else:
                    logger.error(f"请求管理员权限失败，错误码: {ret}")
                    return False
            except Exception as e:
                logger.error(f"提权执行失败: {e}")
                return False
        
        # 先删除旧任务
        try:
            subprocess.run(
                ['schtasks', '/Delete', '/TN', self.TASK_NAME, '/F'],
                capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except:
            pass
        
        # 创建新任务
        cmd = [
            'schtasks', '/Create',
            '/TN', self.TASK_NAME,
            '/TR', f'"{self.app_path}" --boot-startup',
            '/SC', 'ONLOGON',
            '/RL', 'HIGHEST',
            '/F'
        ]
        
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            logger.info(f"任务计划创建成功: {self.TASK_NAME}")
            return True
        else:
            logger.error(f"创建任务计划失败: {result.stderr}")
            return False
    
    def _delete_task(self) -> bool:
        """删除任务计划"""
        logger.info(f"正在删除任务计划: {self.TASK_NAME}")
        
        # 如果不是管理员，尝试提权执行
        if not is_admin():
            logger.info("当前未拥有管理员权限，尝试提权执行...")
            try:
                import ctypes
                params = f'/Delete /TN "{self.TASK_NAME}" /F'
                
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", "schtasks", params, None, 0
                )
                
                if ret > 32:
                    logger.info("已请求管理员权限")
                    return True
                else:
                    logger.error(f"请求管理员权限失败，错误码: {ret}")
                    return False
            except Exception as e:
                logger.error(f"提权执行失败: {e}")
                return False
        
        result = subprocess.run(
            ['schtasks', '/Delete', '/TN', self.TASK_NAME, '/F'],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0 or 'cannot find' in result.stderr.lower():
            logger.info(f"任务计划已删除: {self.TASK_NAME}")
            return True
        else:
            logger.warning(f"删除任务计划时出现警告: {result.stderr}")
            return True
    
    def check_status(self) -> Tuple[bool, str, List[str]]:
        """
        检查开机自启动状态
        
        :return: (是否启用, 任务信息, 问题列表)
        """
        try:
            import re
            
            result = subprocess.run(
                ['schtasks', '/Query', '/TN', self.TASK_NAME, '/FO', 'LIST', '/V'],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                return False, None, ["任务计划不存在"]
            
            output = result.stdout
            problems = []
            task_info = f"任务计划: {self.TASK_NAME}"
            
            # 检查是否禁用
            if '已禁用' in output or 'Disabled' in output:
                problems.append("任务已创建但被禁用")
            
            # 检查执行路径
            match = re.search(r'要执行的操作:.*?([A-Za-z]:\\[^\r\n]+)', output)
            if not match:
                match = re.search(r'Task To Run:.*?([A-Za-z]:\\[^\r\n]+)', output)
            
            if match:
                exe_path = match.group(1).strip()
                task_info = exe_path
                
                # 提取实际路径
                if '"' in exe_path:
                    exe_path = exe_path.split('"')[1]
                else:
                    exe_path = exe_path.split()[0]
                
                if not os.path.exists(exe_path):
                    problems.append(f"EXE文件不存在: {exe_path}")
                
                if "--boot-startup" not in match.group(1):
                    problems.append("缺少--boot-startup参数")
            
            return True, task_info, problems
        except Exception as e:
            logger.error(f"检查任务计划状态失败: {e}")
            return False, None, [f"检查失败: {e}"]


class AutoLogonManager:
    """自动登录管理器"""
    
    def __init__(self):
        self.autologon_path = None
    
    def _download_autologon(self) -> str:
        """下载 Sysinternals Autologon 工具"""
        try:
            tools_dir = get_tools_dir()
            autologon_exe = tools_dir / 'Autologon.exe'
            
            if autologon_exe.exists():
                logger.info(f"Autologon工具已存在: {autologon_exe}")
                return str(autologon_exe)
            
            logger.info("正在下载 Sysinternals Autologon...")
            url = "https://live.sysinternals.com/Autologon.exe"
            
            temp_file = tools_dir / 'Autologon.exe.tmp'
            urllib.request.urlretrieve(url, str(temp_file))
            temp_file.rename(autologon_exe)
            
            logger.info(f"Autologon工具下载完成: {autologon_exe}")
            return str(autologon_exe)
        except Exception as e:
            logger.error(f"下载Autologon工具失败: {e}")
            return None
    
    def set_autologon(self, enable: bool, username: str = "", password: str = "", domain: str = ".") -> bool:
        """
        设置 Windows 自动登录
        
        :param enable: 是否启用
        :param username: 用户名
        :param password: 密码
        :param domain: 域名，默认为本机
        :return: 是否设置成功
        """
        try:
            if enable:
                autologon_path = self._download_autologon()
                if not autologon_path:
                    return False
                
                cmd = [autologon_path, username, domain, password, '/accepteula']
                logger.info(f"正在配置自动登录，用户名: {username}")
                
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    logger.info("自动登录已启用（使用LSA加密）")
                    return True
                else:
                    logger.error(f"Autologon执行失败: {result.stderr}")
                    return False
            else:
                # 禁用自动登录
                logger.info("正在禁用自动登录")
                
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                    winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
                )
                
                winreg.SetValueEx(key, "AutoAdminLogon", 0, winreg.REG_SZ, "0")
                
                try:
                    winreg.DeleteValue(key, "DefaultPassword")
                except:
                    pass
                
                winreg.CloseKey(key)
                logger.info("自动登录已禁用")
                return True
        except Exception as e:
            logger.error(f"设置自动登录失败: {e}")
            return False


def launch_startup_apps(app_list: List[dict]) -> Tuple[List[str], List[str]]:
    """
    启动指定的应用程序列表
    
    :param app_list: 应用程序列表
    :return: (已启动列表, 失败列表)
    """
    import time
    
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
            subprocess.Popen([app_path], shell=True)
            logger.info(f"已启动应用程序: {app_name}")
            launched.append(app_name)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"启动应用程序失败: {app_name} - {e}")
            failed.append(app_name)
    
    return launched, failed
