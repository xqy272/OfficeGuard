import os
import winreg
import re

def check_autostart_status():
    """检查开机自启动的状态"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "OfficeGuard"
        problems = []
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_QUERY_VALUE)
            try:
                value, _ = winreg.QueryValueEx(key, app_name)
                winreg.CloseKey(key)
                
                print(f"✅ 找到注册表项: {app_name}")
                print(f"📋 注册表值: {value}")
                print()
                
                # 解析路径
                match = re.search(r'"([^"]+)"', value)
                if match:
                    exe_path = match.group(1)
                    
                    # 检查文件是否存在
                    if not os.path.exists(exe_path):
                        problems.append(f"❌ EXE文件不存在: {exe_path}")
                    else:
                        print(f"✅ EXE文件存在: {exe_path}")
                    
                    # 检查是否包含OneDrive路径
                    if "OneDrive" in exe_path:
                        problems.append("⚠️ 路径包含OneDrive，可能导致开机时不可用")
                    
                    # 检查是否包含中文
                    if any('\u4e00' <= c <= '\u9fff' for c in exe_path):
                        problems.append("⚠️ 路径包含中文字符，可能导致兼容性问题")
                    
                    # 检查是否有--boot-startup参数
                    if "--boot-startup" in value:
                        print("✅ 包含--boot-startup参数")
                    else:
                        problems.append("❌ 缺少--boot-startup参数")
                    
                    return (True, value, problems)
                else:
                    problems.append("❌ 无法解析注册表值")
                    return (True, value, problems)
                    
            except FileNotFoundError:
                winreg.CloseKey(key)
                print(f"❌ 注册表中未找到启动项: {app_name}")
                return (False, None, ["注册表中未找到启动项"])
        except PermissionError:
            print("❌ 无权限读取注册表")
            return (False, None, ["无权限读取注册表"])
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return (False, None, [f"检查失败: {e}"])

if __name__ == "__main__":
    print("=" * 60)
    print("OfficeGuard 开机自启动诊断工具")
    print("=" * 60)
    print()
    
    enabled, value, problems = check_autostart_status()
    
    print()
    print("=" * 60)
    print("诊断结果")
    print("=" * 60)
    
    if problems:
        print("\n⚠️ 发现以下问题：\n")
        for i, problem in enumerate(problems, 1):
            print(f"{i}. {problem}")
        
        print("\n💡 建议解决方案：")
        print("1. 将程序移动到非OneDrive路径（如 C:\\Program Files\\OfficeGuard）")
        print("2. 确保路径不包含中文字符")
        print("3. 移动后在程序中重新设置开机自启动")
    else:
        print("\n✅ 开机自启动配置正常！")
    
    print()
    input("按回车键退出...")
