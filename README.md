# 数字图像处理软件

基于PySide6和OpenCV开发的数字图像处理软件，提供图像加载、显示、处理和保存等功能。

## 功能特点

- 图像加载和保存
- 基本图像处理（亮度/对比度调整、灰度转换等）
- 高级图像处理（滤波、边缘检测等）
- 实时预览
- 用户友好的界面

## 安装要求

- Python 3.8+
- PySide6
- OpenCV
- NumPy

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository-url]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 使用说明

1. 通过"文件"菜单或工具栏按钮打开图像
2. 使用工具栏或菜单选择图像处理功能
3. 调整处理参数
4. 保存处理结果

## 开发说明

项目采用MVC架构：
- models/: 数据模型
- views/: 视图组件
- controllers/: 控制器
- utils/: 工具函数
- resources/: 资源文件

## 许可证

MIT License 