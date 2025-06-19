"""
测试导入语句
"""
import os
import sys

# 打印当前目录
print("当前目录:", os.getcwd())

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("项目根目录:", project_root)

# 将项目根目录添加到sys.path
sys.path.insert(0, project_root)
print("sys.path:", sys.path)

# 尝试导入 - 方法1：直接导入
try:
    from models.image_model import ImageModel
    print("方法1 导入成功!")
except ImportError as e:
    print("方法1 导入失败:", e)

# 尝试导入 - 方法2：使用完整路径
try:
    import models.image_model
    print("方法2 导入成功!")
except ImportError as e:
    print("方法2 导入失败:", e)

# 尝试导入 - 方法3：使用系统路径
try:
    sys.path.append(os.path.join(project_root, "models"))
    import image_model
    print("方法3 导入成功!")
except ImportError as e:
    print("方法3 导入失败:", e)

# 尝试导入 - 方法4：使用相对导入
try:
    from ..models.image_model import ImageModel
    print("方法4 导入成功!")
except (ImportError, ValueError) as e:
    print("方法4 导入失败:", e)

# 尝试导入 - 方法5：使用exec动态导入
try:
    code = f"import sys; sys.path.insert(0, '{project_root}'); from models.image_model import ImageModel"
    exec(code)
    print("方法5 导入成功!")
except Exception as e:
    print("方法5 导入失败:", e) 