# views/adjustment_section_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox
# QLabel (如果基类会用到) 和 Signal (如果基类会定义通用信号) 可以按需导入
# from PySide6.QtCore import Signal

class AdjustmentSectionWidget(QGroupBox): # 直接继承 QGroupBox
    # 可以定义一些通用信号，如果所有调整部分都有类似的需求
    # 例如，如果每个部分都有自己的"应用"和"重置"按钮：
    # apply_clicked = Signal()
    # reset_clicked = Signal()
    # parameter_preview_requested = Signal(dict) # 用于实时预览
    # parameter_apply_requested = Signal(dict) # 用于最终应用

    def __init__(self, title: str, parent: QWidget = None):
        super().__init__(title, parent)
        self.setObjectName("adjustmentSection") # 便于QSS选择

        # 主布局，用于容纳子类添加的控件
        self.content_layout = QVBoxLayout()
        # QGroupBox 默认的 padding-top 通常由 title 占据, 
        # QSS中通常会为 QGroupBox::title 和 QGroupBox 设置 margin/padding 来美化
        # 我们让 content_layout 更贴近 QGroupBox 的边缘，具体的边距由QSS控制或在子类中细调
        self.content_layout.setContentsMargins(5, 5, 5, 5) 
        self.content_layout.setSpacing(8) # 控件之间的间距

        # QGroupBox 自身的布局 (也是一个 QVBoxLayout)
        # 我们将 content_layout 直接设置为 QGroupBox 的布局
        self.setLayout(self.content_layout)
        # 之前通过一个中间的 content_widget 的方式也可以，但直接设置布局更简洁一些
        # 如果发现QSS对QGroupBox的padding-top等设置与直接设置的布局有冲突，
        # 再考虑恢复使用中间的 content_widget

    def add_widget(self, widget: QWidget):
        """向内容布局中添加控件"""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout): # 明确类型
        """向内容布局中添加布局"""
        self.content_layout.addLayout(layout)

    def add_stretch(self):
        self.content_layout.addStretch()

    # 子类应重写这些方法
    def get_parameters(self, operation_prefix: str = None) -> dict:
        return {}

    def set_parameters(self, params: dict):
        pass