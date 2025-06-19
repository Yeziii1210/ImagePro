"""
高斯模糊对话框模块
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QDoubleSpinBox, QPushButton)
from PySide6.QtCore import Qt, Signal

class GaussianBlurDialog(QDialog):
    """高斯模糊对话框类"""
    
    # 信号定义
    parameters_changed = Signal(int, float)  # 参数改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle("高斯模糊")
        self.setModal(True)
        
        # 创建UI组件
        self._create_ui()
        
        # 初始化参数
        self.kernel_size = 3
        self.sigma = 0.0
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 核大小控制
        kernel_layout = QHBoxLayout()
        kernel_label = QLabel("核大小:")
        self.kernel_spinbox = QSpinBox()
        self.kernel_spinbox.setRange(1, 99)
        self.kernel_spinbox.setValue(3)
        self.kernel_spinbox.setSingleStep(2)
        self.kernel_spinbox.setPrefix("(奇数) ")
        
        kernel_layout.addWidget(kernel_label)
        kernel_layout.addWidget(self.kernel_spinbox)
        
        # Sigma控制
        sigma_layout = QHBoxLayout()
        sigma_label = QLabel("Sigma:")
        self.sigma_spinbox = QDoubleSpinBox()
        self.sigma_spinbox.setRange(0.0, 10.0)
        self.sigma_spinbox.setValue(0.0)
        self.sigma_spinbox.setSingleStep(0.1)
        
        sigma_layout.addWidget(sigma_label)
        sigma_layout.addWidget(self.sigma_spinbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.preview_button = QPushButton("预览")
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加所有布局
        main_layout.addLayout(kernel_layout)
        main_layout.addLayout(sigma_layout)
        main_layout.addLayout(button_layout)
        
        # 连接信号和槽
        self.kernel_spinbox.valueChanged.connect(self._on_kernel_changed)
        self.sigma_spinbox.valueChanged.connect(self._on_sigma_changed)
        self.preview_button.clicked.connect(self._on_preview)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_kernel_changed(self, value):
        """核大小改变处理
        
        Args:
            value: 新的核大小值
        """
        # 确保核大小为奇数
        if value % 2 == 0:
            value += 1
            self.kernel_spinbox.setValue(value)
        self.kernel_size = value
    
    def _on_sigma_changed(self, value):
        """Sigma改变处理
        
        Args:
            value: 新的Sigma值
        """
        self.sigma = value
    
    def _on_preview(self):
        """预览按钮点击处理"""
        self.parameters_changed.emit(self.kernel_size, self.sigma)
    
    def get_parameters(self):
        """获取参数
        
        Returns:
            tuple: (核大小, sigma)
        """
        return self.kernel_size, self.sigma 