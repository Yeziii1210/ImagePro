# views/auto_process_sections.py
"""
自动图像处理功能模块
包含一键优化、自动对比度增强、自动色彩校正和自动白平衡功能
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QSlider, QPushButton, QSpinBox, QDoubleSpinBox, 
                              QComboBox, QCheckBox)
from PySide6.QtCore import Qt, Signal

from .adjustment_section_widget import AdjustmentSectionWidget

class OneClickOptimizeSection(AdjustmentSectionWidget):
    """一键优化区域"""
    
    # 信号
    apply_requested = Signal(str, dict)
    preview_requested = Signal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__("一键智能优化", parent)
        self._build_ui()
    
    def _build_ui(self):
        """构建用户界面"""
        # 优化选项
        self.contrast_checkbox = QCheckBox("自动对比度增强")
        self.contrast_checkbox.setChecked(True)
        self.add_widget(self.contrast_checkbox)
        
        self.color_checkbox = QCheckBox("自动色彩校正")
        self.color_checkbox.setChecked(True)
        self.add_widget(self.color_checkbox)
        
        self.wb_checkbox = QCheckBox("自动白平衡")
        self.wb_checkbox.setChecked(True)
        self.add_widget(self.wb_checkbox)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("预览优化")
        self.preview_button.clicked.connect(self._on_preview_clicked)
        
        self.apply_button = QPushButton("应用优化")
        self.apply_button.clicked.connect(self._on_apply_clicked)
        
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addWidget(self.apply_button)
        self.add_layout(buttons_layout)
    
    def _on_preview_clicked(self):
        """预览一键优化"""
        params = self.get_parameters()
        print(f"OneClickOptimizeSection: Emitting preview_requested for one_click_optimize with params: {params}")
        self.preview_requested.emit("one_click_optimize", params)
    
    def _on_apply_clicked(self):
        """应用一键优化"""
        params = self.get_parameters()
        print(f"OneClickOptimizeSection: Emitting apply_requested for one_click_optimize with params: {params}")
        self.apply_requested.emit("one_click_optimize", params)
    
    def get_parameters(self) -> dict:
        """获取当前参数"""
        return {
            'enable_contrast': self.contrast_checkbox.isChecked(),
            'enable_color': self.color_checkbox.isChecked(),
            'enable_wb': self.wb_checkbox.isChecked()
        }
    
    def set_parameters(self, params: dict):
        """设置参数"""
        if 'enable_contrast' in params:
            self.contrast_checkbox.setChecked(params['enable_contrast'])
        if 'enable_color' in params:
            self.color_checkbox.setChecked(params['enable_color'])
        if 'enable_wb' in params:
            self.wb_checkbox.setChecked(params['enable_wb'])


class AutoContrastSection(AdjustmentSectionWidget):
    """自动对比度增强区域"""
    
    # 信号
    apply_requested = Signal(str, dict)
    preview_requested = Signal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__("自动对比度增强", parent)
        self._ignore_value_change = False
        self._build_ui()
    
    def _build_ui(self):
        """构建用户界面"""
        # 对比度限制滑块
        clip_limit_layout = QHBoxLayout()
        clip_limit_label = QLabel("对比度限制:")
        
        self.clip_limit_slider = QSlider(Qt.Horizontal)
        self.clip_limit_slider.setRange(10, 50)  # 1.0到5.0映射为10到50
        self.clip_limit_slider.setValue(20)      # 默认2.0
        
        self.clip_limit_spin = QDoubleSpinBox()
        self.clip_limit_spin.setRange(1.0, 5.0)
        self.clip_limit_spin.setValue(2.0)
        self.clip_limit_spin.setSingleStep(0.1)
        self.clip_limit_spin.setDecimals(1)
        
        # 连接信号
        self.clip_limit_slider.valueChanged.connect(self._sync_clip_limit_spinbox)
        self.clip_limit_spin.valueChanged.connect(self._sync_clip_limit_slider)
        self.clip_limit_spin.editingFinished.connect(self._on_apply_clicked)
        
        clip_limit_layout.addWidget(clip_limit_label)
        clip_limit_layout.addWidget(self.clip_limit_slider)
        clip_limit_layout.addWidget(self.clip_limit_spin)
        self.add_layout(clip_limit_layout)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("预览")
        self.preview_button.clicked.connect(self._on_preview_clicked)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._on_apply_clicked)
        
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addWidget(self.apply_button)
        self.add_layout(buttons_layout)
    
    def _sync_clip_limit_slider(self, value):
        """同步滑块值"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.clip_limit_slider.setValue(int(value * 10))
            self._ignore_value_change = False
    
    def _sync_clip_limit_spinbox(self, value):
        """同步数值框值"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.clip_limit_spin.setValue(value / 10.0)
            self._ignore_value_change = False
    
    def _on_preview_clicked(self):
        """预览对比度增强"""
        params = self.get_parameters()
        print(f"AutoContrastSection: Emitting preview_requested for auto_contrast with params: {params}")
        self.preview_requested.emit("auto_contrast", params)
    
    def _on_apply_clicked(self):
        """应用对比度增强"""
        params = self.get_parameters()
        print(f"AutoContrastSection: Emitting apply_requested for auto_contrast with params: {params}")
        self.apply_requested.emit("auto_contrast", params)
    
    def get_parameters(self) -> dict:
        """获取当前参数"""
        return {
            'clip_limit': self.clip_limit_spin.value()
        }
    
    def set_parameters(self, params: dict):
        """设置参数"""
        if 'clip_limit' in params:
            self.clip_limit_spin.setValue(params['clip_limit'])


class AutoColorSection(AdjustmentSectionWidget):
    """自动色彩校正区域"""
    
    # 信号
    apply_requested = Signal(str, dict)
    preview_requested = Signal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__("自动色彩校正", parent)
        self._ignore_value_change = False
        self._build_ui()
    
    def _build_ui(self):
        """构建用户界面"""
        # 饱和度滑块
        saturation_layout = QHBoxLayout()
        saturation_label = QLabel("饱和度:")
        
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(10, 20)  # 1.0到2.0映射为10到20
        self.saturation_slider.setValue(13)      # 默认1.3
        
        self.saturation_spin = QDoubleSpinBox()
        self.saturation_spin.setRange(1.0, 2.0)
        self.saturation_spin.setValue(1.3)
        self.saturation_spin.setSingleStep(0.1)
        self.saturation_spin.setDecimals(1)
        
        # 连接饱和度控件
        self.saturation_slider.valueChanged.connect(self._sync_saturation_spinbox)
        self.saturation_spin.valueChanged.connect(self._sync_saturation_slider)
        self.saturation_spin.editingFinished.connect(self._on_apply_clicked)
        
        saturation_layout.addWidget(saturation_label)
        saturation_layout.addWidget(self.saturation_slider)
        saturation_layout.addWidget(self.saturation_spin)
        self.add_layout(saturation_layout)
        
        # 鲜艳度滑块
        vibrance_layout = QHBoxLayout()
        vibrance_label = QLabel("鲜艳度:")
        
        self.vibrance_slider = QSlider(Qt.Horizontal)
        self.vibrance_slider.setRange(10, 20)  # 1.0到2.0映射为10到20
        self.vibrance_slider.setValue(12)      # 默认1.2
        
        self.vibrance_spin = QDoubleSpinBox()
        self.vibrance_spin.setRange(1.0, 2.0)
        self.vibrance_spin.setValue(1.2)
        self.vibrance_spin.setSingleStep(0.1)
        self.vibrance_spin.setDecimals(1)
        
        # 连接鲜艳度控件
        self.vibrance_slider.valueChanged.connect(self._sync_vibrance_spinbox)
        self.vibrance_spin.valueChanged.connect(self._sync_vibrance_slider)
        self.vibrance_spin.editingFinished.connect(self._on_apply_clicked)
        
        vibrance_layout.addWidget(vibrance_label)
        vibrance_layout.addWidget(self.vibrance_slider)
        vibrance_layout.addWidget(self.vibrance_spin)
        self.add_layout(vibrance_layout)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("预览")
        self.preview_button.clicked.connect(self._on_preview_clicked)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._on_apply_clicked)
        
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addWidget(self.apply_button)
        self.add_layout(buttons_layout)
    
    def _sync_saturation_slider(self, value):
        """同步饱和度滑块值"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.saturation_slider.setValue(int(value * 10))
            self._ignore_value_change = False
    
    def _sync_saturation_spinbox(self, value):
        """同步饱和度数值框值"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.saturation_spin.setValue(value / 10.0)
            self._ignore_value_change = False
    
    def _sync_vibrance_slider(self, value):
        """同步鲜艳度滑块值"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.vibrance_slider.setValue(int(value * 10))
            self._ignore_value_change = False
    
    def _sync_vibrance_spinbox(self, value):
        """同步鲜艳度数值框值"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.vibrance_spin.setValue(value / 10.0)
            self._ignore_value_change = False
    
    def _on_preview_clicked(self):
        """预览色彩校正"""
        params = self.get_parameters()
        print(f"AutoColorSection: Emitting preview_requested for auto_color with params: {params}")
        self.preview_requested.emit("auto_color", params)
    
    def _on_apply_clicked(self):
        """应用色彩校正"""
        params = self.get_parameters()
        print(f"AutoColorSection: Emitting apply_requested for auto_color with params: {params}")
        self.apply_requested.emit("auto_color", params)
    
    def get_parameters(self) -> dict:
        """获取当前参数"""
        return {
            'saturation': self.saturation_spin.value(),
            'vibrance': self.vibrance_spin.value()
        }
    
    def set_parameters(self, params: dict):
        """设置参数"""
        if 'saturation' in params:
            self.saturation_spin.setValue(params['saturation'])
        if 'vibrance' in params:
            self.vibrance_spin.setValue(params['vibrance'])


class AutoWhiteBalanceSection(AdjustmentSectionWidget):
    """自动白平衡区域"""
    
    # 信号
    apply_requested = Signal(str, dict)
    preview_requested = Signal(str, dict)
    
    def __init__(self, parent=None):
        super().__init__("自动白平衡", parent)
        self._build_ui()
    
    def _build_ui(self):
        """构建用户界面"""
        # 白平衡方法选择
        method_layout = QHBoxLayout()
        method_label = QLabel("白平衡方法:")
        
        self.method_combo = QComboBox()
        self.method_combo.addItem("灰色世界假设", "gray_world")
        self.method_combo.addItem("完美反射假设", "perfect_reflector")
        self.method_combo.addItem("自适应白平衡", "adaptive")
        self.method_combo.setCurrentIndex(2)  # 默认选择自适应白平衡
        
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        self.add_layout(method_layout)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        self.preview_button = QPushButton("预览")
        self.preview_button.clicked.connect(self._on_preview_clicked)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._on_apply_clicked)
        
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addWidget(self.apply_button)
        self.add_layout(buttons_layout)
    
    def _on_preview_clicked(self):
        """预览白平衡"""
        params = self.get_parameters()
        print(f"AutoWhiteBalanceSection: Emitting preview_requested for auto_white_balance with params: {params}")
        self.preview_requested.emit("auto_white_balance", params)
    
    def _on_apply_clicked(self):
        """应用白平衡"""
        params = self.get_parameters()
        print(f"AutoWhiteBalanceSection: Emitting apply_requested for auto_white_balance with params: {params}")
        self.apply_requested.emit("auto_white_balance", params)
    
    def get_parameters(self) -> dict:
        """获取当前参数"""
        return {
            'method': self.method_combo.currentData()
        }
    
    def set_parameters(self, params: dict):
        """设置参数"""
        if 'method' in params:
            # 找到对应的索引
            for i in range(self.method_combo.count()):
                if self.method_combo.itemData(i) == params['method']:
                    self.method_combo.setCurrentIndex(i)
                    break
