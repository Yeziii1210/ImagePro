"""
边缘检测对话框模块
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QPushButton)
from PySide6.QtCore import Qt, Signal

class EdgeDetectionDialog(QDialog):
    """边缘检测对话框类"""
    
    # 信号定义
    parameters_changed = Signal(int, int)  # 参数改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle("边缘检测")
        self.setModal(True)
        
        # 创建UI组件
        self._create_ui()
        
        # 初始化参数
        self.threshold1 = 100
        self.threshold2 = 200
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 阈值1控制
        threshold1_layout = QHBoxLayout()
        threshold1_label = QLabel("阈值1:")
        self.threshold1_spinbox = QSpinBox()
        self.threshold1_spinbox.setRange(0, 255)
        self.threshold1_spinbox.setValue(100)
        self.threshold1_spinbox.setSingleStep(1)
        
        threshold1_layout.addWidget(threshold1_label)
        threshold1_layout.addWidget(self.threshold1_spinbox)
        
        # 阈值2控制
        threshold2_layout = QHBoxLayout()
        threshold2_label = QLabel("阈值2:")
        self.threshold2_spinbox = QSpinBox()
        self.threshold2_spinbox.setRange(0, 255)
        self.threshold2_spinbox.setValue(200)
        self.threshold2_spinbox.setSingleStep(1)
        
        threshold2_layout.addWidget(threshold2_label)
        threshold2_layout.addWidget(self.threshold2_spinbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.preview_button = QPushButton("预览")
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加所有布局
        main_layout.addLayout(threshold1_layout)
        main_layout.addLayout(threshold2_layout)
        main_layout.addLayout(button_layout)
        
        # 连接信号和槽
        self.threshold1_spinbox.valueChanged.connect(self._on_threshold1_changed)
        self.threshold2_spinbox.valueChanged.connect(self._on_threshold2_changed)
        self.preview_button.clicked.connect(self._on_preview)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_threshold1_changed(self, value):
        """阈值1改变处理
        
        Args:
            value: 新的阈值1值
        """
        # 确保阈值1小于阈值2
        if value >= self.threshold2:
            value = self.threshold2 - 1
            self.threshold1_spinbox.setValue(value)
        self.threshold1 = value
    
    def _on_threshold2_changed(self, value):
        """阈值2改变处理
        
        Args:
            value: 新的阈值2值
        """
        # 确保阈值2大于阈值1
        if value <= self.threshold1:
            value = self.threshold1 + 1
            self.threshold2_spinbox.setValue(value)
        self.threshold2 = value
    
    def _on_preview(self):
        """预览按钮点击处理"""
        self.parameters_changed.emit(self.threshold1, self.threshold2)
    
    def get_parameters(self):
        """获取参数
        
        Returns:
            tuple: (阈值1, 阈值2)
        """
        return self.threshold1, self.threshold2 