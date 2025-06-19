# views/inspector_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QScrollArea, \
                              QSlider, QSpinBox, QDoubleSpinBox, QHBoxLayout # 新增导入
from PySide6.QtCore import Signal, Qt # 新增导入

from .adjustment_section_widget import AdjustmentSectionWidget 
# 假设旧的 BrightnessContrastPanel 的核心逻辑被移到一个新类或方法中
from .tone_adjustment_section import ToneAdjustmentSection
from .filter_sections import BlurSection, SharpenSection
from .transform_sections import GeometrySection # 假设您创建了 transform_sections.py
from .analysis_sections import HistogramSection
from .auto_process_sections import (OneClickOptimizeSection, AutoContrastSection, 
                                   AutoColorSection, AutoWhiteBalanceSection)

# --- 创建具体的调整部分 ---
class BrightnessContrastSection(AdjustmentSectionWidget):
    # 定义信号，专属于这个部分
    preview_requested = Signal(dict)
    apply_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("亮度 / 对比度", parent) # 设置 QGroupBox 的标题
        self._is_dragging = False
        self._ignore_value_change = False
        self._build_ui()

    def _build_ui(self):
        # 亮度调整 (从旧的 BrightnessContrastPanel 迁移控件创建逻辑)
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("亮度:")
        self.brightness_slider = QSlider(Qt.Horizontal)
        # ... (设置范围、值、信号连接等，参照旧 BrightnessContrastPanel) ...
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.sliderPressed.connect(self._on_slider_pressed)
        self.brightness_slider.sliderReleased.connect(self._on_slider_released) # 应用更改
        self.brightness_slider.sliderMoved.connect(self._on_parameter_preview) # 实时预览

        self.brightness_spinbox = QSpinBox()
        self.brightness_spinbox.setRange(-100, 100)
        self.brightness_spinbox.setValue(0)
        # ... (信号连接) ...
        self.brightness_slider.valueChanged.connect(self._sync_brightness_spinbox)
        self.brightness_spinbox.valueChanged.connect(self._sync_brightness_slider)
        self.brightness_spinbox.editingFinished.connect(self._on_spinbox_apply)


        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_spinbox)
        self.add_layout(brightness_layout) # 使用父类的方法添加布局

        # 对比度调整 (类似迁移)
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("对比度:")
        self.contrast_slider = QSlider(Qt.Horizontal)
        # ... (设置范围、值、信号连接等) ...
        self.contrast_slider.setRange(50, 200) # 0.5 to 2.0
        self.contrast_slider.setValue(100)
        self.contrast_slider.sliderPressed.connect(self._on_slider_pressed)
        self.contrast_slider.sliderReleased.connect(self._on_slider_released)
        self.contrast_slider.sliderMoved.connect(self._on_parameter_preview)


        self.contrast_spinbox = QDoubleSpinBox()
        self.contrast_spinbox.setRange(0.5, 2.0)
        self.contrast_spinbox.setValue(1.0)
        self.contrast_spinbox.setSingleStep(0.01) # 更精细的步长
        # ... (信号连接) ...
        self.contrast_slider.valueChanged.connect(self._sync_contrast_spinbox)
        self.contrast_spinbox.valueChanged.connect(self._sync_contrast_slider)
        self.contrast_spinbox.editingFinished.connect(self._on_spinbox_apply)


        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_spinbox)
        self.add_layout(contrast_layout)

    def _on_slider_pressed(self):
        self._is_dragging = True

    def _on_slider_released(self):
        self._is_dragging = False
        self.apply_requested.emit(self.get_parameters()) # 滑块释放时应用

    def _on_parameter_preview(self):
        if self._is_dragging: # 仅在拖动时实时预览
            self.preview_requested.emit(self.get_parameters())

    def _on_spinbox_apply(self):
        self.apply_requested.emit(self.get_parameters()) # SpinBox 输入完成时应用

    def _sync_brightness_slider(self, value):
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.brightness_slider.setValue(value)
            self._ignore_value_change = False
    def _sync_brightness_spinbox(self, value):
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.brightness_spinbox.setValue(value)
            self._ignore_value_change = False
            # self._on_parameter_preview() # 如果希望滑块变化也实时预览

    def _sync_contrast_slider(self, value): # value from spinbox (float)
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.contrast_slider.setValue(int(value * 100))
            self._ignore_value_change = False
    def _sync_contrast_spinbox(self, value): # value from slider (int)
        if not self._ignore_value_change:
            self._ignore_value_change = True
            self.contrast_spinbox.setValue(value / 100.0)
            self._ignore_value_change = False
            # self._on_parameter_preview() # 如果希望滑块变化也实时预览


    def get_parameters(self) -> dict:
        return {
            'brightness': self.brightness_spinbox.value(),
            'contrast': self.contrast_spinbox.value()
        }

    def set_parameters(self, params: dict): # 用于重置等
        self.brightness_spinbox.setValue(params.get('brightness', 0))
        self.contrast_spinbox.setValue(params.get('contrast', 1.0))


class InspectorPanel(QWidget):
    # 主信号，由 MainWindow 连接
    process_requested = Signal(str, dict)
    preview_requested = Signal(str, dict)
    cancel_preview_requested = Signal() # 这个可能不再由各子面板发出，而是InspectorPanel或MainWindow管理
    histogram_requested = Signal(dict) # 新增
    local_exposure_selected = Signal(bool) # 新增
    # ... 其他需要的信号 ...

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inspectorPanel")
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("inspectorTabWidget")
        # 设置选项卡的工具提示
        self.tab_widget.setToolTip("选择不同的图像处理类别。支持快捷键切换：Alt+1-5")

        # --- 调整选项卡 ---
        adjustments_tab_scroll_area = QScrollArea() # 使内容可滚动
        adjustments_tab_scroll_area.setWidgetResizable(True)
        adjustments_tab_scroll_area.setObjectName("adjustmentsScrollArea")
        adjustments_tab_scroll_area.setToolTip("主要图像调整工具：亮度、对比度、曝光、高光、阴影等")

        adjustments_tab_content_widget = QWidget() # QScrollArea 需要一个 QWidget 作为其子控件
        adjustments_tab_layout = QVBoxLayout(adjustments_tab_content_widget)
        adjustments_tab_layout.setContentsMargins(8, 8, 8, 8)
        adjustments_tab_layout.setSpacing(10) # 各个 Section 之间的间距

        # 移除旧的 brightness_contrast_section
        # self.brightness_contrast_section = BrightnessContrastSection()
        # adjustments_tab_layout.addWidget(self.brightness_contrast_section)

        # 添加新的 ToneAdjustmentSection
        self.tone_adjustment_section = ToneAdjustmentSection()
        self.tone_adjustment_section.setToolTip("调整图像的色调：亮度、对比度、曝光、高光和阴影。拖动滑块时实时预览，释放时应用")
        adjustments_tab_layout.addWidget(self.tone_adjustment_section)

        # 在这里添加其他调整部分，例如 ExposureSection, ColorSection 等
        # dummy_exposure_section = AdjustmentSectionWidget("曝光")
        # dummy_exposure_section.add_widget(QLabel("曝光控件..."))
        # adjustments_tab_layout.addWidget(dummy_exposure_section)

        adjustments_tab_layout.addStretch() # 将所有内容推到顶部
        adjustments_tab_scroll_area.setWidget(adjustments_tab_content_widget)
        self.tab_widget.addTab(adjustments_tab_scroll_area, "主要调整")


        # --- 滤镜选项卡 ---
        filters_tab_content = QWidget()
        filters_layout = QVBoxLayout(filters_tab_content)
        # ... (添加滤镜相关的 AdjustmentSectionWidget 实例) ...
        # self.dummy_blur_section = AdjustmentSectionWidget("模糊") # Remove this
        # filters_layout.addWidget(self.dummy_blur_section) # Remove this

        self.blur_section = BlurSection()
        self.blur_section.setToolTip("应用各种模糊效果：高斯模糊、中值滤波、双边滤波。数值越大效果越强")
        filters_layout.addWidget(self.blur_section)

        self.sharpen_section = SharpenSection()
        self.sharpen_section.setToolTip("锐化图像细节：拉普拉斯锐化、USM锐化。适度使用，过度锐化会产生噪点")
        filters_layout.addWidget(self.sharpen_section)

        filters_layout.addStretch()
        filters_tab_content.setToolTip("图像效果滤镜：模糊、锐化等后期处理效果")
        self.tab_widget.addTab(filters_tab_content, "效果滤镜")

        # --- 变换与裁剪选项卡 ---
        transform_scroll_area = QScrollArea()
        transform_scroll_area.setWidgetResizable(True)
        transform_scroll_area.setObjectName("transformScrollArea")
        transform_scroll_area.setToolTip("几何变换工具：旋转、翻转、裁剪图像。支持精确的数值输入")

        transform_tab_content_widget = QWidget()
        transform_layout = QVBoxLayout(transform_tab_content_widget)
        transform_layout.setContentsMargins(8,8,8,8)
        transform_layout.setSpacing(10)
        
        self.geometry_section = GeometrySection() # 实例化
        self.geometry_section.setToolTip("旋转角度：-180°至180°，勾选'扩展'避免裁剪。翻转：水平/垂直。裁剪：输入精确坐标和尺寸")
        transform_layout.addWidget(self.geometry_section)
        
        transform_layout.addStretch()
        transform_scroll_area.setWidget(transform_tab_content_widget)
        self.tab_widget.addTab(transform_scroll_area, "变换与裁剪") # 添加选项卡

        # --- 图像分析选项卡 ---
        analysis_scroll_area = QScrollArea()
        analysis_scroll_area.setWidgetResizable(True)
        analysis_scroll_area.setObjectName("analysisScrollArea")
        analysis_scroll_area.setToolTip("图像分析工具：直方图显示、通道分析、统计信息等")

        analysis_tab_content_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab_content_widget)
        analysis_layout.setContentsMargins(8, 8, 8, 8)
        analysis_layout.setSpacing(10)
        
        self.histogram_section = HistogramSection()
        self.histogram_section.setToolTip("显示图像的直方图分布。可以选择查看全部通道或单独的红、绿、蓝通道，支持直方图均衡化")
        analysis_layout.addWidget(self.histogram_section)
        
        analysis_layout.addStretch()
        analysis_scroll_area.setWidget(analysis_tab_content_widget)
        self.tab_widget.addTab(analysis_scroll_area, "图像分析")

        # --- 自动处理选项卡 ---
        auto_process_scroll_area = QScrollArea()
        auto_process_scroll_area.setWidgetResizable(True)
        auto_process_scroll_area.setObjectName("autoProcessScrollArea")
        auto_process_scroll_area.setToolTip("智能自动处理工具：一键优化、自动对比度、色彩校正、白平衡等")

        auto_process_tab_content_widget = QWidget()
        auto_process_layout = QVBoxLayout(auto_process_tab_content_widget)
        auto_process_layout.setContentsMargins(8, 8, 8, 8)
        auto_process_layout.setSpacing(10)
        
        # 添加各种自动处理功能
        self.one_click_optimize_section = OneClickOptimizeSection()
        self.one_click_optimize_section.setToolTip("一键智能优化图像：自动调整对比度、色彩和白平衡。适合快速处理大部分图像")
        auto_process_layout.addWidget(self.one_click_optimize_section)
        
        self.auto_contrast_section = AutoContrastSection()
        self.auto_contrast_section.setToolTip("自动对比度增强：使用CLAHE算法提升图像细节，调整限制值避免过度增强")
        auto_process_layout.addWidget(self.auto_contrast_section)
        
        self.auto_color_section = AutoColorSection()
        self.auto_color_section.setToolTip("自动色彩校正：增强图像的饱和度和鲜艳度，让色彩更加生动")
        auto_process_layout.addWidget(self.auto_color_section)
        
        self.auto_white_balance_section = AutoWhiteBalanceSection()
        self.auto_white_balance_section.setToolTip("自动白平衡调整：校正图像色温，消除偏色。支持灰度世界、完美反射和自适应算法")
        auto_process_layout.addWidget(self.auto_white_balance_section)
        
        auto_process_layout.addStretch()
        auto_process_scroll_area.setWidget(auto_process_tab_content_widget)
        self.tab_widget.addTab(auto_process_scroll_area, "自动处理")

        # 添加主布局和连接信号（在所有Section创建完成后）
        main_layout.addWidget(self.tab_widget)
        self._connect_signals()

    def _connect_signals(self):
        # 移除旧的 brightness_contrast_section 信号连接
        # self.brightness_contrast_section.preview_requested.connect(...)
        # self.brightness_contrast_section.apply_requested.connect(...)

        # 连接新的 tone_adjustment_section 的信号
        self.tone_adjustment_section.preview_requested.connect(self.preview_requested)
        self.tone_adjustment_section.apply_requested.connect(self.process_requested)
        # 如果 ToneAdjustmentSection 内部也处理局部曝光的激活，则连接相应信号
        # if hasattr(self.tone_adjustment_section, 'local_exposure_mode_toggled'):
        #     self.tone_adjustment_section.local_exposure_mode_toggled.connect(self.local_exposure_selected)
        # if hasattr(self.tone_adjustment_section, 'cancel_preview'):
        #     self.tone_adjustment_section.cancel_preview.connect(self.cancel_preview_requested)

        if hasattr(self, 'blur_section'):
            self.blur_section.preview_requested.connect(self.preview_requested)
            self.blur_section.apply_requested.connect(self.process_requested)

        if hasattr(self, 'sharpen_section'):
            self.sharpen_section.preview_requested.connect(self.preview_requested)
            self.sharpen_section.apply_requested.connect(self.process_requested)
    
        if hasattr(self, 'geometry_section'):
            self.geometry_section.apply_requested.connect(self.process_requested)
            self.geometry_section.preview_requested.connect(self.preview_requested)
            # 如果 GeometrySection 有 cancel_preview_requested, 也在这里连接
            # if hasattr(self.geometry_section, 'cancel_preview_requested'):
            # self.geometry_section.cancel_preview_requested.connect(self.cancel_preview_requested)
        
        if hasattr(self, 'histogram_section'):
            self.histogram_section.apply_requested.connect(self.process_requested)
            self.histogram_section.preview_requested.connect(self.preview_requested)
            self.histogram_section.histogram_requested.connect(self.histogram_requested)
        
        # 连接自动处理模块的信号
        if hasattr(self, 'one_click_optimize_section'):
            self.one_click_optimize_section.apply_requested.connect(self.process_requested)
            self.one_click_optimize_section.preview_requested.connect(self.preview_requested)
        
        if hasattr(self, 'auto_contrast_section'):
            self.auto_contrast_section.apply_requested.connect(self.process_requested)
            self.auto_contrast_section.preview_requested.connect(self.preview_requested)
        
        if hasattr(self, 'auto_color_section'):
            self.auto_color_section.apply_requested.connect(self.process_requested)
            self.auto_color_section.preview_requested.connect(self.preview_requested)
        
        if hasattr(self, 'auto_white_balance_section'):
            self.auto_white_balance_section.apply_requested.connect(self.process_requested)
            self.auto_white_balance_section.preview_requested.connect(self.preview_requested)

    # 供 MainWindow 调用的方法
    def update_histogram(self, hist_data):
        print(f"InspectorPanel: 更新直方图数据")
        if hasattr(self, 'histogram_section'):
            self.histogram_section.update_histogram(hist_data)

    def set_local_exposure_position(self, x, y):
        print(f"InspectorPanel: 设置局部曝光位置 ({x}, {y}) (待实现)")        # if hasattr(self, 'exposure_section'): # 假设曝光部分处理这个
        #     self.exposure_section.set_local_position(x, y)
