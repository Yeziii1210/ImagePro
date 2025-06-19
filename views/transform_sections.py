# views/transform_sections.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                             QSpinBox, QPushButton, QCheckBox, QGridLayout)
from PySide6.QtCore import Signal, Qt
from .adjustment_section_widget import AdjustmentSectionWidget
from .common_widgets import SliderSpinBoxWidget

class GeometrySection(AdjustmentSectionWidget):
    """几何变换区域 - 重构版
    
    使用SliderSpinBoxWidget优化旋转角度控制
    """
    # 信号：操作名, 参数字典
    apply_requested = Signal(str, dict)
    preview_requested = Signal(str, dict) 

    def __init__(self, parent=None):
        super().__init__("几何变换", parent)
        self._is_dragging_rotate = False
        self._build_ui()

    def _build_ui(self):
        # --- 旋转 ---
        rotate_group_layout = QVBoxLayout()

        # 角度控制（使用新的SliderSpinBoxWidget）
        self.rotate_angle_widget = SliderSpinBoxWidget(
            label_text="角度:",
            min_value=-180,
            max_value=180,
            default_value=0,
            step=1,
            slider_scale=1,
            use_double=False
        )
        self._connect_rotate_signals()
        rotate_group_layout.addWidget(self.rotate_angle_widget)

        # 自动扩展选项
        self.rotate_expand_checkbox = QCheckBox("自动扩展以适应图像")
        self.rotate_expand_checkbox.stateChanged.connect(self._on_rotate_preview)
        rotate_group_layout.addWidget(self.rotate_expand_checkbox)

        # 应用按钮
        rotate_apply_button = QPushButton("应用旋转")
        rotate_apply_button.clicked.connect(self._on_rotate_apply_button_clicked)
        rotate_group_layout.addWidget(rotate_apply_button)
        self.add_layout(rotate_group_layout)

        # --- 翻转 ---
        flip_group_layout = QVBoxLayout()
        flip_buttons_layout = QHBoxLayout()
        h_flip_button = QPushButton("水平翻转")
        v_flip_button = QPushButton("垂直翻转")
        h_flip_button.clicked.connect(self._on_h_flip_clicked)
        v_flip_button.clicked.connect(self._on_v_flip_clicked)
        flip_buttons_layout.addWidget(h_flip_button)
        flip_buttons_layout.addWidget(v_flip_button)
        flip_group_layout.addLayout(flip_buttons_layout)
        self.add_layout(flip_group_layout)

        # --- 裁剪 ---
        crop_group_layout = QGridLayout()
        
        # 图像信息标签
        self.image_info_label = QLabel("图像尺寸: --")
        self.image_info_label.setStyleSheet("font-size: 11px; color: #666;")
        crop_group_layout.addWidget(self.image_info_label, 0, 0, 1, 4)
        
        # 裁剪参数
        crop_group_layout.addWidget(QLabel("X:"), 1, 0)
        self.crop_x_spinbox = QSpinBox()
        self.crop_x_spinbox.setRange(0, 10000)
        self.crop_x_spinbox.valueChanged.connect(self._update_crop_info)
        crop_group_layout.addWidget(self.crop_x_spinbox, 1, 1)

        crop_group_layout.addWidget(QLabel("Y:"), 1, 2)
        self.crop_y_spinbox = QSpinBox()
        self.crop_y_spinbox.setRange(0, 10000)
        self.crop_y_spinbox.valueChanged.connect(self._update_crop_info)
        crop_group_layout.addWidget(self.crop_y_spinbox, 1, 3)

        crop_group_layout.addWidget(QLabel("宽度:"), 2, 0)
        self.crop_width_spinbox = QSpinBox()
        self.crop_width_spinbox.setRange(1, 10000)
        self.crop_width_spinbox.setValue(100)
        self.crop_width_spinbox.valueChanged.connect(self._update_crop_info)
        crop_group_layout.addWidget(self.crop_width_spinbox, 2, 1)

        crop_group_layout.addWidget(QLabel("高度:"), 2, 2)
        self.crop_height_spinbox = QSpinBox()
        self.crop_height_spinbox.setRange(1, 10000)
        self.crop_height_spinbox.setValue(100)
        self.crop_height_spinbox.valueChanged.connect(self._update_crop_info)
        crop_group_layout.addWidget(self.crop_height_spinbox, 2, 3)
        
        # 裁剪区域信息
        self.crop_info_label = QLabel("裁剪区域: 100×100")
        self.crop_info_label.setStyleSheet("font-size: 11px; color: #444;")
        crop_group_layout.addWidget(self.crop_info_label, 3, 0, 1, 4)

        # 裁剪按钮
        crop_buttons_layout = QHBoxLayout()
        crop_preview_button = QPushButton("预览裁剪")
        crop_preview_button.clicked.connect(self._on_crop_preview_button_clicked)
        crop_buttons_layout.addWidget(crop_preview_button)

        crop_apply_button = QPushButton("应用裁剪")
        crop_apply_button.clicked.connect(self._on_crop_apply_button_clicked)
        crop_buttons_layout.addWidget(crop_apply_button)
        crop_group_layout.addLayout(crop_buttons_layout, 4, 0, 1, 4)
        self.add_layout(crop_group_layout)

    def _connect_rotate_signals(self):
        """连接旋转角度控件信号"""
        self.rotate_angle_widget.sliderPressed.connect(self._on_rotate_slider_pressed)
        self.rotate_angle_widget.sliderReleased.connect(self._on_rotate_slider_released)
        self.rotate_angle_widget.sliderMoved.connect(self._on_rotate_preview)
        self.rotate_angle_widget.editingFinished.connect(self._on_rotate_apply_button_clicked)
        
        # 添加调试输出
        self.rotate_angle_widget.valueChanged.connect(lambda v: print(f"GeometrySection: Rotate angle changed to {v}"))

    def _on_rotate_slider_pressed(self):
        """旋转滑块按下处理"""
        self._is_dragging_rotate = True
        print(f"GeometrySection: Rotate slider pressed")

    def _on_rotate_slider_released(self):
        """旋转滑块释放处理"""
        self._is_dragging_rotate = False
        params = {
            'angle': self.rotate_angle_widget.value(),
            'expand': self.rotate_expand_checkbox.isChecked(),
            'scale': 1.0
        }
        print(f"GeometrySection: Rotate slider released, emitting preview_requested with params: {params}")
        self.preview_requested.emit("rotate_preview", params)

    def _on_rotate_preview(self):
        """旋转预览处理"""
        # 仅当拖动滑块或复选框状态改变时触发预览
        if self._is_dragging_rotate or (self.sender() == self.rotate_expand_checkbox):
            params = {
                'angle': self.rotate_angle_widget.value(),
                'expand': self.rotate_expand_checkbox.isChecked(),
                'scale': 1.0
            }
            print(f"GeometrySection: Emitting preview_requested for rotate_preview with params: {params}")
            self.preview_requested.emit("rotate_preview", params)

    def _on_rotate_apply_button_clicked(self):
        """应用旋转按钮点击处理"""
        params = {
            'angle': self.rotate_angle_widget.value(),
            'expand': self.rotate_expand_checkbox.isChecked(),
            'scale': 1.0
        }
        print(f"GeometrySection: Emitting apply_requested for rotate with params: {params}")
        self.apply_requested.emit("rotate", params)

    def _on_h_flip_clicked(self):
        """水平翻转处理"""
        params = {'flip_code': 1}
        print(f"GeometrySection: Emitting apply_requested for flip with params: {params}")
        self.apply_requested.emit("flip", params)

    def _on_v_flip_clicked(self):
        """垂直翻转处理"""
        params = {'flip_code': 0}
        print(f"GeometrySection: Emitting apply_requested for flip with params: {params}")
        self.apply_requested.emit("flip", params)

    def _on_crop_preview_button_clicked(self):
        """预览裁剪处理"""
        params = {
            'x': self.crop_x_spinbox.value(),
            'y': self.crop_y_spinbox.value(),
            'width': self.crop_width_spinbox.value(),
            'height': self.crop_height_spinbox.value()
        }
        print(f"GeometrySection: Emitting preview_requested for crop with params: {params}")
        self.preview_requested.emit("crop", params)

    def _update_crop_info(self):
        """更新裁剪区域信息"""
        width = self.crop_width_spinbox.value()
        height = self.crop_height_spinbox.value()
        x = self.crop_x_spinbox.value()
        y = self.crop_y_spinbox.value()
        self.crop_info_label.setText(f"裁剪区域: {width}×{height} at ({x},{y})")

    def update_image_info(self, image_width, image_height):
        """更新图像信息
        
        Args:
            image_width: 图像宽度
            image_height: 图像高度
        """
        self.image_info_label.setText(f"图像尺寸: {image_width}×{image_height}")
        
        # 更新spinbox的最大值
        self.crop_x_spinbox.setMaximum(max(0, image_width - 1))
        self.crop_y_spinbox.setMaximum(max(0, image_height - 1))
        self.crop_width_spinbox.setMaximum(image_width)
        self.crop_height_spinbox.setMaximum(image_height)
        
        # 如果当前设置超出图像范围，调整为合理值
        if self.crop_x_spinbox.value() >= image_width:
            self.crop_x_spinbox.setValue(max(0, image_width - 100))
        if self.crop_y_spinbox.value() >= image_height:
            self.crop_y_spinbox.setValue(max(0, image_height - 100))
        if self.crop_width_spinbox.value() > image_width:
            self.crop_width_spinbox.setValue(min(100, image_width))
        if self.crop_height_spinbox.value() > image_height:
            self.crop_height_spinbox.setValue(min(100, image_height))

    def _on_crop_apply_button_clicked(self):
        """应用裁剪处理"""
        params = {
            'x': self.crop_x_spinbox.value(),
            'y': self.crop_y_spinbox.value(),
            'width': self.crop_width_spinbox.value(),
            'height': self.crop_height_spinbox.value()
        }
        print(f"GeometrySection: Emitting apply_requested for crop with params: {params}")
        self.apply_requested.emit("crop", params)

    def get_parameters(self, operation: str = None) -> dict:
        """获取参数（可选实现）"""
        if operation == "rotate":
            return {
                'angle': self.rotate_angle_widget.value(),
                'expand': self.rotate_expand_checkbox.isChecked(),
                'scale': 1.0
            }
        elif operation == "crop":
            return {
                'x': self.crop_x_spinbox.value(),
                'y': self.crop_y_spinbox.value(),
                'width': self.crop_width_spinbox.value(),
                'height': self.crop_height_spinbox.value()
            }
        return {}

    def set_parameters(self, operation: str, params: dict):
        """设置参数（可选实现）"""
        if operation == "rotate":
            if 'angle' in params:
                self.rotate_angle_widget.setValue(params['angle'])
            if 'expand' in params:
                self.rotate_expand_checkbox.setChecked(params['expand'])
        elif operation == "crop":
            if 'x' in params:
                self.crop_x_spinbox.setValue(params['x'])
            if 'y' in params:
                self.crop_y_spinbox.setValue(params['y'])
            if 'width' in params:
                self.crop_width_spinbox.setValue(params['width'])
            if 'height' in params:
                self.crop_height_spinbox.setValue(params['height'])