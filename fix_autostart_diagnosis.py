# -*- coding: utf-8 -*-
"""
开机自启动诊断工具
用于检查和修复系统优化助手的开机自启动问题
"""

import winreg
import os
import sys

def check_registry():
    """检查注册表中的所有启动项"""
    print("=" * 60)
    print("检查注册表启动项")
    print("=" * 60)
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        
        # 获取所有启动项
        i = 0
        found_items = []
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                found_items.append((name, value))
                print(f"\n启动项 {i+1}:")
                print(f"  名称: {name}")
                print(f"  路径: {value}")
                
                # 检查是否包含我们的程序
                if "系统优化助手" in name or "系统优化助手" in value or "OfficeGuard" in name or "OfficeGuard" in value:
                    print("  ⭐ 这是我们的程序!")
                
                i += 1
            except OSError:
                break
        
        winreg.CloseKey(key)
        
        if not found_items:
            print("\n❌ 没有找到任何启动项")
        else:
            print(f"\n✅ 共找到 {len(found_items)} 个启动项")
        
        return found_items
    except Exception as e:
        print(f"❌ 读取注册表失败: {e}")
        return []

def clean_old_entries():
    """清理旧的启动项"""
    print("\n" + "=" * 60)
    print("清理旧的启动项")
    print("=" * 60)
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    names_to_remove = ["OfficeGuard", "系统优化助手", "系统优化助手 - 高性能模优化工具"]
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        removed = []
        for name in names_to_remove:
            try:
                winreg.DeleteValue(key, name)
                removed.append(name)
                print(f"✅ 已删除: {name}")
            except FileNotFoundError:
                print(f"⚠️ 不存在: {name}")
        
        winreg.CloseKey(key)
        
        if removed:
            print(f"\n✅ 共删除了 {len(removed)} 个旧启动项")
        else:
            print("\n✅ 没有需要删除的旧启动项")
        
        return True
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        return False

def add_new_entry():
    """添加新的启动项"""
    print("\n" + "=" * 60)
    print("添加新的启动项")
    print("=" * 60)
    
    # 查找OfficeGuard.exe的位置
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, "OfficeGuard.exe")
    
    if not os.path.exists(exe_path):
        print(f"❌ 未找到程序: {exe_path}")
        print("\n请手动输入exe路径:")
        exe_path = input("路径: ").strip('"')
        
        if not os.path.exists(exe_path):
            print(f"❌ 路径无效: {exe_path}")
            return False
    
    print(f"✅ 找到程序: {exe_path}")
    
    # 添加到注册表
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "OfficeGuard"
    startup_cmd = f'"{exe_path}" --boot-startup'
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, startup_cmd)
        
        # 验证
        verify_value, _ = winreg.QueryValueEx(key, app_name)
        winreg.CloseKey(key)
        
        if verify_value == startup_cmd:
            print(f"✅ 添加成功!")
            print(f"   名称: {app_name}")
            print(f"   命令: {startup_cmd}")
            return True
        else:
            print(f"❌ 验证失败:")
            print(f"   期望: {startup_cmd}")
            print(f"   实际: {verify_value}")
            return False
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("系统优化助手 - 开机自启动诊断工具")
    print("=" * 60)
    
    # 1. 检查当前状态
    items = check_registry()
    
    # 2. 询问是否修复
    print("\n" + "=" * 60)
    print("是否需要修复开机自启动？")
    print("=" * 60)
    print("1. 是 - 清理旧项并添加新项")
    print("2. 否 - 仅查看，不修改")
    
    choice = input("\n请选择 (1/2): ").strip()
    
    if choice == "1":
        # 清理旧的
        clean_old_entries()
        
        # 添加新的
        add_new_entry()
        
        # 再次检查
        print("\n" + "=" * 60)
        print("修复后的状态")
        print("=" * 60)
        check_registry()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
