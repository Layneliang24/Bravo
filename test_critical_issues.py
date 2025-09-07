#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件 - 包含大量高严重性临时修改标记
用于验证Git钩子的阻止提交功能
"""

import os
import sys

# FIXME: 这是一个严重的安全漏洞，需要立即修复
def vulnerable_function():
    # XXX: 危险！这里直接执行用户输入
    user_input = input("输入命令: ")
    os.system(user_input)  # HACK: 临时解决方案，极其危险

# FIXME: 数据库连接硬编码密码
DB_PASSWORD = "admin123"  # TODO: 移动到环境变量

# XXX: 这个函数会导致内存泄漏
def memory_leak_function():
    # FIXME: 无限循环，会耗尽系统资源
    data = []
    while True:
        data.append("x" * 1000000)  # HACK: 测试用，记得删除

# FIXME: 错误的权限检查逻辑
def check_permissions(user):
    # XXX: 总是返回True，绕过所有安全检查
    return True  # TODO: 实现真正的权限验证

# FIXME: SQL注入漏洞
def unsafe_query(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # XXX: 直接拼接SQL
    # HACK: 临时禁用参数化查询
    return query

# FIXME: 密钥硬编码
API_KEY = "sk-1234567890abcdef"  # TODO: 使用密钥管理服务

if __name__ == "__main__":
    # XXX: 调试代码，生产环境需要删除
    print("DEBUG: 启动测试模式")
    # FIXME: 这里会暴露敏感信息
    print(f"API密钥: {API_KEY}")
    
    # HACK: 临时跳过初始化
    # vulnerable_function()