"""
通用UI组件
包含可复用的UI控件，减少代码重复
"""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QSlider, 
                              QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, Signal

class SliderSpinBoxWidget(QWidget):
    """滑块-数值框组合控件
    
    统一处理滑块和数值框的同步，减少重复代码
    """
    
    # 信号
    valueChanged = Signal(float)  # 值改变信号
    sliderPressed = Signal()      # 滑块按下信号  
    sliderReleased = Signal()     # 滑块释放信号
    sliderMoved = Signal(float)   # 滑块移动信号
    editingFinished = Signal()    # 编辑完成信号
    
    def __init__(self, label_text: str, min_value: float, max_value: float, 
                 default_value: float = 0.0, step: float = 0.1, 
                 slider_scale: int = 100, use_double: bool = True, parent=None):
        """初始化滑块-数值框组合控件
        
        Args:
            label_text: 标签文本
            min_value: 最小值
            max_value: 最大值
            default_value: 默认值
            step: 步长
            slider_scale: 滑块缩放倍数（用于浮点数转整数）
            use_double: 是否使用双精度数值框
            parent: 父控件
        """
        super().__init__(parent)
        
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._slider_scale = slider_scale
        self._use_double = use_double
        self._ignore_value_change = False
        
        self._setup_ui(label_text, default_value)
        self._connect_signals()
    
    def _setup_ui(self, label_text: str, default_value: float):
        """设置用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 标签
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(60)  # 确保标签有足够宽度
        self.label.setToolTip(f"{label_text}调整范围: {self._min_value} - {self._max_value}")
        layout.addWidget(self.label)
        
        # 滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(
            int(self._min_value * self._slider_scale),
            int(self._max_value * self._slider_scale)
        )
        self.slider.setValue(int(default_value * self._slider_scale))
        self.slider.setMinimumWidth(120)  # 确保滑块有足够宽度
        self.slider.setToolTip(f"拖动调整{label_text}，范围: {self._min_value} - {self._max_value}。拖动时实时预览，释放时应用")
        layout.addWidget(self.slider)
        
        # 数值框
        if self._use_double:
            self.spinbox = QDoubleSpinBox()
            self.spinbox.setDecimals(len(str(self._step).split('.')[-1]) if '.' in str(self._step) else 0)
        else:
            self.spinbox = QSpinBox()
        
        self.spinbox.setRange(self._min_value, self._max_value)
        self.spinbox.setSingleStep(self._step)
        self.spinbox.setValue(default_value)
        self.spinbox.setMinimumWidth(70)  # 确保数值框有足够宽度
        self.spinbox.setToolTip(f"精确输入{label_text}数值，步长: {self._step}")
        layout.addWidget(self.spinbox)
        
        # 设置现代化样式
        self._apply_modern_style()
    
    def _apply_modern_style(self):
        """应用现代化样式"""
        # 滑块样式
        slider_style = """
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 6px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 16px;
                margin: -2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d4d4d4, stop:1 #afafaf);
            }
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8f8f8f, stop:1 #6f6f6f);
            }
        """
        self.slider.setStyleSheet(slider_style)
        
        # 数值框样式
        spinbox_style = """
            QSpinBox, QDoubleSpinBox {
                padding: 2px 4px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #0078d4;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 16px;
                border-left: 1px solid #cccccc;
                border-bottom: 1px solid #cccccc;
                border-top-right-radius: 4px;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 16px;
                border-left: 1px solid #cccccc;
                border-top: 1px solid #cccccc;
                border-bottom-right-radius: 4px;
            }
        """
        self.spinbox.setStyleSheet(spinbox_style)
    
    def _connect_signals(self):
        """连接信号"""
        # 滑块信号
        self.slider.valueChanged.connect(self._on_slider_value_changed)
        self.slider.sliderPressed.connect(self.sliderPressed.emit)
        self.slider.sliderReleased.connect(self.sliderReleased.emit)
        self.slider.sliderMoved.connect(self._on_slider_moved)
        
        # 数值框信号
        self.spinbox.valueChanged.connect(self._on_spinbox_value_changed)
        self.spinbox.editingFinished.connect(self.editingFinished.emit)
    
    def _on_slider_value_changed(self, value: int):
        """滑块值改变处理"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            real_value = value / self._slider_scale
            self.spinbox.setValue(real_value)
            self._ignore_value_change = False
            self.valueChanged.emit(real_value)
    
    def _on_slider_moved(self, value: int):
        """滑块移动处理"""
        real_value = value / self._slider_scale
        self.sliderMoved.emit(real_value)
    
    def _on_spinbox_value_changed(self, value: float):
        """数值框值改变处理"""
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.slider.setValue(int(value * self._slider_scale))
            self._ignore_value_change = False
            self.valueChanged.emit(value)
    
    def value(self) -> float:
        """获取当前值"""
        return self.spinbox.value()
    
    def setValue(self, value: float):
        """设置值"""
        self._ignore_value_change = True
        self.spinbox.setValue(value)
        self.slider.setValue(int(value * self._slider_scale))
        self._ignore_value_change = False
    
    def setRange(self, min_value: float, max_value: float):
        """设置范围"""
        self._min_value = min_value
        self._max_value = max_value
        
        self.slider.setRange(
            int(min_value * self._slider_scale),
            int(max_value * self._slider_scale)
        )
        self.spinbox.setRange(min_value, max_value)
    
    def setEnabled(self, enabled: bool):
        """设置启用状态"""
        super().setEnabled(enabled)
        self.slider.setEnabled(enabled)
        self.spinbox.setEnabled(enabled)
        self.label.setEnabled(enabled)


class ParameterManager:
    """参数管理器
    
    统一管理各种调整参数，提供序列化和反序列化功能
    """
    
    def __init__(self):
        self._parameters = {}
    
    def set_parameter(self, section_name: str, param_name: str, value):
        """设置参数"""
        if section_name not in self._parameters:
            self._parameters[section_name] = {}
        self._parameters[section_name][param_name] = value
    
    def get_parameter(self, section_name: str, param_name: str, default_value=None):
        """获取参数"""
        return self._parameters.get(section_name, {}).get(param_name, default_value)
    
    def get_section_parameters(self, section_name: str) -> dict:
        """获取整个section的参数"""
        return self._parameters.get(section_name, {}).copy()
    
    def set_section_parameters(self, section_name: str, parameters: dict):
        """设置整个section的参数"""
        self._parameters[section_name] = parameters.copy()
    
    def clear_section(self, section_name: str):
        """清除section的所有参数"""
        if section_name in self._parameters:
            del self._parameters[section_name]
    
    def to_dict(self) -> dict:
        """导出所有参数为字典"""
        return self._parameters.copy()
    
    def from_dict(self, data: dict):
        """从字典导入参数"""
        self._parameters = data.copy()
    
    def reset(self):
        """重置所有参数"""
        self._parameters.clear()


class PresetManager:
    """预设管理器
    
    管理用户预设，支持保存和加载预设配置
    """
    
    def __init__(self):
        self._presets = {}
    
    def save_preset(self, name: str, parameters: dict):
        """保存预设"""
        self._presets[name] = parameters.copy()
    
    def load_preset(self, name: str) -> dict:
        """加载预设"""
        return self._presets.get(name, {}).copy()
    
    def delete_preset(self, name: str):
        """删除预设"""
        if name in self._presets:
            del self._presets[name]
    
    def get_preset_names(self) -> list:
        """获取所有预设名称"""
        return list(self._presets.keys())
    
    def has_preset(self, name: str) -> bool:
        """检查预设是否存在"""
        return name in self._presets 