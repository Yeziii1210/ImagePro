# views/filter_sections.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                             QSpinBox, QDoubleSpinBox, QComboBox, QPushButton)
from PySide6.QtCore import Signal, Qt
from .adjustment_section_widget import AdjustmentSectionWidget
from .common_widgets import SliderSpinBoxWidget

class BlurSection(AdjustmentSectionWidget):
    """模糊处理区域 - 重构版
    
    保留复杂的UI逻辑，但简化一些参数控件
    """
    preview_requested = Signal(str, dict)
    apply_requested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__("模糊处理", parent)
        self._build_ui()
        self.on_blur_type_changed() # Initialize UI state based on default blur type

    def _build_ui(self):
        # 模糊类型选择
        blur_type_layout = QHBoxLayout()
        blur_type_label = QLabel("模糊类型:")
        self.blur_type_combo = QComboBox()
        self.blur_type_combo.addItems(["高斯模糊", "中值滤波", "双边滤波"])
        self.blur_type_combo.currentIndexChanged.connect(self.on_blur_type_changed)
        blur_type_layout.addWidget(blur_type_label)
        blur_type_layout.addWidget(self.blur_type_combo)
        self.add_layout(blur_type_layout)

        # --- 高斯模糊参数 ---
        self.gaussian_params_widget = QWidget()
        gaussian_layout = QVBoxLayout(self.gaussian_params_widget)
        gaussian_layout.setContentsMargins(0,0,0,0)

        # 核大小（保持原来的SpinBox，因为需要奇数验证）
        kernel_layout_gauss = QHBoxLayout()
        kernel_label_gauss = QLabel("核大小:")
        self.kernel_size_spin_gauss = QSpinBox()
        self.kernel_size_spin_gauss.setRange(1, 99)
        self.kernel_size_spin_gauss.setSingleStep(2)
        self.kernel_size_spin_gauss.setValue(3)
        self.kernel_size_spin_gauss.editingFinished.connect(lambda: self._on_spinbox_apply("blur"))
        self.kernel_size_spin_gauss.valueChanged.connect(lambda val: self._ensure_odd(self.kernel_size_spin_gauss, val))
        kernel_layout_gauss.addWidget(kernel_label_gauss)
        kernel_layout_gauss.addWidget(self.kernel_size_spin_gauss)
        gaussian_layout.addLayout(kernel_layout_gauss)

        # Sigma参数（保持简单的SpinBox，因为主要通过按钮触发应用）
        sigma_layout_gauss = QHBoxLayout()
        sigma_label_gauss = QLabel("Sigma:")
        self.sigma_spin_gauss = QDoubleSpinBox()
        self.sigma_spin_gauss.setRange(0.0, 10.0)
        self.sigma_spin_gauss.setValue(0.0)
        self.sigma_spin_gauss.setSingleStep(0.1)
        self.sigma_spin_gauss.editingFinished.connect(lambda: self._on_spinbox_apply("blur"))
        sigma_layout_gauss.addWidget(sigma_label_gauss)
        sigma_layout_gauss.addWidget(self.sigma_spin_gauss)
        gaussian_layout.addLayout(sigma_layout_gauss)
        self.add_widget(self.gaussian_params_widget)

        # --- 中值滤波参数 ---
        self.median_params_widget = QWidget()
        median_layout = QVBoxLayout(self.median_params_widget)
        median_layout.setContentsMargins(0,0,0,0)
        kernel_layout_median = QHBoxLayout()
        kernel_label_median = QLabel("核大小:")
        self.kernel_size_spin_median = QSpinBox()
        self.kernel_size_spin_median.setRange(1, 99)
        self.kernel_size_spin_median.setSingleStep(2)
        self.kernel_size_spin_median.setValue(3)
        self.kernel_size_spin_median.editingFinished.connect(lambda: self._on_spinbox_apply("blur"))
        self.kernel_size_spin_median.valueChanged.connect(lambda val: self._ensure_odd(self.kernel_size_spin_median, val))
        kernel_layout_median.addWidget(kernel_label_median)
        kernel_layout_median.addWidget(self.kernel_size_spin_median)
        median_layout.addLayout(kernel_layout_median)
        self.add_widget(self.median_params_widget)

        # --- 双边滤波参数 ---
        self.bilateral_params_widget = QWidget()
        bilateral_layout = QVBoxLayout(self.bilateral_params_widget)
        bilateral_layout.setContentsMargins(0,0,0,0)

        # 邻域直径（保持简单SpinBox）
        d_layout = QHBoxLayout()
        d_label = QLabel("邻域直径 (d):")
        self.d_spin_bilateral = QSpinBox()
        self.d_spin_bilateral.setRange(1, 20)
        self.d_spin_bilateral.setValue(9)
        self.d_spin_bilateral.editingFinished.connect(lambda: self._on_spinbox_apply("blur"))
        d_layout.addWidget(d_label)
        d_layout.addWidget(self.d_spin_bilateral)
        bilateral_layout.addLayout(d_layout)

        # Sigma Color（保持简单SpinBox）
        sigma_color_layout = QHBoxLayout()
        sigma_color_label = QLabel("Sigma Color:")
        self.sigma_color_spin_bilateral = QDoubleSpinBox()
        self.sigma_color_spin_bilateral.setRange(1.0, 200.0)
        self.sigma_color_spin_bilateral.setValue(75.0)
        self.sigma_color_spin_bilateral.setSingleStep(1.0)
        self.sigma_color_spin_bilateral.editingFinished.connect(lambda: self._on_spinbox_apply("blur"))
        sigma_color_layout.addWidget(sigma_color_label)
        sigma_color_layout.addWidget(self.sigma_color_spin_bilateral)
        bilateral_layout.addLayout(sigma_color_layout)
        
        # Sigma Space（保持简单SpinBox）
        sigma_space_layout = QHBoxLayout()
        sigma_space_label = QLabel("Sigma Space:")
        self.sigma_space_spin_bilateral = QDoubleSpinBox()
        self.sigma_space_spin_bilateral.setRange(1.0, 200.0)
        self.sigma_space_spin_bilateral.setValue(75.0)
        self.sigma_space_spin_bilateral.setSingleStep(1.0)
        self.sigma_space_spin_bilateral.editingFinished.connect(lambda: self._on_spinbox_apply("blur"))
        sigma_space_layout.addWidget(sigma_space_label)
        sigma_space_layout.addWidget(self.sigma_space_spin_bilateral)
        bilateral_layout.addLayout(sigma_space_layout)
        self.add_widget(self.bilateral_params_widget)

        # --- 应用/预览按钮 ---
        buttons_layout = QHBoxLayout()
        preview_button = QPushButton("预览模糊")
        apply_button = QPushButton("应用模糊")
        preview_button.clicked.connect(lambda: self.preview_requested.emit("blur", self.get_parameters()))
        apply_button.clicked.connect(lambda: self.apply_requested.emit("blur", self.get_parameters()))
        buttons_layout.addWidget(preview_button)
        buttons_layout.addWidget(apply_button)
        self.add_layout(buttons_layout)
        
    def _ensure_odd(self, spinbox, value):
        """确保核大小为奇数"""
        if value % 2 == 0:
            spinbox.setValue(value + 1 if value < spinbox.maximum() else value - 1)

    def on_blur_type_changed(self):
        """模糊类型改变时的处理"""
        blur_type = self.blur_type_combo.currentText()
        self.gaussian_params_widget.setVisible(blur_type == "高斯模糊")
        self.median_params_widget.setVisible(blur_type == "中值滤波")
        self.bilateral_params_widget.setVisible(blur_type == "双边滤波")
        print(f"BlurSection: Blur type changed to {blur_type}")

    def _on_spinbox_apply(self, operation_name):
        """SpinBox编辑完成处理（模糊主要通过按钮应用）"""
        print(f"BlurSection: SpinBox edited for {operation_name}")

    def get_parameters(self) -> dict:
        """获取当前参数"""
        blur_type_text = self.blur_type_combo.currentText()
        params = {'blur_type': 'gaussian'}  # Default
        if blur_type_text == "高斯模糊":
            params['blur_type'] = 'gaussian'
            params['kernel_size'] = self.kernel_size_spin_gauss.value()
            params['sigma'] = self.sigma_spin_gauss.value()
        elif blur_type_text == "中值滤波":
            params['blur_type'] = 'median'
            params['kernel_size'] = self.kernel_size_spin_median.value()
        elif blur_type_text == "双边滤波":
            params['blur_type'] = 'bilateral'
            params['d'] = self.d_spin_bilateral.value()
            params['sigma_color'] = self.sigma_color_spin_bilateral.value()
            params['sigma_space'] = self.sigma_space_spin_bilateral.value()
        return params

    def set_parameters(self, params: dict):
        """设置参数"""
        # TODO: 根据需要实现预设加载功能
        pass


class SharpenSection(AdjustmentSectionWidget):
    """锐化处理区域 - 重构版
    
    使用SliderSpinBoxWidget优化主要调整参数
    """
    preview_requested = Signal(str, dict)
    apply_requested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__("锐化处理", parent)
        self._current_method = "laplacian"  # Default
        self._is_dragging = False
        self._current_operation = ""
        self._build_ui()
        self.on_sharpen_method_changed()  # Initialize

    def _build_ui(self):
        # 锐化方法选择
        method_layout = QHBoxLayout()
        method_label = QLabel("锐化方法:")
        self.method_combo = QComboBox()
        self.method_combo.addItem("拉普拉斯锐化", "laplacian")
        self.method_combo.addItem("USM锐化", "usm")
        self.method_combo.currentIndexChanged.connect(self.on_sharpen_method_changed)
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        self.add_layout(method_layout)

        # --- 拉普拉斯参数 ---
        self.laplacian_params_widget = QWidget()
        lap_layout = QVBoxLayout(self.laplacian_params_widget)
        lap_layout.setContentsMargins(0, 0, 0, 0)

        # 核大小（保持简单SpinBox，需要奇数验证）
        lap_kernel_layout = QHBoxLayout()
        lap_kernel_label = QLabel("核大小:")
        self.lap_kernel_spin = QSpinBox()
        self.lap_kernel_spin.setRange(1, 99)
        self.lap_kernel_spin.setSingleStep(2)
        self.lap_kernel_spin.setValue(3)
        self.lap_kernel_spin.valueChanged.connect(lambda val: self._ensure_odd(self.lap_kernel_spin, val))
        self.lap_kernel_spin.editingFinished.connect(lambda: self._on_editing_finished("sharpen"))
        lap_kernel_layout.addWidget(lap_kernel_label)
        lap_kernel_layout.addWidget(self.lap_kernel_spin)
        lap_layout.addLayout(lap_kernel_layout)

        # 强度参数（使用新的SliderSpinBoxWidget）
        self.laplacian_strength_widget = SliderSpinBoxWidget(
            label_text="强度:",
            min_value=0.0,
            max_value=5.0,
            default_value=1.0,
            step=0.1,
            slider_scale=100,
            use_double=True
        )
        self._connect_widget_signals(self.laplacian_strength_widget, "sharpen")
        lap_layout.addWidget(self.laplacian_strength_widget)
        self.add_widget(self.laplacian_params_widget)

        # --- USM锐化参数 ---
        self.usm_params_widget = QWidget()
        usm_layout = QVBoxLayout(self.usm_params_widget)
        usm_layout.setContentsMargins(0, 0, 0, 0)

        # 锐化量（使用新的SliderSpinBoxWidget）
        self.usm_amount_widget = SliderSpinBoxWidget(
            label_text="锐化量:",
            min_value=0.0,
            max_value=5.0,
            default_value=1.0,
            step=0.1,
            slider_scale=100,
            use_double=True
        )
        self._connect_widget_signals(self.usm_amount_widget, "sharpen")
        usm_layout.addWidget(self.usm_amount_widget)

        # 半径（保持简单SpinBox）
        radius_layout = QHBoxLayout()
        radius_label = QLabel("半径:")
        self.usm_radius_spin = QDoubleSpinBox()
        self.usm_radius_spin.setRange(0.1, 10.0)
        self.usm_radius_spin.setValue(1.0)
        self.usm_radius_spin.setSingleStep(0.1)
        self.usm_radius_spin.editingFinished.connect(lambda: self._on_editing_finished("sharpen"))
        radius_layout.addWidget(radius_label)
        radius_layout.addWidget(self.usm_radius_spin)
        usm_layout.addLayout(radius_layout)

        # 阈值（保持简单SpinBox）
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("阈值:")
        self.usm_threshold_spin = QSpinBox()
        self.usm_threshold_spin.setRange(0, 255)
        self.usm_threshold_spin.setValue(0)
        self.usm_threshold_spin.editingFinished.connect(lambda: self._on_editing_finished("sharpen"))
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.usm_threshold_spin)
        usm_layout.addLayout(threshold_layout)
        self.add_widget(self.usm_params_widget)

        # --- 应用/预览按钮 ---
        buttons_layout = QHBoxLayout()
        preview_button = QPushButton("预览锐化")
        apply_button = QPushButton("应用锐化")
        preview_button.clicked.connect(lambda: self.preview_requested.emit("sharpen", self.get_parameters()))
        apply_button.clicked.connect(lambda: self.apply_requested.emit("sharpen", self.get_parameters()))
        buttons_layout.addWidget(preview_button)
        buttons_layout.addWidget(apply_button)
        self.add_layout(buttons_layout)

    def _connect_widget_signals(self, widget: SliderSpinBoxWidget, operation: str):
        """连接widget信号到对应的操作"""
        widget.sliderPressed.connect(lambda: self._on_slider_pressed(operation))
        widget.sliderReleased.connect(lambda: self._on_slider_released(operation))
        widget.sliderMoved.connect(lambda v: self._on_slider_moved(operation))
        widget.editingFinished.connect(lambda: self._on_editing_finished(operation))
        
        # 添加调试输出
        widget.valueChanged.connect(lambda v: print(f"SharpenSection: {operation} value changed to {v}"))

    def _on_slider_pressed(self, operation: str):
        """滑块按下处理"""
        self._is_dragging = True
        self._current_operation = operation
        print(f"SharpenSection: Slider pressed for {operation}")

    def _on_slider_released(self, operation: str):
        """滑块释放处理"""
        if self._is_dragging and self._current_operation == operation:
            self._is_dragging = False
            params = self.get_parameters()
            print(f"SharpenSection: Emitting apply_requested for {operation} with params: {params}")
            self.apply_requested.emit(operation, params)

    def _on_slider_moved(self, operation: str):
        """滑块移动处理"""
        if self._is_dragging and self._current_operation == operation:
            params = self.get_parameters()
            print(f"SharpenSection: Emitting preview_requested for {operation} with params: {params}")
            self.preview_requested.emit(operation, params)

    def _on_editing_finished(self, operation: str):
        """编辑完成处理"""
        if not self._is_dragging:  # 避免与滑块释放重复
            params = self.get_parameters()
            print(f"SharpenSection: Emitting apply_requested for {operation} with params: {params}")
            self.apply_requested.emit(operation, params)

    def _ensure_odd(self, spinbox, value):
        """确保核大小为奇数"""
        if value % 2 == 0:
            spinbox.setValue(value + 1 if value < spinbox.maximum() else value - 1)

    def on_sharpen_method_changed(self):
        """锐化方法改变时的处理"""
        self._current_method = self.method_combo.currentData()
        self.laplacian_params_widget.setVisible(self._current_method == "laplacian")
        self.usm_params_widget.setVisible(self._current_method == "usm")
        print(f"SharpenSection: Method changed to {self._current_method}")

    def get_parameters(self) -> dict:
        """获取当前参数"""
        params = {'method': self._current_method}
        
        if self._current_method == "laplacian":
            params.update({
                'kernel_size': self.lap_kernel_spin.value(),
                'strength': self.laplacian_strength_widget.value()
            })
        elif self._current_method == "usm":
            params.update({
                'amount': self.usm_amount_widget.value(),
                'radius': self.usm_radius_spin.value(),
                'threshold': self.usm_threshold_spin.value()
            })
        
        return params

    def set_parameters(self, params: dict):
        """设置参数"""
        # TODO: 根据需要实现预设加载功能
        pass