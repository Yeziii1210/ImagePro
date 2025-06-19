"""
测试运行器 - 用于执行单元测试
"""
import os
import sys
import unittest
import argparse
import time
import importlib.util
from pathlib import Path

# 添加项目根目录到系统路径，确保能够正确导入应用模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 确保app.config模块可以被正确导入
app_dir = os.path.join(project_root, "app")
sys.path.insert(0, app_dir)

# 添加主要项目目录到路径
for module_dir in ["models", "views", "controllers", "utils"]:
    module_path = os.path.join(project_root, module_dir)
    if os.path.exists(module_path) and module_path not in sys.path:
        sys.path.insert(0, module_path)

print("系统路径:", sys.path)

# 导入自定义的模块导入工具
try:
    # 导入测试配置模块
    from test_import_with_config import import_module_from_file, create_module_imports
    
    # 预先导入所有必要的模块
    create_module_imports()
except Exception as e:
    print("预加载模块失败:", e)
    import traceback
    traceback.print_exc()

def discover_tests(test_dir=None, pattern="test_*.py"):
    """
    发现测试模块
    
    Args:
        test_dir (str): 测试目录路径，默认为当前目录
        pattern (str): 测试文件匹配模式
        
    Returns:
        unittest.TestSuite: 测试套件
    """
    if test_dir is None:
        test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 导入测试配置
    try:
        # 从测试配置中获取跳过的测试
        from test_config import test_modules, should_skip_test
    except ImportError:
        print("警告：未找到测试配置文件，将运行所有测试")
        test_modules = {}
        def should_skip_test(module_name, test_name):
            return False
    
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 发现测试
    suite = unittest.TestSuite()
    
    for dirpath, dirnames, filenames in os.walk(test_dir):
        # 获取相对于测试目录的路径
        rel_path = os.path.relpath(dirpath, test_dir)
        if rel_path == '.':
            module_name = ""
        else:
            module_name = rel_path.replace(os.path.sep, '.')
        
        # 检查模块是否应该被跳过
        if module_name in test_modules and not test_modules.get(module_name, {}).get("enabled", True):
            print(f"跳过模块: {module_name}")
            continue
        
        # 加载测试
        for filename in filenames:
            if filename.startswith("test_") and filename.endswith(".py"):
                # 获取测试名
                test_name = os.path.splitext(filename)[0]
                
                # 检查测试是否应该被跳过
                if should_skip_test(module_name, test_name):
                    print(f"跳过测试: {module_name}.{test_name}")
                    continue
                
                # 构建模块路径
                if module_name:
                    module_path = f"{module_name}.{test_name}"
                else:
                    module_path = test_name
                
                # 加载测试
                try:
                    tests = loader.loadTestsFromName(module_path)
                    suite.addTest(tests)
                except Exception as e:
                    print(f"加载测试失败 {module_path}: {e}")
    
    return suite

def run_tests(args):
    """
    运行测试
    
    Args:
        args: 命令行参数
    """
    start_time = time.time()
    
    # 发现测试
    suite = discover_tests(args.test_dir, args.pattern)
    
    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=args.verbosity)
    
    # 运行测试
    result = runner.run(suite)
    
    # 输出测试结果
    print(f"\n测试完成，耗时: {time.time() - start_time:.2f}秒")
    print(f"运行测试: {result.testsRun}个")
    print(f"通过测试: {result.testsRun - len(result.failures) - len(result.errors)}个")
    print(f"失败测试: {len(result.failures)}个")
    print(f"错误测试: {len(result.errors)}个")
    
    # 返回测试结果
    return result

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行单元测试")
    parser.add_argument("--test-dir", help="测试目录路径", default=None)
    parser.add_argument("--pattern", help="测试文件匹配模式", default="test_*.py")
    parser.add_argument("-v", "--verbosity", help="输出详细程度", type=int, default=2)
    args = parser.parse_args()
    
    result = run_tests(args)
    
    # 返回测试结果码
    sys.exit(not result.wasSuccessful())

if __name__ == "__main__":
    main() 