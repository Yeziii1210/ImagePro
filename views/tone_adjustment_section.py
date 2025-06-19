from PySide6.QtCore import Signal
from .adjustment_section_widget import AdjustmentSectionWidget
from .common_widgets import SliderSpinBoxWidget

class ToneAdjustmentSection(AdjustmentSectionWidget):
    """光照与色调调整区域 - 重构版
    
    使用SliderSpinBoxWidget简化实现，减少代码重复
    """
    
    # 信号：操作名, 参数字典
    preview_requested = Signal(str, dict)
    apply_requested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__("光照与色调", parent)
        
        # 跟踪当前拖动状态
        self._current_dragging_operation = None
        self._build_ui()

    def _build_ui(self):
        """构建用户界面"""
        # 亮度调整 (-100 到 100，整数)
        self.brightness_widget = SliderSpinBoxWidget(
            label_text="亮度:",
            min_value=-100,
            max_value=100,
            default_value=0,
            step=1,
            slider_scale=1,
            use_double=False
        )
        self._connect_widget_signals(self.brightness_widget, "brightness_contrast")
        self.add_widget(self.brightness_widget)
        
        # 对比度调整 (0.5 到 2.0，浮点数)
        self.contrast_widget = SliderSpinBoxWidget(
            label_text="对比度:",
            min_value=0.5,
            max_value=2.0,
            default_value=1.0,
            step=0.01,
            slider_scale=100,
            use_double=True
        )
        self._connect_widget_signals(self.contrast_widget, "brightness_contrast")
        self.add_widget(self.contrast_widget)
        
        # 曝光度调整 (-1.0 到 1.0，浮点数)
        self.exposure_widget = SliderSpinBoxWidget(
            label_text="曝光度:",
            min_value=-1.0,
            max_value=1.0,
            default_value=0.0,
            step=0.01,
            slider_scale=100,
            use_double=True
        )
        self._connect_widget_signals(self.exposure_widget, "exposure")
        self.add_widget(self.exposure_widget)
        
        # 高光调整 (-1.0 到 1.0，浮点数)
        self.highlights_widget = SliderSpinBoxWidget(
            label_text="高光:",
            min_value=-1.0,
            max_value=1.0,
            default_value=0.0,
            step=0.01,
            slider_scale=100,
            use_double=True
        )
        self._connect_widget_signals(self.highlights_widget, "highlights")
        self.add_widget(self.highlights_widget)
        
        # 阴影调整 (-1.0 到 1.0，浮点数)
        self.shadows_widget = SliderSpinBoxWidget(
            label_text="阴影:",
            min_value=-1.0,
            max_value=1.0,
            default_value=0.0,
            step=0.01,
            slider_scale=100,
            use_double=True
        )
        self._connect_widget_signals(self.shadows_widget, "shadows")
        self.add_widget(self.shadows_widget)

    def _connect_widget_signals(self, widget: SliderSpinBoxWidget, operation: str):
        """连接widget信号到对应的操作"""
        widget.sliderPressed.connect(lambda: self._on_slider_pressed(operation))
        widget.sliderReleased.connect(lambda: self._on_slider_released(operation))
        widget.sliderMoved.connect(lambda v: self._on_slider_moved(operation))
        widget.editingFinished.connect(lambda: self._on_editing_finished(operation))
        
        # 添加调试输出
        widget.valueChanged.connect(lambda v: print(f"ToneSection: {operation} value changed to {v}"))

    def _on_slider_pressed(self, operation: str):
        """滑块按下处理"""
        self._current_dragging_operation = operation
        print(f"ToneSection: Slider pressed for {operation}")

    def _on_slider_released(self, operation: str):
        """滑块释放处理"""
        if self._current_dragging_operation == operation:
            self._current_dragging_operation = None
            params = self.get_parameters(operation)
            print(f"ToneSection: Emitting apply_requested for {operation} with params: {params}")
            self.apply_requested.emit(operation, params)

    def _on_slider_moved(self, operation: str):
        """滑块移动处理"""
        if self._current_dragging_operation == operation:
            params = self.get_parameters(operation)
            print(f"ToneSection: Emitting preview_requested for {operation} with params: {params}")
            self.preview_requested.emit(operation, params)

    def _on_editing_finished(self, operation: str):
        """编辑完成处理"""
        if self._current_dragging_operation != operation:  # 避免与滑块释放重复
            params = self.get_parameters(operation)
            print(f"ToneSection: Emitting apply_requested for {operation} with params: {params}")
            self.apply_requested.emit(operation, params)

    def get_parameters(self, operation: str) -> dict:
        """获取指定操作的参数"""
        if operation == "brightness_contrast":
            return {
                'brightness': self.brightness_widget.value(),
                'contrast': self.contrast_widget.value()
            }
        elif operation == "exposure":
            return {'exposure': self.exposure_widget.value()}
        elif operation == "highlights":
            return {'highlights': self.highlights_widget.value()}
        elif operation == "shadows":
            return {'shadows': self.shadows_widget.value()}
        return {}

    def set_parameters(self, params: dict):
        """设置参数"""
        if 'brightness' in params:
            self.brightness_widget.setValue(params['brightness'])
        if 'contrast' in params:
            self.contrast_widget.setValue(params['contrast'])
        if 'exposure' in params:
            self.exposure_widget.setValue(params['exposure'])
        if 'highlights' in params:
            self.highlights_widget.setValue(params['highlights'])
        if 'shadows' in params:
            self.shadows_widget.setValue(params['shadows'])

    def reset_to_defaults(self):
        """重置到默认值"""
        self.brightness_widget.setValue(0)
        self.contrast_widget.setValue(1.0)
        self.exposure_widget.setValue(0.0)
        self.highlights_widget.setValue(0.0)
        self.shadows_widget.setValue(0.0)