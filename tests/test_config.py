"""
测试配置文件

本文件定义了测试框架的配置项，包括哪些测试可以运行，哪些测试需要跳过。
"""

# 定义测试模块配置
test_modules = {
    # 模型测试模块配置
    "models": {
        "enabled": True,  # 是否启用模型测试
        "skip_tests": []  # 跳过的测试类或方法名
    },
    
    # 控制器测试模块配置
    "controllers": {
        "enabled": True,  # 是否启用控制器测试
        "skip_tests": []  # 跳过的测试类或方法名
    },
    
    # 视图测试模块配置
    "views": {
        "enabled": True,  # 是否启用视图测试
        "skip_tests": []  # 跳过的测试类或方法名
    },
    
    # 应用程序测试模块配置
    "app": {
        "enabled": False,  # 暂时不启用应用程序测试，因为main_window尚未完成
        "skip_tests": ["test_main_window"]  # 跳过的测试模块
    },
    
    # 工具类测试模块配置
    "utils": {
        "enabled": True,  # 是否启用工具类测试
        "skip_tests": []  # 跳过的测试类或方法名
    }
}

# 测试资源配置
test_resources = {
    "images_dir": "resources",  # 测试图像存储目录
    "sample_image": "test_image.png",  # 样例测试图像
}

# 测试框架配置
test_framework = {
    "verbose": 2,  # 测试输出的详细程度 (0-2)
    "fail_fast": False,  # 是否遇到第一个失败就停止
    "buffer": False,  # 是否缓冲测试输出
    "catch_break": False,  # 是否捕获中断
}

# 测试报告配置
test_reporting = {
    "generate_report": True,  # 是否生成测试报告
    "report_format": "text",  # 测试报告格式 (text, xml, html)
    "report_file": "test_results.txt",  # 测试报告文件名
}

def should_skip_test(module_name, test_name):
    """
    检查指定测试是否应该跳过
    
    Args:
        module_name (str): 模块名称
        test_name (str): 测试名称
        
    Returns:
        bool: 如果应该跳过则返回True，否则返回False
    """
    if module_name not in test_modules:
        return False
    
    module_config = test_modules[module_name]
    if not module_config["enabled"]:
        return True
    
    return test_name in module_config["skip_tests"] 