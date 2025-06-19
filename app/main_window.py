"""
主窗口模块
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QToolBar, QStatusBar, QFileDialog, QMessageBox,
                             QLabel, QProgressBar, QDockWidget)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QActionGroup
import os
import gc

from views.image_view import ImageView
from models.image_model import ImageModel
from controllers.image_controller import ImageController

from utils.memory_monitor import memory_monitor
from app.config import config
from views.inspector_panel import InspectorPanel

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("ImagePro")
        self.resize(1024, 768)     #窗口大小
        
        # 创建模型、视图和控制器
        self.image_model = ImageModel() #图像模型，在模型中处理图像的加载、保存、撤销、重做等操作(modeels文件夹image_model.py)
        self.image_view = ImageView() #图像视图，在视图中显示图像(views文件夹image_view.py)
        self.image_controller = ImageController(self.image_model) #图像控制器，在控制器中处理图像的预览、亮度、对比度、模糊等操作(controllers文件夹image_controller.py)

        # 创建 InspectorPanel 并放入 QDockWidget
        self.inspector_panel = InspectorPanel()
        self.inspector_panel.setObjectName("inspectorPanelMain")
        inspector_dock = QDockWidget("检查器", self)
        inspector_dock.setObjectName("inspectorDockWidget")
        inspector_dock.setWidget(self.inspector_panel)
        inspector_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        inspector_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.RightDockWidgetArea, inspector_dock)

        # 创建中央窗口容器，只包含 image_view
        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        central_layout.addWidget(self.image_view, stretch=1)
        self.setCentralWidget(central_widget)
        
        # 创建UI组件
        self._create_actions() #创建动作
        self._create_menus() #创建菜单
        self._create_toolbars() #创建工具栏
        self._create_statusbar() #创建状态栏
        
        # 连接信号和槽
        self._connect_signals()
        
        # 加载样式表
        self._load_stylesheet()
        
        # 初始化内存监控
        self._setup_memory_monitor()
        
        # 启动内存状态更新计时器
        self._start_memory_status_timer()
        
        # 初始化主题菜单
        self._initialize_theme_menu_state()
    
    def _setup_memory_monitor(self):
        """设置内存监控器"""
        # 注册模型和视图
        memory_monitor.register_image_model(self.image_model)
        memory_monitor.register_image_view(self.image_view)
        
        # 连接内存监控信号
        memory_monitor.memory_warning.connect(self._on_memory_warning)
        memory_monitor.memory_critical.connect(self._on_memory_critical)
        memory_monitor.memory_status.connect(self._on_memory_status)
        
        # 开始监控
        memory_monitor.start_monitoring()
    
    def _start_memory_status_timer(self):
        """启动内存状态更新计时器"""
        self._memory_timer = QTimer(self)
        self._memory_timer.timeout.connect(self._update_memory_status)
        self._memory_timer.start(2000)  # 每2秒更新一次状态
    
    def _update_memory_status(self):
        """更新内存状态显示"""
        if hasattr(self, '_memory_label') and hasattr(self, '_memory_bar'):
            memory_info = memory_monitor.get_memory_info()
            used_memory = memory_info['used']
            total_memory = memory_info['total']
            percent = memory_info['percent']
            
            # 更新内存标签
            self._memory_label.setText(f"内存: {used_memory:.0f}MB/{total_memory:.0f}MB")
            
            # 更新内存条
            self._memory_bar.setValue(int(percent))
            
            # 设置内存条颜色
            if percent > config.get('performance.auto_gc_threshold', 80):
                self._memory_bar.setStyleSheet("QProgressBar::chunk { background-color: #FF4444; }")
            elif percent > 70:
                self._memory_bar.setStyleSheet("QProgressBar::chunk { background-color: #FFAA44; }")
            else:
                self._memory_bar.setStyleSheet("QProgressBar::chunk { background-color: #44AA44; }")
    
    def _on_memory_warning(self, percent):
        """内存警告处理
        
        Args:
            percent: 内存使用百分比
        """
        self.statusBar.showMessage(f"内存使用率较高: {percent:.1f}%，系统将自动优化内存使用", 5000)
    
    def _on_memory_critical(self, percent):
        """内存危急处理
        
        Args:
            percent: 内存使用百分比
        """
        self.statusBar.showMessage(f"内存使用率过高: {percent:.1f}%，正在强制清理内存...", 5000)
        # 强制清理内存
        QTimer.singleShot(100, self._force_cleanup_memory)
    
    def _on_memory_status(self, memory_info):
        """内存状态处理
        
        Args:
            memory_info: 内存信息
        """
        # 可扩展为在日志中记录详细内存使用情况
        pass
    
    def _force_cleanup_memory(self):
        """强制清理内存"""
        # 清理图像处理缓存
        self.image_model.clear_memory()
        self.image_view.clear_cache()
        
        # 强制垃圾回收
        gc.collect()
        
        # 更新状态
        self.statusBar.showMessage("内存清理完成", 3000)
    
    def _create_actions(self):
        """创建动作"""
        # 文件操作
        self.open_action = QAction("打开", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._on_open)
        
        self.save_action = QAction("保存", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._on_save)
        
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # 编辑操作
        self.undo_action = QAction("撤销", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.triggered.connect(self._on_undo)
        
        self.redo_action = QAction("重做", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.triggered.connect(self._on_redo)
        
        # 优化操作
        self.cleanup_action = QAction("清理内存", self)
        self.cleanup_action.setShortcut("Ctrl+Shift+M")
        self.cleanup_action.setToolTip("手动清理内存缓存 (Ctrl+Shift+M)")
        self.cleanup_action.triggered.connect(self._force_cleanup_memory)

        # 新增主题切换动作
        self.set_dark_theme_action = QAction("暗色主题", self, checkable=True)
        self.set_dark_theme_action.setShortcut("Ctrl+Shift+D")
        self.set_dark_theme_action.setToolTip("切换到暗色主题 (Ctrl+Shift+D)")
        self.set_dark_theme_action.triggered.connect(lambda: self._set_theme("dark_theme"))

        self.set_light_theme_action = QAction("亮色主题", self, checkable=True)
        self.set_light_theme_action.setShortcut("Ctrl+Shift+L")
        self.set_light_theme_action.setToolTip("切换到亮色主题 (Ctrl+Shift+L)")
        self.set_light_theme_action.triggered.connect(lambda: self._set_theme("light_theme"))

        # 选项卡切换快捷键
        self.tab_1_action = QAction("主要调整", self)
        self.tab_1_action.setShortcut("Alt+1")
        self.tab_1_action.setToolTip("切换到主要调整选项卡 (Alt+1)")
        self.tab_1_action.triggered.connect(lambda: self._switch_tab(0))

        self.tab_2_action = QAction("效果滤镜", self)
        self.tab_2_action.setShortcut("Alt+2")
        self.tab_2_action.setToolTip("切换到效果滤镜选项卡 (Alt+2)")
        self.tab_2_action.triggered.connect(lambda: self._switch_tab(1))

        self.tab_3_action = QAction("几何变换", self)
        self.tab_3_action.setShortcut("Alt+3")
        self.tab_3_action.setToolTip("切换到几何变换选项卡 (Alt+3)")
        self.tab_3_action.triggered.connect(lambda: self._switch_tab(2))

        self.tab_4_action = QAction("图像分析", self)
        self.tab_4_action.setShortcut("Alt+4")
        self.tab_4_action.setToolTip("切换到图像分析选项卡 (Alt+4)")
        self.tab_4_action.triggered.connect(lambda: self._switch_tab(3))

        self.tab_5_action = QAction("自动处理", self)
        self.tab_5_action.setShortcut("Alt+5")
        self.tab_5_action.setToolTip("切换到自动处理选项卡 (Alt+5)")
        self.tab_5_action.triggered.connect(lambda: self._switch_tab(4))

        # 主题动作组，确保单选
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.addAction(self.set_dark_theme_action)
        self.theme_action_group.addAction(self.set_light_theme_action)
        self.theme_action_group.setExclusive(True)

    
    def _create_menus(self):
        """创建菜单"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        
        # 工具菜单
        tools_menu = self.menuBar().addMenu("工具")
        tools_menu.addAction(self.cleanup_action)

        # 新增视图菜单
        view_menu = self.menuBar().addMenu("视图")
        theme_menu = view_menu.addMenu("主题")
        theme_menu.addAction(self.set_dark_theme_action)
        theme_menu.addAction(self.set_light_theme_action)
        
        # 添加选项卡切换菜单
        view_menu.addSeparator()
        tab_menu = view_menu.addMenu("切换面板")
        tab_menu.addAction(self.tab_1_action)
        tab_menu.addAction(self.tab_2_action)
        tab_menu.addAction(self.tab_3_action)
        tab_menu.addAction(self.tab_4_action)
        tab_menu.addAction(self.tab_5_action)
    
    def _set_theme(self, theme_name: str):
        """设置主题
        Args:
            theme_name: 主题名称
        """
        config.set('ui.theme', theme_name)
        self._load_stylesheet() # 重新加载样式表

        # 尝试强制更新 ImageView viewport
        if hasattr(self, 'image_view') and self.image_view:
            self.image_view.viewport().update() # 请求重绘viewport

        if theme_name == "dark_theme":
            self.set_dark_theme_action.setChecked(True)
        elif theme_name == "light_theme":
            self.set_light_theme_action.setChecked(True)

    def _switch_tab(self, tab_index: int):
        """切换到指定的选项卡"""
        if hasattr(self, 'inspector_panel') and hasattr(self.inspector_panel, 'tab_widget'):
            if 0 <= tab_index < self.inspector_panel.tab_widget.count():
                self.inspector_panel.tab_widget.setCurrentIndex(tab_index)
                # 显示切换状态信息
                tab_names = ["主要调整", "效果滤镜", "几何变换", "图像分析", "自动处理"]
                if tab_index < len(tab_names):
                    self.statusBar.showMessage(f"已切换到 {tab_names[tab_index]} 面板", 2000)

    def _create_toolbars(self):
        """创建工具栏"""
        # 文件工具栏
        file_toolbar = QToolBar("文件")
        file_toolbar.setIconSize(QSize(24, 24))
        file_toolbar.addAction(self.open_action)
        file_toolbar.addAction(self.save_action)
        self.addToolBar(file_toolbar)
        
        # 编辑工具栏
        edit_toolbar = QToolBar("编辑")
        edit_toolbar.setIconSize(QSize(24, 24))
        edit_toolbar.addAction(self.undo_action)
        edit_toolbar.addAction(self.redo_action)
        self.addToolBar(edit_toolbar)
    
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 添加内存使用指示器
        self._memory_label = QLabel("内存: 0MB/0MB")
        self.statusBar.addPermanentWidget(self._memory_label)
        
        # 添加内存使用进度条
        self._memory_bar = QProgressBar()
        self._memory_bar.setFixedWidth(100)
        self._memory_bar.setRange(0, 100)
        self._memory_bar.setValue(0)
        self._memory_bar.setTextVisible(False)
        self.statusBar.addPermanentWidget(self._memory_bar)
        
        self.statusBar.showMessage("就绪")
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 图像模型信号
        self.image_model.image_changed.connect(self._on_image_changed)
        self.image_model.error_occurred.connect(self._on_error)
        
        # 图像视图信号
        self.image_view.image_changed.connect(self._on_view_changed)
        self.image_view.local_exposure_position_selected.connect(self._on_local_exposure_position_selected)
        
        # InspectorPanel 信号
        self.inspector_panel.process_requested.connect(self._on_process_requested)
        self.inspector_panel.preview_requested.connect(self._on_preview_requested)
        
        # 确保这些 hasattr 检查仍然有效，因为 InspectorPanel 中的这些信号暂时是占位符
        if hasattr(self.inspector_panel, 'cancel_preview_requested'):
            self.inspector_panel.cancel_preview_requested.connect(self._on_cancel_preview)
        if hasattr(self.inspector_panel, 'histogram_requested'):
            self.inspector_panel.histogram_requested.connect(self._on_histogram_requested)
        if hasattr(self.inspector_panel, 'local_exposure_selected'):
            self.inspector_panel.local_exposure_selected.connect(self._on_local_exposure_mode_changed)
    
    def _load_stylesheet(self): # 添加一个参数，或者从config读取
        theme_name = config.get('ui.theme', 'dark_theme') # 从配置读取主题名称
        style_filename = f"{theme_name}.qss"
         # ... (rest of your _load_stylesheet method, using style_filename) ...
        # Ensure this part is robust as in your previous successful attempt
        style_path = os.path.join(os.path.dirname(__file__), "..", "resources", "styles", style_filename)
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
            print(f"成功加载样式表: {style_path}")
        except Exception as e:
            print(f"加载样式表 '{style_filename}' 失败: {e}")
            # Fallback to a very basic default if specific theme fails
            if theme_name != "default_fallback": # Avoid recursion
                print("尝试加载默认备用样式...")
                self._load_stylesheet(theme_name="default_fallback") # Assumes you have a default_fallback.qss

    def _initialize_theme_menu_state(self):
        current_theme = config.get('ui.theme', 'dark_theme')
        if current_theme == "dark_theme":
            self.set_dark_theme_action.setChecked(True)
        elif current_theme == "light_theme":
            self.set_light_theme_action.setChecked(True)
        # 确保在启动时加载一次正确的样式表
        self._load_stylesheet()
    
    def _on_open(self):
        """打开文件处理"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开图像",
            "",
            "图像文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            # 打开大文件前先清理内存
            self._force_cleanup_memory()
            self.image_model.load_image(file_path)
    
    def _on_save(self):
        """保存文件处理"""
        if not self.image_model.has_image():
            QMessageBox.warning(self, "警告", "没有图像可保存")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图像",
            "",
            "PNG图像 (*.png);;JPEG图像 (*.jpg);;BMP图像 (*.bmp)"
        )
        if file_path:
            self.image_model.save_image(file_path)
    
    def _on_undo(self):
        """撤销操作处理"""
        self.image_model.undo()
    
    def _on_redo(self):
        """重做操作处理"""
        self.image_model.redo()
    
    def _on_process_requested(self, operation: str, parameters: dict):
        print(f"MainWindow: Process requested - Operation: {operation}, Parameters: {parameters}") # 调试
        try:
            if operation == "brightness_contrast":
                self.image_controller.adjust_brightness_contrast(
                    brightness=parameters['brightness'],
                    contrast=parameters['contrast']
                )
            elif operation == "blur":
                blur_type = parameters.get('blur_type', 'gaussian')
                if blur_type == 'gaussian':
                    self.image_controller.apply_gaussian_blur(
                        parameters.get('kernel_size', 3),
                        parameters.get('sigma', 0)
                    )
                elif blur_type == 'median':
                    self.image_controller.apply_median_blur(
                        parameters.get('kernel_size', 3)
                    )
                elif blur_type == 'bilateral':
                    self.image_controller.apply_bilateral_filter(
                        parameters.get('d', 9),
                        parameters.get('sigma_color', 75),
                        parameters.get('sigma_space', 75)
                    )
            elif operation == "rotate":
                print("Processing rotate...") # 调试
                self.image_controller.rotate_image(
                    angle=parameters.get('angle', 0),
                    scale=parameters.get('scale', 1.0), # 确保 ImageController.rotate_image 处理 scale
                    expand=parameters.get('expand', False)
                )
            elif operation == "flip":
                print("Processing flip...") # 调试
                self.image_controller.flip_image(
                    parameters.get('flip_code', 1)
                )
            elif operation == "crop":
                print("Processing crop...") # 调试
                self.image_controller.crop_image(
                    parameters.get('x', 0),
                    parameters.get('y', 0),
                    parameters.get('width', 100),
                    parameters.get('height', 100)
                )
            elif operation == "apply_preview":
                self.image_controller.apply_last_preview()
            elif operation == "laplacian":
                self.image_controller.apply_laplacian_sharpen(
                    kernel_size=parameters.get('kernel_size', 3),
                    strength=parameters.get('strength', 1.0)
                )
            elif operation == "usm":
                self.image_controller.apply_usm_sharpen(
                    radius=parameters.get('radius', 5),
                    amount=parameters.get('amount', 1.0),
                    threshold=parameters.get('threshold', 0)
                )
            elif operation == "histogram_equalization":
                self.image_controller.apply_histogram_equalization(
                    per_channel=parameters.get('per_channel', False)
                )
                # 直方图均衡化后自动刷新直方图显示
                self._refresh_histogram_display()
            elif operation == "exposure":
                self.image_controller.adjust_exposure(
                    exposure=parameters.get('exposure', 0.0)
                )
            elif operation == "highlights":
                self.image_controller.adjust_highlights(
                    highlights=parameters.get('highlights', 0.0)
                )
            elif operation == "shadows":
                self.image_controller.adjust_shadows(
                    shadows=parameters.get('shadows', 0.0)
                )
            elif operation == "local_exposure":
                self.image_controller.adjust_local_exposure(
                    center_x=parameters.get('center_x', 0),
                    center_y=parameters.get('center_y', 0),
                    radius=parameters.get('radius', 100),
                    strength=parameters.get('strength', 0.5)
                )
            elif operation == "auto_contrast":
                self.image_controller.apply_auto_contrast(
                    clip_limit=parameters.get('clip_limit', 2.0),
                    tile_grid_size=parameters.get('tile_grid_size', (8, 8))
                )
            elif operation == "auto_color":
                self.image_controller.apply_auto_color(
                    saturation_scale=parameters.get('saturation_scale', 1.3),
                    vibrance_scale=parameters.get('vibrance_scale', 1.2)
                )
            elif operation == "auto_white_balance":
                self.image_controller.apply_auto_white_balance(
                    method=parameters.get('method', 'adaptive')
                )
            elif operation == "auto_all":
                self.image_controller.apply_auto_all(
                    contrast=parameters.get('contrast', True),
                    color=parameters.get('color', True),
                    white_balance=parameters.get('white_balance', True)
                )
            elif operation == "one_click_optimize":
                # 处理一键优化操作，参数名称需要映射
                self.image_controller.apply_auto_all(
                    contrast=parameters.get('enable_contrast', True),
                    color=parameters.get('enable_color', True),
                    white_balance=parameters.get('enable_wb', True)
                )
            elif operation == "rotate":
                self.image_controller.rotate_image(
                    angle=parameters.get('angle', 0),
                    scale=parameters.get('scale', 1.0),
                    expand=parameters.get('expand', False)
                )
            elif operation == "flip":
                self.image_controller.flip_image(
                    flip_code=parameters.get('flip_code', 1)
                )
            elif operation == "crop":
                self.image_controller.crop_image(
                    x=parameters.get('x', 0),
                    y=parameters.get('y', 0),
                    width=parameters.get('width', 100),
                    height=parameters.get('height', 100)
                )
            
            # 更新状态栏
            self.statusBar.showMessage(f"已应用{operation}处理", 3000)
            
        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            self._show_error_message("处理操作失败", error_msg)
            self.statusBar.showMessage(error_msg, 5000)
            import traceback # 详细错误信息
            traceback.print_exc() # 详细错误信息
    
    def _on_image_changed(self):
        """图像发生变化时的回调"""
        self.image_view.update_image(self.image_model.current_image)
        
        # 更新裁剪面板的图像信息
        if self.image_model.has_image():
            current_image = self.image_model.current_image
            if current_image is not None:
                height, width = current_image.shape[:2]
                if hasattr(self.inspector_panel, 'geometry_section'):
                    self.inspector_panel.geometry_section.update_image_info(width, height)
                
                # 自动刷新直方图显示
                self._refresh_histogram_display()
    
    def _on_view_changed(self):
        """视图发生变化时的回调"""
        pass
    
    def _on_error(self, message):
        """错误处理"""
        self._show_error_message("图像处理错误", message)
    
    def _show_error_message(self, title: str, message: str):
        """统一的错误消息显示方法
        
        Args:
            title: 错误标题
            message: 错误详细信息
        """
        # 记录错误到控制台
        print(f"[错误] {title}: {message}")
        
        # 显示用户友好的错误对话框
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # 添加详细信息按钮
        if len(message) > 100:  # 长消息提供详细信息
            msg_box.setDetailedText(message)
            msg_box.setText(message[:100] + "...")
        
        # 添加重试和帮助按钮
        retry_button = msg_box.addButton("重试", QMessageBox.AcceptRole)
        help_button = msg_box.addButton("帮助", QMessageBox.HelpRole)
        msg_box.addButton(QMessageBox.Ok)
        
        result = msg_box.exec()
        
        # 处理按钮点击
        if msg_box.clickedButton() == help_button:
            self._show_help_dialog()
        elif msg_box.clickedButton() == retry_button:
            # 可以在这里添加重试逻辑
            self.statusBar.showMessage("操作已取消，可以重试", 3000)
    
    def _show_help_dialog(self):
        """显示帮助对话框"""
        help_text = """
        <h3>图像处理软件使用帮助</h3>
        <p><b>常见问题解决方案：</b></p>
        <ul>
        <li><b>内存不足：</b>尝试使用 Ctrl+Shift+M 清理内存，或处理较小的图像</li>
        <li><b>图像无法加载：</b>检查图像格式是否支持 (PNG, JPG, BMP, GIF)</li>
        <li><b>处理速度慢：</b>降低图像分辨率或调整参数范围</li>
        <li><b>快捷键：</b>Alt+1-5 切换面板，Ctrl+Z/Y 撤销重做</li>
        </ul>
        <p><b>获得更多帮助：</b></p>
        <p>查看用户手册或联系技术支持</p>
        """
        
        help_dialog = QMessageBox(self)
        help_dialog.setIcon(QMessageBox.Information)
        help_dialog.setWindowTitle("使用帮助")
        help_dialog.setText(help_text)
        help_dialog.exec()
    
    def _on_local_exposure_position_selected(self, x, y):
        """局部曝光位置选择处理
        
        Args:
            x: X坐标
            y: Y坐标
        """
        if hasattr(self.inspector_panel, 'set_local_exposure_position'):
            self.inspector_panel.set_local_exposure_position(x, y)
    
    def _on_local_exposure_mode_changed(self, enabled):
        """局部曝光模式切换处理
        
        Args:
            enabled: 是否启用局部曝光模式
        """
        self.image_view.set_local_exposure_mode(enabled)
    
    def _on_cancel_preview(self):
        """取消预览处理"""
        # 重置视图以取消预览效果
        self.image_view.update_image(self.image_model.current_image)
    
    def _on_histogram_requested(self, parameters):
        """直方图数据请求处理
        
        Args:
            parameters: 请求参数
        """
        channel = parameters.get('channel')
        
        # 转换字符串通道参数为数字索引
        channel_index = None
        if channel == "red":
            channel_index = 2  # OpenCV顺序：BGR，红色是索引2
        elif channel == "green":
            channel_index = 1
        elif channel == "blue":
            channel_index = 0
        elif channel == "all":
            channel_index = None  # 所有通道
        
        print(f"MainWindow: Requesting histogram for channel: {channel} (index: {channel_index})")
        hist_data = self.image_controller.calculate_histogram(channel=channel_index)
        if hist_data is not None:
            print(f"MainWindow: Received histogram data, updating panel")
            if hasattr(self.inspector_panel, 'update_histogram'):
                self.inspector_panel.update_histogram(hist_data)
    
    def _on_preview_requested(self, operation: str, parameters: dict):
        print(f"MainWindow: Preview requested - Operation: {operation}, Parameters: {parameters}") # 调试
        try:
            if operation == "brightness_contrast":
                self.image_controller.preview_brightness_contrast(
                    brightness=parameters['brightness'],
                    contrast=parameters['contrast']
                )
            elif operation == "rotate_preview":
                print("Previewing rotate...") # 调试
                self.image_controller.preview_rotate_image(
                    angle=parameters.get('angle', 0),
                    scale=parameters.get('scale', 1.0), # 确保 ImageController.preview_rotate_image 处理 scale
                    expand=parameters.get('expand', False)
                )
            elif operation == "crop":
                self.image_controller.preview_crop_image(
                    parameters.get('x', 0),
                    parameters.get('y', 0),
                    parameters.get('width', 100),
                    parameters.get('height', 100)
                )
            elif operation == "blur":
                blur_type = parameters.get('blur_type', 'gaussian')
                if blur_type == 'gaussian':
                    self.image_controller.apply_gaussian_blur(
                        parameters.get('kernel_size', 3),
                        parameters.get('sigma', 0)
                    )
                elif blur_type == 'median':
                    self.image_controller.apply_median_blur(
                        parameters.get('kernel_size', 3)
                    )
                elif blur_type == 'bilateral':
                    self.image_controller.apply_bilateral_filter(
                        parameters.get('d', 9),
                        parameters.get('sigma_color', 75),
                        parameters.get('sigma_space', 75)
                    )
            elif operation == "laplacian":
                self.image_controller.preview_laplacian_sharpen(
                    kernel_size=parameters.get('kernel_size', 3),
                    strength=parameters.get('strength', 1.0)
                )
            elif operation == "usm":
                self.image_controller.preview_usm_sharpen(
                    radius=parameters.get('radius', 5),
                    amount=parameters.get('amount', 1.0),
                    threshold=parameters.get('threshold', 0)
                )
            elif operation == "histogram_equalization":
                self.image_controller.preview_histogram_equalization(
                    per_channel=parameters.get('per_channel', False)
                )
            elif operation == "exposure":
                self.image_controller.preview_exposure(
                    exposure=parameters.get('exposure', 0.0)
                )
            elif operation == "highlights":
                self.image_controller.preview_highlights(
                    highlights=parameters.get('highlights', 0.0)
                )
            elif operation == "shadows":
                self.image_controller.preview_shadows(
                    shadows=parameters.get('shadows', 0.0)
                )
            elif operation == "local_exposure":
                self.image_controller.preview_local_exposure(
                    center_x=parameters.get('center_x', 0),
                    center_y=parameters.get('center_y', 0),
                    radius=parameters.get('radius', 100),
                    strength=parameters.get('strength', 0.5)
                )
            elif operation == "auto_contrast":
                self.image_controller.preview_auto_contrast(
                    clip_limit=parameters.get('clip_limit', 2.0),
                    tile_grid_size=parameters.get('tile_grid_size', (8, 8))
                )
            elif operation == "auto_color":
                self.image_controller.preview_auto_color(
                    saturation_scale=parameters.get('saturation_scale', 1.3),
                    vibrance_scale=parameters.get('vibrance_scale', 1.2)
                )
            elif operation == "auto_white_balance":
                self.image_controller.preview_auto_white_balance(
                    method=parameters.get('method', 'adaptive')
                )
            elif operation == "auto_all":
                self.image_controller.preview_auto_all(
                    contrast=parameters.get('contrast', True),
                    color=parameters.get('color', True),
                    white_balance=parameters.get('white_balance', True)
                )
            elif operation == "one_click_optimize":
                # 处理一键优化预览操作，参数名称需要映射
                self.image_controller.preview_auto_all(
                    contrast=parameters.get('enable_contrast', True),
                    color=parameters.get('enable_color', True),
                    white_balance=parameters.get('enable_wb', True)
                )
            elif operation == "flip":
                self.image_controller.preview_flip_image(
                    flip_code=parameters.get('flip_code', 1)
                )
            
        except Exception as e:
            self.statusBar.showMessage(f"预览失败: {str(e)}", 3000)
            import traceback # 详细错误信息
            traceback.print_exc() # 详细错误信息
    
    def _refresh_histogram_display(self):
        """刷新直方图显示
        
        在图像处理操作后自动更新直方图，让用户看到变化效果
        """
        try:
            if hasattr(self.inspector_panel, 'histogram_section'):
                # 获取当前选择的通道
                current_channel = self.inspector_panel.histogram_section.channel_combo.currentData()
                
                # 请求更新直方图数据
                parameters = {'channel': current_channel}
                print(f"MainWindow: Auto-refreshing histogram for channel: {current_channel}")
                self._on_histogram_requested(parameters)
                
        except Exception as e:
            print(f"MainWindow: Error refreshing histogram display: {e}") 