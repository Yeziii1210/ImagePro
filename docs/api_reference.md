# ImagePro API参考文档

## 概述

ImagePro采用模块化设计，代码组织清晰，主要包括以下几个模块：
- 模型（Model）：处理数据和业务逻辑
- 视图（View）：负责UI界面展示
- 控制器（Controller）：连接模型和视图
- 工具（Utils）：提供各种实用功能

本文档详细介绍了各个模块的API，方便开发者进行二次开发或功能扩展。

## 模型（models）

### ImageModel

`models/image_model.py`中的`ImageModel`类负责图像数据的存储和管理。

#### 主要属性

- `_original_image`: 原始图像数据（OpenCV格式，numpy数组）
- `_current_image`: 当前处理后的图像数据
- `_preview_image`: 预览状态下的图像数据
- `_history`: 历史记录队列
- `_history_index`: 当前历史记录索引

#### 主要方法

```python
# 加载图像
load_image(file_path: str) -> bool

# 保存图像
save_image(file_path: str) -> bool

# 应用图像处理操作（添加到历史记录）
apply_operation(operation_func: Callable, *args, **kwargs) -> bool

# 预览操作（不添加到历史记录）
preview_operation(operation_func: Callable, *args, **kwargs) -> bool

# 应用最后一次预览
apply_last_preview() -> bool

# 撤销操作
undo() -> bool

# 重做操作
redo() -> bool

# 重置图像到原始状态
reset() -> bool

# 转换为Qt图像格式
to_qimage(image=None) -> QImage

# 获取当前图像（Qt格式）
get_image() -> QImage

# 检查是否有图像
has_image() -> bool

# 检查是否可以撤销
can_undo() -> bool

# 检查是否可以重做
can_redo() -> bool

# 清理内存
clear_memory() -> None
```

#### 信号

- `image_changed`: 图像改变时发出
- `history_changed`: 历史记录改变时发出
- `error_occurred(str)`: 发生错误时发出，附带错误信息

## 视图（views）

### ImageView

`views/image_view.py`中的`ImageView`类负责图像的显示和交互。

#### 主要属性

- `_scene`: 图像场景
- `_pixmap_item`: 图像项
- `_scale_factor`: 缩放因子
- `_cache`: LRU缓存

#### 主要方法

```python
# 设置要显示的图像
set_image(image: QImage) -> None

# 调整视图适应图像
fit_in_view() -> None

# 获取指定区域的图像
get_image_region(rect: QRectF) -> QImage

# 获取当前变换
get_current_transform() -> QTransform

# 应用变换
apply_transform(transform: QTransform) -> None

# 清除缓存
clear_cache() -> None
```

#### 信号

- `image_changed`: 图像改变时发出

### SidePanel

`views/side_panel.py`中的`SidePanel`类提供图像处理功能的参数控制面板。

#### 主要属性

- `brightness_contrast_panel`: 亮度/对比度调整面板
- `geometry_transform_panel`: 几何变换面板

#### 主要方法

```python
# 设置UI
setup_ui() -> None
```

#### 信号

- `process_requested(str, dict)`: 请求处理操作时发出，含操作类型和参数
- `preview_requested(str, dict)`: 请求预览时发出，含操作类型和参数

## 控制器（controllers）

### ImageController

`controllers/image_controller.py`中的`ImageController`类负责处理图像处理操作。

#### 主要方法

```python
# 初始化控制器
__init__(image_model: ImageModel) -> None

# 调整亮度和对比度
adjust_brightness_contrast(brightness: int, contrast: float) -> bool

# 应用高斯模糊
apply_gaussian_blur(kernel_size: int, sigma: float) -> bool

# 应用中值滤波
apply_median_blur(kernel_size: int) -> bool

# 应用双边滤波
apply_bilateral_filter(d: int, sigma_color: float, sigma_space: float) -> bool

# 转换为灰度图
convert_to_grayscale() -> bool

# 应用阈值处理
apply_threshold(threshold: int, max_value: int, threshold_type: int) -> bool

# 应用自适应阈值处理
apply_adaptive_threshold(max_value: int, block_size: int, c: int) -> bool

# 旋转图像
rotate_image(angle: float, scale: float = 1.0, expand: bool = False) -> bool

# 翻转图像
flip_image(flip_code: int) -> bool

# 裁剪图像
crop_image(x: int, y: int, width: int, height: int) -> bool

# 预览亮度和对比度调整
preview_brightness_contrast(brightness: int, contrast: float) -> bool

# 预览裁剪效果
preview_crop_image(x: int, y: int, width: int, height: int) -> bool

# 预览旋转效果
preview_rotate_image(angle: float, scale: float = 1.0, expand: bool = False) -> bool

# 应用最后一次预览
apply_last_preview() -> bool
```

## 工具（utils）

### image_utils.py

`utils/image_utils.py`提供各种图像处理函数。

#### 主要函数

```python
# 调整亮度和对比度
adjust_brightness_contrast(image: np.ndarray, brightness: int = 0, contrast: float = 1.0) -> np.ndarray

# 应用高斯模糊
apply_gaussian_blur(image: np.ndarray, kernel_size: int = 3, sigma: float = 0) -> np.ndarray

# 应用中值滤波
apply_median_blur(image: np.ndarray, kernel_size: int = 3) -> np.ndarray

# 应用双边滤波
apply_bilateral_filter(image: np.ndarray, d: int = 9, sigma_color: float = 75, sigma_space: float = 75) -> np.ndarray

# 转换为灰度图
convert_to_grayscale(image: np.ndarray) -> np.ndarray

# 应用阈值处理
apply_threshold(image: np.ndarray, threshold: int = 127, max_value: int = 255, threshold_type: int = cv2.THRESH_BINARY) -> np.ndarray

# 应用自适应阈值处理
apply_adaptive_threshold(image: np.ndarray, max_value: int = 255, block_size: int = 11, c: int = 2) -> np.ndarray

# 旋转图像
rotate_image(image: np.ndarray, angle: float, center: tuple = None, scale: float = 1.0, expand: bool = False) -> np.ndarray

# 翻转图像
flip_image(image: np.ndarray, flip_code: int) -> np.ndarray

# 裁剪图像
crop_image(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray
```

## 应用主窗口（app）

### MainWindow

`app/main_window.py`中的`MainWindow`类是应用程序的主窗口。

#### 主要属性

- `image_model`: 图像数据模型
- `image_view`: 图像视图
- `image_controller`: 图像控制器
- `side_panel`: 侧边栏

#### 主要方法

```python
# 初始化
__init__() -> None

# 创建动作
_create_actions() -> None

# 创建菜单
_create_menus() -> None

# 创建工具栏
_create_toolbars() -> None

# 创建状态栏
_create_statusbar() -> None

# 连接信号和槽
_connect_signals() -> None

# 打开文件处理
_on_open() -> None

# 保存文件处理
_on_save() -> None

# 撤销操作处理
_on_undo() -> None

# 重做操作处理
_on_redo() -> None

# 处理操作请求
_on_process_requested(operation: str, parameters: dict) -> None

# 处理预览请求
_on_preview_requested(operation: str, parameters: dict) -> None

# 清理内存
_force_cleanup_memory() -> None
```

## 配置（app/config.py）

`app/config.py`中的`config`对象提供应用程序配置。

#### 主要配置项

```python
# 性能配置
'performance.cache_size': 100        # 历史记录缓存大小
'performance.auto_gc_threshold': 80  # 自动垃圾回收阈值（内存使用百分比）

# 图像处理配置
'image_processing.max_image_size': (10000, 10000)  # 最大图像尺寸
```

## 示例代码

### 加载和处理图像

```python
from models.image_model import ImageModel
from controllers.image_controller import ImageController

# 创建模型和控制器
model = ImageModel()
controller = ImageController(model)

# 加载图像
model.load_image('path/to/image.jpg')

# 处理图像
controller.adjust_brightness_contrast(10, 1.2)
controller.rotate_image(45, expand=True)

# 保存结果
model.save_image('path/to/result.png')
```

### 创建自定义图像处理函数

```python
import numpy as np
from models.image_model import ImageModel

# 自定义处理函数
def invert_colors(image):
    return 255 - image

# 使用模型应用自定义函数
model = ImageModel()
model.load_image('path/to/image.jpg')

# 使用apply_operation应用自定义函数
model.apply_operation(invert_colors)
``` 