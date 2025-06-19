# ImagePro 开发者指南

## 简介

本指南面向希望参与ImagePro开发或基于ImagePro进行二次开发的开发者，详细介绍了ImagePro的架构设计、代码组织、开发规范和扩展方法。

## 项目架构

ImagePro采用MVC（Model-View-Controller）架构设计，各组件职责明确，代码模块化程度高。

### 架构图

```
+-------------+      +---------------+      +--------------+
|             |      |               |      |              |
|    Model    <------+  Controller   <------+    View      |
|             |      |               |      |              |
+-------------+      +---------------+      +--------------+
       ^                    ^                     ^
       |                    |                     |
       v                    v                     v
+-------------+      +---------------+      +--------------+
|   image     |      |    image      |      |    UI        |
|   data      |      |  processing   |      | components   |
+-------------+      +---------------+      +--------------+
```

### 组件说明

1. **Model（模型）**：
   - 负责数据的存储、访问和管理
   - 处理图像的加载、保存和历史记录
   - 独立于用户界面，提供数据访问API

2. **Controller（控制器）**：
   - 连接模型和视图
   - 处理用户输入，调用模型进行数据处理
   - 协调模型和视图的交互

3. **View（视图）**：
   - 负责界面显示和用户交互
   - 将模型数据可视化
   - 接收用户输入并发送到控制器

## 代码组织

### 目录结构

```
ImagePro/
│
├── main.py                  # 应用程序入口
├── requirements.txt         # 项目依赖
├── README.md                # 项目说明
│
├── app/                     # 应用程序核心
│   ├── __init__.py
│   ├── main_window.py       # 主窗口类
│   └── config.py            # 应用配置
│
├── models/                  # 数据模型
│   ├── __init__.py
│   └── image_model.py       # 图像数据模型
│
├── controllers/             # 控制器
│   ├── __init__.py
│   └── image_controller.py  # 图像处理控制器
│
├── views/                   # 视图组件
│   ├── __init__.py
│   ├── image_view.py        # 图像显示组件
│   ├── side_panel.py        # 侧边栏组件
│   ├── toolbar.py           # 工具栏（可选）
│   └── dialogs/             # 对话框
│       ├── __init__.py
│       └── ... 
│
├── utils/                   # 工具函数
│   ├── __init__.py
│   ├── image_utils.py       # 图像处理工具
│   └── qt_utils.py          # Qt相关工具函数
│
├── resources/               # 资源文件
│   ├── icons/               # 图标
│   └── styles/              # 样式表
│
├── tests/                   # 测试代码
│   ├── models/              # 模型测试
│   ├── controllers/         # 控制器测试
│   ├── views/               # 视图测试
│   └── utils/               # 工具函数测试
│
└── docs/                    # 文档
    ├── user_manual.md       # 用户手册
    ├── api_reference.md     # API参考文档
    └── developer_guide.md   # 开发者指南
```

### 核心模块及其职责

1. **app/main_window.py**：
   - 定义主窗口类，组织整个应用的UI结构
   - 创建菜单、工具栏和状态栏
   - 连接UI组件与控制器

2. **models/image_model.py**：
   - 管理图像数据和历史记录
   - 提供图像的加载、保存和处理接口
   - 发出信号通知视图更新

3. **controllers/image_controller.py**：
   - 封装图像处理逻辑
   - 将用户操作转换为对模型的调用
   - 协调模型和视图的数据交换

4. **views/image_view.py**：
   - 显示图像和处理结果
   - 处理图像缩放、平移等交互
   - 捕获用户鼠标和键盘事件

5. **views/side_panel.py**：
   - 提供图像处理参数的调整界面
   - 包含各种控制面板（亮度/对比度、几何变换等）
   - 发送处理请求信号

6. **utils/image_utils.py**：
   - 提供底层图像处理函数
   - 封装OpenCV等图像处理库的功能
   - 独立于UI，便于测试和复用

## 开发规范

### 编码风格

ImagePro遵循PEP 8编码规范，主要规则包括：
- 使用4个空格缩进，不使用制表符
- 每行代码最大长度为79个字符
- 函数和类定义之间空两行
- 使用下划线分隔的小写字母命名变量和函数
- 使用驼峰式命名类
- 类定义的空行间隔为1行

### 注释规范

- 每个模块、类和方法都应有清晰的文档字符串（docstring）
- 文档字符串使用三重引号（"""）
- 方法文档字符串应包括参数和返回值的描述
- 复杂逻辑应有行内注释说明

示例：
```python
def rotate_image(image, angle, center=None, scale=1.0, expand=False):
    """旋转图像
    
    Args:
        image: 输入图像
        angle: 旋转角度（度），正值表示逆时针旋转
        center: 旋转中心，默认为图像中心
        scale: 缩放比例，默认为1.0
        expand: 是否扩展图像以包含整个旋转后的图像，默认为False
    
    Returns:
        旋转后的图像
    """
    # 函数实现...
```

### 错误处理

- 使用异常处理捕获可能的错误
- 避免使用空except子句
- 在合适的地方记录和显示错误信息
- 使用`error_occurred`信号传递错误信息

### 代码质量

- 编写单元测试验证每个功能
- 使用版本控制（如Git）管理代码
- 在添加新功能前，确保现有测试通过
- 避免重复代码，提取共同功能到工具函数

## 扩展指南

### 添加新的图像处理功能

1. **在utils/image_utils.py中添加处理函数**：
```python
def apply_new_effect(image, param1, param2):
    """应用新效果
    
    Args:
        image: 输入图像
        param1: 参数1
        param2: 参数2
    
    Returns:
        处理后的图像
    """
    # 处理逻辑
    return processed_image
```

2. **在ImageController中添加方法**：
```python
def apply_new_effect(self, param1, param2):
    """应用新效果
    
    Args:
        param1: 参数1
        param2: 参数2
    
    Returns:
        bool: 操作是否成功
    """
    def operation(image):
        return apply_new_effect(image, param1, param2)
    
    return self.image_model.apply_operation(operation)
```

3. **创建控制面板**：
   - 在views/side_panel.py中添加新的面板类
   - 定义参数控件和布局
   - 连接信号和槽

4. **更新主窗口**：
   - 在MainWindow中注册新功能
   - 处理新的操作请求

### 添加新的视图组件

1. **创建视图类**：
   - 继承适当的Qt类（如QWidget、QGraphicsView等）
   - 实现必要的方法和信号

2. **集成到主窗口**：
   - 在MainWindow中添加新视图
   - 连接信号和槽

## 测试指南

### 单元测试

- 使用Python的unittest框架
- 为每个模块创建测试类
- 测试所有公共方法和边界情况
- 使用模拟对象（mock）隔离依赖

示例：
```python
class TestImageUtils(unittest.TestCase):
    def test_rotate_image(self):
        # 准备测试图像
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        # ... 设置测试图像 ...
        
        # 调用被测函数
        result = rotate_image(test_image, 45)
        
        # 验证结果
        self.assertEqual(result.shape, (142, 142, 3))
        # ... 更多断言 ...
```

### 运行测试

```bash
# 运行所有测试
python -m unittest discover

# 运行特定测试文件
python -m unittest tests.utils.test_image_utils
```

## 常见问题和解决方案

### 内存管理

图像处理可能消耗大量内存，特别是处理大尺寸图像时：

1. **使用引用计数和智能缓存**：
   - ImageModel已实现引用计数机制
   - 定期清理不再使用的图像数据

2. **限制历史记录大小**：
   - 通过config.py中的'performance.cache_size'配置项控制

3. **大图像优化**：
   - 处理大图像前先清理内存
   - 考虑添加图像缩放预处理

### Qt与多线程

Qt GUI操作通常应在主线程中进行：

1. **使用信号-槽机制跨线程通信**：
   - 避免直接在工作线程中更新UI
   - 使用信号将结果传递给主线程

2. **处理进度反馈**：
   - 添加进度信号通知UI更新进度条
   - 使用QueuedConnection连接跨线程信号

### 图像格式转换

OpenCV和Qt使用不同的图像格式：

1. **OpenCV使用BGR格式，而Qt使用RGB格式**：
   - 加载时将BGR转换为RGB
   - 保存时将RGB转换为BGR

2. **数据共享优化**：
   - 使用to_qimage方法优化转换
   - 避免不必要的数据复制

## 发布与部署

### 创建发布版本

1. **添加版本信息**：
   - 在config.py中定义版本号
   - 更新README.md和文档

2. **打包应用**：
   - 使用PyInstaller创建独立可执行文件
   - 包含所有必要的资源和依赖

### 部署步骤

1. **准备环境**：
   - 确保所有依赖已安装
   - 检查操作系统兼容性

2. **分发应用**：
   - 提供安装程序或便携版
   - 包含用户手册和示例

## 贡献指南

欢迎对ImagePro项目做出贡献：

1. **提交问题**：
   - 报告bug或提出功能请求
   - 提供清晰的复现步骤

2. **提交代码**：
   - Fork项目仓库
   - 创建新分支开发功能
   - 提交Pull Request

3. **文档贡献**：
   - 改进现有文档
   - 添加教程或示例

## 联系方式

如有任何问题或建议，请通过以下方式联系：

- 项目仓库：[GitHub链接]
- 电子邮件：[联系邮箱] 