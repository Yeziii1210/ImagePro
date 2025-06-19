"""
亮度/对比度对话框模块
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QDoubleSpinBox, QPushButton)
from PySide6.QtCore import Qt, Signal

class BrightnessDialog(QDialog):
    """亮度/对比度对话框类"""
    
    # 信号定义
    parameters_changed = Signal(int, float)  # 参数改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle("调整亮度/对比度")
        self.setModal(True)
        
        # 创建UI组件
        self._create_ui()
        
        # 初始化参数
        self.brightness = 0
        self.contrast = 1.0
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 亮度控制
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("亮度:")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_spinbox = QDoubleSpinBox()
        self.brightness_spinbox.setRange(-100, 100)
        self.brightness_spinbox.setValue(0)
        self.brightness_spinbox.setSingleStep(1)
        
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_spinbox)
        
        # 对比度控制
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("对比度:")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        self.contrast_spinbox = QDoubleSpinBox()
        self.contrast_spinbox.setRange(0.0, 3.0)
        self.contrast_spinbox.setValue(1.0)
        self.contrast_spinbox.setSingleStep(0.1)
        
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_spinbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.preview_button = QPushButton("预览")
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加所有布局
        main_layout.addLayout(brightness_layout)
        main_layout.addLayout(contrast_layout)
        main_layout.addLayout(button_layout)
        
        # 连接信号和槽
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self.brightness_spinbox.valueChanged.connect(self._on_brightness_changed)
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)
        self.contrast_spinbox.valueChanged.connect(self._on_contrast_changed)
        self.preview_button.clicked.connect(self._on_preview)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_brightness_changed(self, value):
        """亮度改变处理
        
        Args:
            value: 新的亮度值
        """
        if self.sender() == self.brightness_slider:
            self.brightness_spinbox.setValue(value)
        else:
            self.brightness_slider.setValue(int(value))
        self.brightness = value
    
    def _on_contrast_changed(self, value):
        """对比度改变处理
        
        Args:
            value: 新的对比度值
        """
        if self.sender() == self.contrast_slider:
            self.contrast_spinbox.setValue(value / 100.0)
        else:
            self.contrast_slider.setValue(int(value * 100))
        self.contrast = value / 100.0 if isinstance(value, int) else value
    
    def _on_preview(self):
        """预览按钮点击处理"""
        self.parameters_changed.emit(self.brightness, self.contrast)
    
    def get_parameters(self):
        """获取参数
        
        Returns:
            tuple: (亮度, 对比度)
        """
        return self.brightness, self.contrast 