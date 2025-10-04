# 强制本地测试系统 - 调试维护指南

## 🎯 基于架构的问题诊断方法

### 诊断流程图

```
问题发生 → 确定层次 → 检查组件 → 分析日志 → 定位根因 → 实施修复
     │         │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼         ▼
 用户反馈   架构层次   组件状态   日志分析   问题定位   问题解决
```

### 1. 架构层次诊断法

根据[ARCHITECTURE.md](./ARCHITECTURE.md)中的四层验证架构，按层次排查问题：

```
┌─────────────────────────────────────────┐
│          问题层次诊断矩阵               │
├─────────────────────────────────────────┤
│ Layer 1: 语法层问题                     │
│ ├─ GitHub Actions语法错误               │
│ ├─ act工具不可用或版本问题              │
│ └─ YAML/JSON格式错误                    │
│                                         │
│ Layer 2: 环境层问题                     │
│ ├─ Docker服务未启动                     │
│ ├─ docker-compose配置错误               │
│ └─ 服务依赖缺失                         │
│                                         │
│ Layer 3: 功能层问题                     │
│ ├─ 后端单元测试失败                     │
│ ├─ 前端构建错误                         │
│ └─ 集成测试超时                         │
│                                         │
│ Layer 4: 差异层问题                     │
│ ├─ 环境配置不一致                       │
│ ├─ 跨平台兼容性问题                     │
│ └─ npm workspaces结构异常               │
└─────────────────────────────────────────┘
```

### 2. 组件状态检查

基于[FILES_STRUCTURE.md](./FILES_STRUCTURE.md)中的文件依赖关系，检查各组件状态：

```bash
#!/bin/bash
# scripts/system_health_check.sh

echo "🏥 强制本地测试系统健康检查"
echo "="*50

# 1. 核心文件检查
check_core_files() {
    echo "📁 检查核心文件..."

    local core_files=(
        "scripts/git-guard.sh"
        "scripts/local_test_passport.py"
        "scripts/one_click_test.sh"
        "scripts/setup_cursor_protection.sh"
    )

    for file in "${core_files[@]}"; do
        if [[ -f "$file" && -x "$file" ]]; then
            echo "✅ $file - 存在且可执行"
        elif [[ -f "$file" ]]; then
            echo "⚠️ $file - 存在但不可执行"
            chmod +x "$file"
            echo "🔧 已修复执行权限"
        else
            echo "❌ $file - 缺失"
        fi
    done
}

# 2. 依赖工具检查
check_dependencies() {
    echo "🔧 检查依赖工具..."

    # Docker
    if docker info &> /dev/null; then
        echo "✅ Docker - 运行正常"
    else
        echo "❌ Docker - 服务异常"
    fi

    # Python
    if command -v python3 &> /dev/null; then
        echo "✅ Python3 - $(python3 --version)"
    elif command -v python &> /dev/null; then
        echo "✅ Python - $(python --version)"
    else
        echo "❌ Python - 未找到"
    fi

    # Git
    if command -v git &> /dev/null; then
        echo "✅ Git - $(git --version)"
    else
        echo "❌ Git - 未找到"
    fi

    # act (可选)
    if command -v act &> /dev/null; then
        echo "✅ act - $(act --version)"
    else
        echo "⚠️ act - 未安装 (可选工具)"
    fi
}

# 3. 通行证状态检查
check_passport_status() {
    echo "🎫 检查通行证状态..."

    if [[ -f ".git/local_test_passport.json" ]]; then
        echo "📄 通行证文件存在"
        python3 scripts/local_test_passport.py --check
    else
        echo "📝 无通行证文件"
    fi
}

# 运行所有检查
check_core_files
check_dependencies
check_passport_status
```

## 🔍 常见问题诊断

### 1. 推送被拦截问题

#### 问题表现

```
🎫🎫🎫 本地测试通行证验证失败！🎫🎫🎫
❌ 检测到推送操作，但未找到有效的本地测试通行证！
```

#### 诊断步骤

```bash
# 1. 检查通行证状态
python3 scripts/local_test_passport.py --check

# 2. 检查Git Guard是否正常工作
bash scripts/git-guard.sh --version

# 3. 查看拦截日志
tail -20 logs/git-no-verify-attempts.log

# 4. 手动生成通行证
python3 scripts/local_test_passport.py --force
```

#### 根因分析

```python
def diagnose_passport_failure():
    """诊断通行证验证失败的原因"""

    # 检查文件是否存在
    passport_file = ".git/local_test_passport.json"
    if not os.path.exists(passport_file):
        return "通行证文件不存在，需要运行本地测试"

    # 检查文件格式
    try:
        with open(passport_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return "通行证文件格式损坏，需要重新生成"

    # 检查过期时间
    expire_time = datetime.fromisoformat(data.get("expires_at"))
    if datetime.now() > expire_time:
        return f"通行证已过期 (过期时间: {expire_time})"

    # 检查Git状态
    current_hash = get_git_hash()
    stored_hash = data.get("git_hash")
    if current_hash != stored_hash:
        return "代码已修改，通行证失效"

    return "通行证验证逻辑异常，需要深入排查"
```

### 2. 本地测试失败问题

#### Docker相关问题

```bash
# 诊断Docker问题
diagnose_docker_issues() {
    echo "🐳 诊断Docker问题..."

    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        echo "❌ Docker服务未运行"
        echo "💡 解决方案："
        echo "   Windows: 启动Docker Desktop"
        echo "   Linux: sudo systemctl start docker"
        return 1
    fi

    # 检查docker-compose配置
    if ! docker-compose config &> /dev/null; then
        echo "❌ docker-compose配置有误"
        echo "💡 运行以下命令查看详细错误："
        echo "   docker-compose config"
        return 1
    fi

    # 检查镜像和容器状态
    echo "📊 Docker状态摘要："
    echo "   镜像数量: $(docker images -q | wc -l)"
    echo "   运行容器: $(docker ps -q | wc -l)"
    echo "   停止容器: $(docker ps -aq | wc -l)"

    # 检查磁盘空间
    local disk_usage=$(docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}")
    echo "💾 Docker磁盘使用："
    echo "$disk_usage"
}
```

#### Python环境问题

```bash
# 诊断Python问题
diagnose_python_issues() {
    echo "🐍 诊断Python问题..."

    # 检查Python可用性
    local python_cmd=""
    if command -v python3 &> /dev/null; then
        python_cmd="python3"
    elif command -v python &> /dev/null; then
        python_cmd="python"
    else
        echo "❌ 未找到Python"
        echo "💡 请安装Python 3.7+"
        return 1
    fi

    echo "✅ Python命令: $python_cmd"
    echo "📝 Python版本: $($python_cmd --version)"

    # 检查必要模块
    local required_modules=("json" "hashlib" "subprocess" "datetime" "pathlib" "argparse")
    for module in "${required_modules[@]}"; do
        if $python_cmd -c "import $module" &> /dev/null; then
            echo "✅ 模块 $module 可用"
        else
            echo "❌ 模块 $module 不可用"
        fi
    done

    # 检查脚本语法
    if $python_cmd -m py_compile scripts/local_test_passport.py; then
        echo "✅ local_test_passport.py 语法正确"
    else
        echo "❌ local_test_passport.py 语法错误"
    fi
}
```

### 3. 性能问题诊断

#### 测试执行慢的问题

```python
# scripts/performance_analyzer.py
import time
import json
from datetime import datetime

class PerformanceAnalyzer:
    def __init__(self):
        self.checkpoints = {}
        self.start_time = None

    def start_analysis(self):
        self.start_time = time.time()
        self.checkpoint("analysis_start")

    def checkpoint(self, name):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.checkpoints[name] = {
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
            print(f"⏱️ {name}: {elapsed:.2f}s")

    def analyze_bottlenecks(self):
        """分析性能瓶颈"""
        if len(self.checkpoints) < 2:
            return "数据不足，无法分析"

        bottlenecks = []
        checkpoints = list(self.checkpoints.items())

        for i in range(1, len(checkpoints)):
            prev_time = checkpoints[i-1][1]["elapsed"]
            curr_time = checkpoints[i][1]["elapsed"]
            step_time = curr_time - prev_time

            if step_time > 30:  # 超过30秒的步骤
                bottlenecks.append({
                    "step": checkpoints[i][0],
                    "duration": step_time,
                    "percentage": (step_time / curr_time) * 100
                })

        return bottlenecks

    def generate_report(self):
        """生成性能报告"""
        total_time = time.time() - self.start_time
        bottlenecks = self.analyze_bottlenecks()

        report = {
            "total_duration": total_time,
            "checkpoints": self.checkpoints,
            "bottlenecks": bottlenecks,
            "recommendations": self._get_recommendations(bottlenecks)
        }

        # 保存报告
        with open("performance_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report

    def _get_recommendations(self, bottlenecks):
        """基于瓶颈分析给出优化建议"""
        recommendations = []

        for bottleneck in bottlenecks:
            step = bottleneck["step"]
            duration = bottleneck["duration"]

            if "docker" in step.lower():
                recommendations.append(
                    f"Docker操作慢({duration:.1f}s): 考虑使用Docker镜像缓存或升级硬件"
                )
            elif "test" in step.lower():
                recommendations.append(
                    f"测试执行慢({duration:.1f}s): 考虑使用--quick模式或优化测试用例"
                )
            elif "npm" in step.lower():
                recommendations.append(
                    f"NPM操作慢({duration:.1f}s): 考虑使用镜像源或npm ci --cache"
                )

        return recommendations
```

## 📊 日志分析方法

### 1. 日志文件结构

基于[IMPLEMENTATION.md](./IMPLEMENTATION.md)中的日志格式，分析不同类型的日志：

```bash
# 日志分析脚本
analyze_logs() {
    echo "📊 分析系统日志..."

    # 1. Git拦截日志分析
    if [[ -f "logs/git-no-verify-attempts.log" ]]; then
        echo "🚫 Git拦截统计："
        echo "   总拦截次数: $(wc -l < logs/git-no-verify-attempts.log)"
        echo "   最近拦截: $(tail -1 logs/git-no-verify-attempts.log)"

        echo "📈 拦截类型分布："
        grep -o '| [^|]* |' logs/git-no-verify-attempts.log | sort | uniq -c | sort -nr
    fi

    # 2. 通行证操作日志分析
    if [[ -f "logs/local_test_passport.log" ]]; then
        echo "🎫 通行证操作统计："
        echo "   总操作次数: $(wc -l < logs/local_test_passport.log)"
        echo "   成功生成: $(grep -c '通行证已生成' logs/local_test_passport.log)"
        echo "   验证失败: $(grep -c '验证失败' logs/local_test_passport.log)"
    fi
}

# 错误模式识别
identify_error_patterns() {
    echo "🔍 识别错误模式..."

    # 合并所有日志文件
    local all_logs="/tmp/all_force_local_test_logs.txt"
    cat logs/*.log > "$all_logs" 2>/dev/null || touch "$all_logs"

    # 常见错误模式
    local error_patterns=(
        "Docker.*not.*running"
        "Python.*not.*found"
        "Permission.*denied"
        "No.*such.*file"
        "Timeout.*expired"
        "Connection.*refused"
    )

    for pattern in "${error_patterns[@]}"; do
        local count=$(grep -c "$pattern" "$all_logs")
        if [[ $count -gt 0 ]]; then
            echo "⚠️ 发现 $count 次错误模式: $pattern"
            echo "   最近发生: $(grep "$pattern" "$all_logs" | tail -1)"
        fi
    done

    rm -f "$all_logs"
}
```

### 2. 实时监控

```bash
# 实时日志监控
monitor_system_logs() {
    echo "👁️ 启动实时日志监控..."

    # 创建命名管道用于多文件监控
    local fifo="/tmp/force_local_test_monitor"
    mkfifo "$fifo"

    # 监控多个日志文件
    tail -f logs/git-no-verify-attempts.log logs/local_test_passport.log 2>/dev/null | \
    while read line; do
        timestamp=$(date '+%H:%M:%S')

        # 根据日志内容着色输出
        if echo "$line" | grep -q "ERROR\|FAILED\|❌"; then
            echo -e "\033[31m[$timestamp] $line\033[0m"  # 红色
        elif echo "$line" | grep -q "SUCCESS\|✅"; then
            echo -e "\033[32m[$timestamp] $line\033[0m"  # 绿色
        elif echo "$line" | grep -q "WARNING\|⚠️"; then
            echo -e "\033[33m[$timestamp] $line\033[0m"  # 黄色
        else
            echo "[$timestamp] $line"
        fi
    done

    rm -f "$fifo"
}
```

## 🔧 系统维护

### 1. 定期维护检查清单

```bash
# scripts/maintenance_checklist.sh
run_maintenance_checklist() {
    echo "🔧 执行系统维护检查..."

    local checklist=(
        "check_file_permissions:检查文件权限"
        "cleanup_old_logs:清理旧日志"
        "verify_git_hooks:验证Git钩子"
        "test_core_functions:测试核心功能"
        "check_disk_usage:检查磁盘使用"
        "update_dependencies:检查依赖更新"
    )

    for item in "${checklist[@]}"; do
        local func_name="${item%:*}"
        local description="${item#*:}"

        echo "📋 $description..."
        if $func_name; then
            echo "✅ $description - 完成"
        else
            echo "❌ $description - 失败"
        fi
    done
}

# 维护函数实现
check_file_permissions() {
    find scripts/ -name "*.sh" -not -perm -u+x -exec chmod +x {} \;
    find scripts/ -name "*.py" -not -perm -u+x -exec chmod +x {} \;
    return 0
}

cleanup_old_logs() {
    # 保留最近7天的日志
    find logs/ -name "*.log" -mtime +7 -exec rm {} \;
    return 0
}

verify_git_hooks() {
    if [[ -f ".git/hooks/post-merge" && -x ".git/hooks/post-merge" ]]; then
        return 0
    else
        return 1
    fi
}

test_core_functions() {
    # 快速功能测试
    timeout 60 bash scripts/one_click_test.sh --act-only
    return $?
}

check_disk_usage() {
    local usage=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $usage -gt 90 ]]; then
        echo "⚠️ 磁盘使用率过高: ${usage}%"
        return 1
    fi
    return 0
}

update_dependencies() {
    # 检查Docker镜像更新
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}" | head -10
    return 0
}
```

### 2. 自动修复机制

```bash
# scripts/auto_repair.sh
auto_repair_common_issues() {
    echo "🔨 启动自动修复..."

    # 修复文件权限
    chmod +x scripts/*.sh scripts/*.py 2>/dev/null

    # 重新创建便捷命令
    if [[ ! -f "test" || ! -x "test" ]]; then
        cat > test << 'EOF'
#!/bin/bash
bash scripts/one_click_test.sh "$@"
EOF
        chmod +x test
        echo "🔧 已修复 test 命令"
    fi

    # 修复通行证文件权限
    if [[ -f ".git/local_test_passport.json" ]]; then
        chmod 600 .git/local_test_passport.json
    fi

    # 清理损坏的通行证文件
    if [[ -f ".git/local_test_passport.json" ]]; then
        if ! python3 -c "import json; json.load(open('.git/local_test_passport.json'))" 2>/dev/null; then
            rm .git/local_test_passport.json
            echo "🔧 已清理损坏的通行证文件"
        fi
    fi

    # 修复日志目录
    mkdir -p logs
    chmod 755 logs

    echo "✅ 自动修复完成"
}
```

## 📈 性能优化建议

### 1. 测试执行优化

```bash
# 优化测试执行速度
optimize_test_performance() {
    echo "⚡ 优化测试性能..."

    # 1. Docker缓存优化
    echo "🐳 优化Docker缓存..."
    docker system prune -f --volumes

    # 2. npm缓存优化
    echo "📦 优化npm缓存..."
    npm cache clean --force
    npm config set cache ~/.npm-cache

    # 3. Python包缓存
    echo "🐍 优化Python缓存..."
    pip3 cache purge 2>/dev/null || true

    # 4. 并行测试配置
    echo "⚡ 配置并行测试..."
    export DOCKER_PARALLEL=true
    export NPM_CONCURRENT=true
}
```

### 2. 系统资源监控

```python
# scripts/resource_monitor.py
import psutil
import time
import json
from datetime import datetime

class ResourceMonitor:
    def __init__(self):
        self.metrics = []

    def collect_metrics(self):
        """收集系统资源指标"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('.').percent,
            "docker_containers": self._count_docker_containers()
        }

        self.metrics.append(metric)
        return metric

    def _count_docker_containers(self):
        """统计Docker容器数量"""
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "ps", "-q"],
                capture_output=True, text=True
            )
            return len(result.stdout.strip().split('\n'))
        except:
            return 0

    def analyze_performance_issues(self):
        """分析性能问题"""
        if not self.metrics:
            return []

        issues = []
        latest = self.metrics[-1]

        if latest["cpu_percent"] > 80:
            issues.append("CPU使用率过高，建议关闭其他应用")

        if latest["memory_percent"] > 85:
            issues.append("内存使用率过高，建议重启Docker")

        if latest["disk_usage"] > 90:
            issues.append("磁盘空间不足，建议清理Docker镜像")

        return issues

    def save_report(self, filename="resource_report.json"):
        """保存性能报告"""
        report = {
            "collected_at": datetime.now().isoformat(),
            "metrics": self.metrics,
            "issues": self.analyze_performance_issues(),
            "recommendations": self._get_recommendations()
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def _get_recommendations(self):
        """获取优化建议"""
        recommendations = [
            "定期运行 docker system prune 清理未使用的镜像",
            "使用 --quick 模式进行日常开发测试",
            "关闭不必要的后台应用释放资源",
            "考虑升级硬件配置（SSD、更大内存）"
        ]
        return recommendations
```

---

**调试维护核心原则**:

- **层次化诊断**: 按架构层次逐级排查问题
- **数据驱动**: 基于日志和指标进行问题分析
- **预防性维护**: 定期检查，防患于未然
- **自动化修复**: 常见问题自动识别和修复
- **文档驱动**: 所有诊断过程都有详细记录
