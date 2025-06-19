"""
测试直接导入
"""
import os
import sys
import importlib.util

# 打印当前目录
print("当前目录:", os.getcwd())

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("项目根目录:", project_root)

# 直接导入模块
def import_module_from_file(module_name, file_path):
    """从文件路径导入模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 尝试导入model_module
try:
    model_file = os.path.join(project_root, "models", "image_model.py")
    print("尝试从文件导入:", model_file)
    model_module = import_module_from_file("image_model", model_file)
    if model_module:
        print("image_model.py 导入成功!")
        print("可用类:", [name for name in dir(model_module) if not name.startswith("_")])
        # 尝试创建ImageModel实例
        ImageModel = getattr(model_module, "ImageModel")
        model = ImageModel()
        print("ImageModel实例创建成功!")
    else:
        print("导入模块失败")
except Exception as e:
    print("导入或实例化失败:", e) 