#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地CI测试脚本
模拟GitHub Actions workflow的执行流程
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class LocalCITester:
    def __init__(self):
        self.project_root = Path.cwd()
        self.processes = []
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, cmd, cwd=None, timeout=300):
        """执行命令"""
        if cwd is None:
            cwd = self.project_root
            
        self.log(f"执行命令: {cmd}")
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0:
                self.log(f"✅ 命令执行成功")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.log(f"❌ 命令执行失败 (退出码: {result.returncode})", "ERROR")
                if result.stderr.strip():
                    print(f"错误输出: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"❌ 命令执行超时", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ 命令执行异常: {e}", "ERROR")
            return False
    
    def check_dependencies(self):
        """检查依赖是否存在"""
        self.log("🔍 检查项目依赖")
        
        # 检查前端依赖
        frontend_deps = self.project_root / "frontend" / "node_modules"
        if frontend_deps.exists():
            self.log("✅ 前端依赖已存在")
        else:
            self.log("❌ 前端依赖不存在")
            
        # 检查E2E依赖
        e2e_deps = self.project_root / "e2e" / "node_modules"
        if e2e_deps.exists():
            self.log("✅ E2E依赖已存在")
        else:
            self.log("❌ E2E依赖不存在")
            
        # 检查后端虚拟环境
        backend_venv = self.project_root / "backend" / ".venv"
        if backend_venv.exists():
            self.log("✅ 后端虚拟环境已存在")
        else:
            self.log("❌ 后端虚拟环境不存在")
    
    def install_dependencies(self):
        """安装依赖（模拟smart-dependencies job）"""
        self.log("📦 开始安装依赖 (模拟smart-dependencies job)")
        
        # 安装前端依赖
        self.log("安装前端依赖...")
        if not self.run_command("npm ci", cwd=self.project_root / "frontend"):
            return False
            
        # 安装E2E依赖
        self.log("安装E2E依赖...")
        if not self.run_command("npm install", cwd=self.project_root / "e2e"):
            return False
            
        # 安装后端依赖
        self.log("安装后端依赖...")
        backend_cmds = [
            "python -m venv .venv",
            ".venv/Scripts/activate && pip install --upgrade pip",
            ".venv/Scripts/activate && pip install -r requirements/base.txt",
            ".venv/Scripts/activate && pip install -r requirements/test.txt"
        ]
        
        for cmd in backend_cmds:
            if not self.run_command(cmd, cwd=self.project_root / "backend"):
                return False
                
        self.log("✅ 所有依赖安装完成")
        return True
    
    def test_frontend(self):
        """测试前端（模拟frontend-tests job）"""
        self.log("🧪 开始前端测试")
        
        # 检查依赖是否存在
        if not (self.project_root / "frontend" / "node_modules").exists():
            self.log("❌ 前端依赖不存在，跳过测试")
            return False
            
        # 运行前端测试
        return self.run_command("npm run test", cwd=self.project_root / "frontend")
    
    def test_backend(self):
        """测试后端（模拟backend-tests job）"""
        self.log("🧪 开始后端测试")
        
        # 检查虚拟环境是否存在
        if not (self.project_root / "backend" / ".venv").exists():
            self.log("❌ 后端虚拟环境不存在，跳过测试")
            return False
            
        # 运行后端测试
        return self.run_command(
            ".venv/Scripts/activate && python manage.py test", 
            cwd=self.project_root / "backend"
        )
    
    def start_servers(self):
        """启动服务器"""
        self.log("🚀 启动服务器")
        
        # 启动后端服务器
        self.log("启动后端服务器...")
        backend_process = subprocess.Popen(
            ".venv/Scripts/activate && python manage.py runserver 8000",
            shell=True,
            cwd=self.project_root / "backend"
        )
        self.processes.append(backend_process)
        
        # 等待后端启动
        time.sleep(5)
        
        # 构建前端
        self.log("构建前端...")
        if not self.run_command("npm run build", cwd=self.project_root / "frontend"):
            return False
            
        self.log("✅ 服务器启动完成")
        return True
    
    def test_e2e(self):
        """测试E2E（模拟e2e-tests job）"""
        self.log("🧪 开始E2E测试")
        
        # 检查依赖是否存在
        if not (self.project_root / "e2e" / "node_modules").exists():
            self.log("❌ E2E依赖不存在，跳过测试")
            return False
            
        # 安装Playwright浏览器
        self.log("安装Playwright浏览器...")
        if not self.run_command("npx playwright install chromium", cwd=self.project_root / "e2e"):
            return False
            
        # 运行E2E测试（使用优化后的配置）
        self.log("运行E2E测试...")
        return self.run_command(
            "npx playwright test --project=chromium --workers=1", 
            cwd=self.project_root / "e2e"
        )
    
    def cleanup(self):
        """清理进程"""
        self.log("🧹 清理进程")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        # 清理端口
        self.run_command("taskkill /F /IM python.exe 2>nul || true")
        self.run_command("taskkill /F /IM node.exe 2>nul || true")
    
    def run_full_test(self):
        """运行完整测试流程"""
        try:
            self.log("🚀 开始本地CI测试")
            self.log("=" * 50)
            
            # 1. 检查当前依赖状态
            self.check_dependencies()
            
            # 2. 安装依赖（模拟smart-dependencies）
            if not self.install_dependencies():
                self.log("❌ 依赖安装失败", "ERROR")
                return False
            
            # 3. 并行测试（模拟优化后的workflow）
            self.log("\n🔄 开始并行测试")
            
            # 前端测试
            frontend_success = self.test_frontend()
            
            # 后端测试
            backend_success = self.test_backend()
            
            # 4. E2E测试
            self.log("\n🎭 准备E2E测试")
            
            # 启动服务器
            if not self.start_servers():
                self.log("❌ 服务器启动失败", "ERROR")
                return False
            
            # 运行E2E测试
            e2e_success = self.test_e2e()
            
            # 5. 总结结果
            self.log("\n📊 测试结果总结")
            self.log("=" * 30)
            self.log(f"前端测试: {'✅ 通过' if frontend_success else '❌ 失败'}")
            self.log(f"后端测试: {'✅ 通过' if backend_success else '❌ 失败'}")
            self.log(f"E2E测试: {'✅ 通过' if e2e_success else '❌ 失败'}")
            
            overall_success = frontend_success and backend_success and e2e_success
            self.log(f"\n总体结果: {'✅ 全部通过' if overall_success else '❌ 存在失败'}")
            
            return overall_success
            
        except KeyboardInterrupt:
            self.log("\n⚠️ 测试被用户中断", "WARNING")
            return False
        except Exception as e:
            self.log(f"\n❌ 测试过程中发生异常: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

def main():
    print("🧪 本地CI测试工具")
    print("模拟GitHub Actions workflow执行")
    print("=" * 50)
    
    tester = LocalCITester()
    
    # 注册信号处理器
    def signal_handler(sig, frame):
        print("\n\n⚠️ 收到中断信号，正在清理...")
        tester.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # 运行测试
    success = tester.run_full_test()
    
    if success:
        print("\n🎉 所有测试通过！优化方案验证成功！")
        sys.exit(0)
    else:
        print("\n💥 测试失败，需要进一步调试")
        sys.exit(1)

if __name__ == '__main__':
    main()