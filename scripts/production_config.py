#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境配置文件
代码变更追踪系统 - 生产级配置

此文件包含生产环境的优化配置，包括:
- 检测规则配置
- 性能参数调优
- 日志和监控设置
- 安全和权限配置
"""

import os
import re
from typing import Dict, List, Set, Tuple

# ============================================================================
# 核心检测规则配置
# ============================================================================

# 高严重性模式 - 会阻止提交
HIGH_SEVERITY_PATTERNS = [
    # 基础临时标记
    r'\b(TODO|FIXME|HACK|XXX|BUG|TEMP|DEBUG|REMOVE)\b',
    
    # 调试相关
    r'console\.log\(',  # JavaScript调试输出
    r'print\(',         # Python调试输出（需要更精确的匹配）
    r'debugger;',       # JavaScript断点
    r'pdb\.set_trace\(', # Python调试断点
    
    # 敏感信息泄露
    r'password\s*=\s*["\'][^"\'].*["\']',  # 硬编码密码
    r'api[_-]?key\s*=\s*["\'][^"\'].*["\']', # API密钥
    r'secret\s*=\s*["\'][^"\'].*["\']',     # 密钥信息
    
    # 临时绕过和禁用
    r'# *disable',      # 禁用检查
    r'# *skip',         # 跳过检查
    r'# *ignore',       # 忽略检查
]

# 中等严重性模式 - 仅警告
MEDIUM_SEVERITY_PATTERNS = [
    r'\b(NOTE|REVIEW|OPTIMIZE|REFACTOR|IMPROVE)\b',
    r'\b(QUESTION|DISCUSS|CONSIDER)\b',
    r'# *TODO:', # 带冒号的TODO（可能是正式文档）
]

# 低严重性模式 - 仅记录
LOW_SEVERITY_PATTERNS = [
    r'\b(INFO|HINT|TIP)\b',
]

# ============================================================================
# 文件类型和扩展名配置
# ============================================================================

# 支持检查的文件扩展名
SUPPORTED_EXTENSIONS = {
    # 前端
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', '.scss', '.less',
    # 后端
    '.py', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs',
    # 移动端
    '.swift', '.kt', '.dart',
    # 配置文件
    '.json', '.yaml', '.yml', '.xml', '.toml',
    # 脚本
    '.sh', '.bash', '.ps1', '.bat',
    # 文档
    '.md', '.rst', '.txt',
}

# 排除的文件路径模式
EXCLUDED_PATHS = [
    r'node_modules/',
    r'\.git/',
    r'\.vscode/',
    r'\.idea/',
    r'__pycache__/',
    r'\.pytest_cache/',
    r'coverage/',
    r'dist/',
    r'build/',
    r'\.next/',
    r'\.nuxt/',
    r'vendor/',
    r'logs?/',
    r'tmp/',
    r'temp/',
]

# 排除的文件名模式
EXCLUDED_FILES = [
    r'.*\.min\.(js|css)$',  # 压缩文件
    r'.*\.bundle\.(js|css)$',  # 打包文件
    r'.*\.lock$',  # 锁文件
    r'.*\.log$',   # 日志文件
]

# ============================================================================
# 性能和限制配置
# ============================================================================

# 文件大小限制（字节）
MAX_FILE_SIZE = 1024 * 1024  # 1MB

# 单次检查的最大文件数量
MAX_FILES_PER_CHECK = 100

# 超时设置（秒）
CHECK_TIMEOUT = 30

# 并发处理配置
MAX_WORKERS = 4  # 最大并发数
USE_MULTIPROCESSING = True  # 是否启用多进程

# ============================================================================
# 阈值和行为配置
# ============================================================================

# 严重性阈值配置
SEVERITY_THRESHOLDS = {
    'high': {
        'max_issues': 0,  # 高严重性问题最大允许数量（0表示不允许）
        'block_commit': True,  # 是否阻止提交
    },
    'medium': {
        'max_issues': 5,  # 中等严重性问题最大允许数量
        'block_commit': False,  # 仅警告，不阻止提交
    },
    'low': {
        'max_issues': 20,  # 低严重性问题最大允许数量
        'block_commit': False,  # 仅记录，不阻止提交
    }
}

# 特殊文件类型的宽松规则
RELAXED_RULES_FOR_TYPES = {
    '.md': ['TODO', 'FIXME'],  # Markdown文件允许TODO和FIXME
    '.txt': ['TODO', 'NOTE'],  # 文本文件允许TODO和NOTE
    '.json': [],  # JSON文件不检查注释
}

# ============================================================================
# 日志和监控配置
# ============================================================================

# 日志级别
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# 日志文件配置
LOG_FILE = '.git/hooks/pre-commit.log'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 统计信息收集
ENABLE_STATISTICS = True
STATISTICS_FILE = '.git/hooks/statistics.json'

# 性能监控
ENABLE_PERFORMANCE_MONITORING = True
PERFORMANCE_LOG_THRESHOLD = 0.1  # 超过0.1秒记录性能日志

# ============================================================================
# 输出和显示配置
# ============================================================================

# 输出格式配置
OUTPUT_CONFIG = {
    'show_line_numbers': True,
    'show_file_path': True,
    'show_severity': True,
    'show_suggestions': True,
    'max_issues_display': 20,  # 最多显示的问题数量
    'truncate_long_lines': True,
    'max_line_length': 100,
}

# 颜色和样式配置（如果终端支持）
COLOR_CONFIG = {
    'enable_colors': False,  # 生产环境建议关闭颜色
    'high_severity_color': 'red',
    'medium_severity_color': 'yellow',
    'low_severity_color': 'blue',
    'success_color': 'green',
}

# 消息模板
MESSAGE_TEMPLATES = {
    'start': '[INFO] 代码变更追踪系统启动 - 生产模式',
    'scanning': '[INFO] 扫描 {file_count} 个暂存文件',
    'completed': '[INFO] 扫描完成，耗时 {duration:.3f} 秒',
    'issues_found': '[RESULT] 发现 {total} 个问题 (高: {high}, 中: {medium}, 低: {low})',
    'commit_blocked': '[FAILED] 提交被阻止 - 发现 {count} 个高严重性问题',
    'commit_allowed': '[SUCCESS] 提交检查通过',
    'bypass_hint': '[TIP] 紧急情况可使用 --no-verify 跳过检查',
    'error': '[ERROR] {message}',
    'warning': '[WARNING] {message}',
}

# ============================================================================
# 环境特定配置
# ============================================================================

# 根据环境变量调整配置
def get_environment_config():
    """根据环境变量获取配置"""
    env = os.getenv('ENVIRONMENT', 'production').lower()
    
    if env == 'development':
        return {
            'LOG_LEVEL': 'DEBUG',
            'ENABLE_STATISTICS': True,
            'COLOR_CONFIG': {'enable_colors': True},
            'SEVERITY_THRESHOLDS': {
                'high': {'max_issues': 3, 'block_commit': False},  # 开发环境更宽松
                'medium': {'max_issues': 10, 'block_commit': False},
                'low': {'max_issues': 50, 'block_commit': False},
            }
        }
    elif env == 'staging':
        return {
            'LOG_LEVEL': 'INFO',
            'SEVERITY_THRESHOLDS': {
                'high': {'max_issues': 1, 'block_commit': True},  # 预发布环境严格一些
                'medium': {'max_issues': 3, 'block_commit': False},
                'low': {'max_issues': 10, 'block_commit': False},
            }
        }
    else:  # production
        return {}  # 使用默认配置

# ============================================================================
# 配置验证和初始化
# ============================================================================

def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 验证文件大小限制
    if MAX_FILE_SIZE <= 0:
        errors.append("MAX_FILE_SIZE must be positive")
    
    # 验证超时设置
    if CHECK_TIMEOUT <= 0:
        errors.append("CHECK_TIMEOUT must be positive")
    
    # 验证并发配置
    if MAX_WORKERS <= 0:
        errors.append("MAX_WORKERS must be positive")
    
    # 验证阈值配置
    for severity, config in SEVERITY_THRESHOLDS.items():
        if config['max_issues'] < 0:
            errors.append(f"max_issues for {severity} must be non-negative")
    
    if errors:
        raise ValueError("Configuration validation failed: " + "; ".join(errors))

def initialize_config():
    """初始化配置，应用环境特定设置"""
    env_config = get_environment_config()
    
    # 更新全局配置
    globals().update(env_config)
    
    # 验证配置
    validate_config()
    
    # 创建必要的目录
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

# ============================================================================
# 配置导出
# ============================================================================

def get_config_dict():
    """获取完整的配置字典"""
    return {
        'HIGH_SEVERITY_PATTERNS': HIGH_SEVERITY_PATTERNS,
        'MEDIUM_SEVERITY_PATTERNS': MEDIUM_SEVERITY_PATTERNS,
        'LOW_SEVERITY_PATTERNS': LOW_SEVERITY_PATTERNS,
        'SUPPORTED_EXTENSIONS': SUPPORTED_EXTENSIONS,
        'EXCLUDED_PATHS': EXCLUDED_PATHS,
        'EXCLUDED_FILES': EXCLUDED_FILES,
        'MAX_FILE_SIZE': MAX_FILE_SIZE,
        'MAX_FILES_PER_CHECK': MAX_FILES_PER_CHECK,
        'CHECK_TIMEOUT': CHECK_TIMEOUT,
        'MAX_WORKERS': MAX_WORKERS,
        'USE_MULTIPROCESSING': USE_MULTIPROCESSING,
        'SEVERITY_THRESHOLDS': SEVERITY_THRESHOLDS,
        'RELAXED_RULES_FOR_TYPES': RELAXED_RULES_FOR_TYPES,
        'LOG_LEVEL': LOG_LEVEL,
        'LOG_FILE': LOG_FILE,
        'MAX_LOG_SIZE': MAX_LOG_SIZE,
        'LOG_BACKUP_COUNT': LOG_BACKUP_COUNT,
        'ENABLE_STATISTICS': ENABLE_STATISTICS,
        'STATISTICS_FILE': STATISTICS_FILE,
        'ENABLE_PERFORMANCE_MONITORING': ENABLE_PERFORMANCE_MONITORING,
        'PERFORMANCE_LOG_THRESHOLD': PERFORMANCE_LOG_THRESHOLD,
        'OUTPUT_CONFIG': OUTPUT_CONFIG,
        'COLOR_CONFIG': COLOR_CONFIG,
        'MESSAGE_TEMPLATES': MESSAGE_TEMPLATES,
    }

if __name__ == '__main__':
    # 配置测试
    try:
        initialize_config()
        print("[SUCCESS] 配置验证通过")
        print(f"[INFO] 当前环境: {os.getenv('ENVIRONMENT', 'production')}")
        print(f"[INFO] 日志级别: {LOG_LEVEL}")
        print(f"[INFO] 支持的文件类型: {len(SUPPORTED_EXTENSIONS)} 种")
        print(f"[INFO] 高严重性规则: {len(HIGH_SEVERITY_PATTERNS)} 条")
    except Exception as e:
        print(f"[ERROR] 配置验证失败: {e}")
        exit(1)