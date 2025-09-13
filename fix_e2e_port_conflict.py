#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E测试端口冲突修复脚本
解决localhost:3001端口被占用的问题
"""

import os
import sys
import subprocess
import time
import socket
import psutil
from pathlib import Path

def check_port_usage(port):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            return result == 0  # 0表示连接成功，端口被占用
    except Exception as e:
        print(f"检查端口时出错: {e}")
        return False

def find_processes_using_port(port):
    """找到占用指定端口的进程"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def kill_processes_on_port(port):
    """杀死占用指定端口的进程"""
    processes = find_processes_using_port(port)
    killed_count = 0
    
    for proc_info in processes:
        try:
            pid = proc_info['pid']
            name = proc_info['name']
            print(f"正在终止进程: PID={pid}, Name={name}")
            
            # 尝试优雅终止
            proc = psutil.Process(pid)
            proc.terminate()
            
            # 等待进程终止
            try:
                proc.wait(timeout=5)
                print(f"✅ 进程 {pid} 已优雅终止")
                killed_count += 1
            except psutil.TimeoutExpired:
                # 强制杀死
                proc.kill()
                print(f"⚠️ 强制终止进程 {pid}")
                killed_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"无法终止进程 {proc_info['pid']}: {e}")
    
    return killed_count

def cleanup_pid_files():
    """清理可能存在的PID文件"""
    pid_files = [
        'frontend/frontend.pid',
        'backend/backend.pid',
        'e2e/server.pid'
    ]
    
    for pid_file in pid_files:
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # 尝试终止PID文件中的进程
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    proc.wait(timeout=3)
                    print(f"✅ 终止PID文件中的进程: {pid}")
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass
                
                # 删除PID文件
                os.remove(pid_file)
                print(f"🗑️ 删除PID文件: {pid_file}")
                
            except (ValueError, FileNotFoundError, PermissionError) as e:
                print(f"处理PID文件 {pid_file} 时出错: {e}")

def check_playwright_config():
    """检查Playwright配置中的端口设置"""
    config_file = Path('e2e/playwright.config.ts')
    if config_file.exists():
        try:
            content = config_file.read_text(encoding='utf-8')
            print("\n📋 Playwright配置检查:")
            
            # 检查webServer配置
            if 'webServer' in content:
                print("✅ 找到webServer配置")
                if 'reuseExistingServer' in content:
                    print("✅ 找到reuseExistingServer配置")
                else:
                    print("⚠️ 未找到reuseExistingServer配置，建议添加")
            else:
                print("⚠️ 未找到webServer配置")
                
        except Exception as e:
            print(f"读取Playwright配置时出错: {e}")
    else:
        print("⚠️ 未找到Playwright配置文件")

def suggest_fixes():
    """提供修复建议"""
    print("\n🔧 修复建议:")
    print("1. 在Playwright配置中添加 reuseExistingServer: true")
    print("2. 使用动态端口分配避免冲突")
    print("3. 在测试前检查端口可用性")
    print("4. 确保测试结束后正确清理进程")
    print("5. 使用Docker容器隔离测试环境")

def main():
    print("🔍 E2E测试端口冲突诊断和修复")
    print("=" * 50)
    
    # 检查端口3001
    port = 3001
    print(f"\n🔍 检查端口 {port} 使用情况...")
    
    if check_port_usage(port):
        print(f"❌ 端口 {port} 被占用")
        
        # 找到占用端口的进程
        processes = find_processes_using_port(port)
        if processes:
            print(f"\n📋 占用端口 {port} 的进程:")
            for proc in processes:
                print(f"  - PID: {proc['pid']}, Name: {proc['name']}")
                print(f"    Command: {proc['cmdline'][:100]}...")
            
            # 询问是否终止进程
            response = input(f"\n是否终止这些进程以释放端口 {port}? (y/N): ")
            if response.lower() in ['y', 'yes']:
                killed = kill_processes_on_port(port)
                print(f"✅ 已终止 {killed} 个进程")
                
                # 再次检查端口
                time.sleep(1)
                if not check_port_usage(port):
                    print(f"✅ 端口 {port} 现在可用")
                else:
                    print(f"❌ 端口 {port} 仍被占用")
        else:
            print(f"⚠️ 未找到占用端口 {port} 的进程")
    else:
        print(f"✅ 端口 {port} 可用")
    
    # 清理PID文件
    print("\n🧹 清理PID文件...")
    cleanup_pid_files()
    
    # 检查Playwright配置
    check_playwright_config()
    
    # 提供修复建议
    suggest_fixes()
    
    print("\n✅ 诊断完成")

if __name__ == '__main__':
    main()