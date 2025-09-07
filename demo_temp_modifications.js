// 这是一个演示文件，用于测试代码变更追踪系统

function demoFunction() {
    console.log('这是一个临时调试输出'); // 临时调试代码
    
    // TODO: 这里需要添加错误处理逻辑
    const result = processData();
    
    // FIXME: 这个逻辑有问题，需要修复
    if (result) {
        console.error('调试：结果处理', result);
        return result;
    }
    
    // HACK: 临时解决方案，后续需要重构
    return 'default_value';
}

function processData() {
    // XXX: 这个函数实现不完整
    console.warn('警告：临时实现');
    return Math.random() > 0.5;
}

// DEBUG: 测试代码，生产环境需要删除
if (process.env.NODE_ENV === 'development') {
    console.log('开发模式调试信息');
}

export { demoFunction };