"""
改进版测试导入工具 - 解决模块导入问题

此模块提供了一个在测试环境中正确导入项目模块的机制，解决路径和导入问题。
"""
import os
import sys
import importlib.util
from pathlib import Path

# 打印当前目录
print("当前目录:", os.getcwd())

# 获取项目根目录
project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("项目根目录:", project_root)

# 将项目根目录添加到sys.path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
# 添加app目录到sys.path
app_dir = project_root / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))
    
# 添加所有主要模块目录到系统路径
for module_dir in ["models", "views", "controllers", "utils"]:
    module_path = project_root / module_dir
    if module_path.exists() and str(module_path) not in sys.path:
        sys.path.insert(0, str(module_path))

print("系统路径:", sys.path)

def import_module_from_file(module_name, file_path):
    """从文件路径导入模块"""
    print(f"尝试从文件导入: {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        print(f"{module_name} 导入成功!")
        return module
    except ImportError as e:
        print(f"{module_name} 导入失败: {e}")
        return None
        
def create_module_imports():
    """创建关键模块的导入"""
    # 导入config模块
    config_file = project_root / "app" / "config.py"
    if config_file.exists():
        config_module = import_module_from_file("config", str(config_file))
        if config_module:
            sys.modules["app.config"] = config_module
            print("创建了app.config模块!")
            
    # 导入image_utils模块
    image_utils_file = project_root / "utils" / "image_utils.py"
    if image_utils_file.exists():
        image_utils_module = import_module_from_file("image_utils", str(image_utils_file))
        if image_utils_module:
            sys.modules["utils.image_utils"] = image_utils_module
            print("创建了utils.image_utils模块!")
    
    # 导入image_model模块
    image_model_file = project_root / "models" / "image_model.py"
    if image_model_file.exists():
        image_model_module = import_module_from_file("image_model", str(image_model_file))
        if image_model_module:
            sys.modules["models.image_model"] = image_model_module
            print("创建了models.image_model模块!")
            # 尝试创建模型实例
            if hasattr(image_model_module, "ImageModel"):
                print("可用类:", image_model_module.__dir__())
                try:
                    model = image_model_module.ImageModel()
                    print("ImageModel实例创建成功!")
                except Exception as e:
                    print(f"创建ImageModel实例失败: {e}")
                
    # 导入image_controller模块
    controller_file = project_root / "controllers" / "image_controller.py"
    if controller_file.exists():
        controller_module = import_module_from_file("image_controller", str(controller_file))
        if controller_module:
            sys.modules["controllers.image_controller"] = controller_module
            print("创建了controllers.image_controller模块!")
            
    # 导入image_view模块
    view_file = project_root / "views" / "image_view.py"
    if view_file.exists():
        view_module = import_module_from_file("image_view", str(view_file))
        if view_module:
            sys.modules["views.image_view"] = view_module
            print("创建了views.image_view模块!")

# 执行导入
create_module_imports()
 