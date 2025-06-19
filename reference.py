import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageDraw
from PIL.Image import Resampling
import cv2
import numpy as np
import torch
from torchvision.transforms import ToTensor, ToPILImage
import os
from basicsr.archs.rrdbnet_arch import RRDBNet
# 内存优化配置
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"  # 减少内存碎片
torch.backends.cudnn.benchmark = True  # 加速计算


class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("图像美化系统 v1.0")
        self.image = None   # 原始图像
        self.processed_image = None  # 当前处理后的图像
        self.original_image = None  # 备份原始图像
        self.history = []
        self.esrgan_model = None  # 延迟加载模型
        self.current_panel = None
        self.image_status = tk.StringVar()
        self.image_status.set("🟡 初始化...")
        # 创建界面布局
        self.create_widgets()

    # 系统界面
    def create_widgets(self):
        # 主窗口配置
        self.root.configure(bg="#FFF0F5")  # 粉白色背景
        root.geometry("1200x800")  # 可以设置更大初始窗口

        # ===== 顶部工具栏 =====
        toolbar = tk.Frame(self.root, bg="#FFD1DC", height=40)
        toolbar.pack(fill="x", padx=5, pady=5)

        # 工具栏按钮
        ttk.Button(toolbar, text="🖼️ 打开", command=self.open_image).pack(
            side="left", padx=5)
        ttk.Button(toolbar, text="💾 保存", command=self.save_image).pack(
            side="left", padx=5)
        ttk.Button(toolbar, text="🔄 重置", command=self.reset_image).pack(
            side="left", padx=5)
        ttk.Button(toolbar, text="↪️ 撤销", command=self.undo).pack(
            side="left", padx=5)

        # ===== 左侧整体布局 =====
        left_container = tk.Frame(self.root, bg="#FFF0F5")
        left_container.pack(side="left", fill="y", padx=5, pady=5)

        # 创建可滚动画布
        canvas = tk.Canvas(left_container, bg="#FFF0F5",
                           width=240, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Pink.TFrame")

        # 配置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 网格布局
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        left_container.grid_rowconfigure(0, weight=1)
        left_container.grid_columnconfigure(0, weight=1)

        # 参数面板（右）
        self.param_panel = tk.Frame(left_container, width=100, bg="#FFF0F5")
        self.param_panel.grid(row=0, column=2, sticky="nsew", padx=5)

        # 右侧主区域 (70%宽度)
        main_container = tk.Frame(self.root, bg="#F0F0F0")
        main_container.pack(side="right", expand=True, fill="both")

        # 图像显示区
        img_frame = tk.Frame(main_container, bg="#FFFFFF",
                             bd=2, relief="groove")
        img_frame.pack(expand=True, fill="both", padx=0, pady=0)

        self.canvas = tk.Canvas(img_frame, bg="#FFFFFF", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        # ===== 状态栏 =====
        status_bar = tk.Frame(main_container, bg="#FFD1DC", height=22)
        status_bar.pack(fill="x", side="bottom", pady=(5, 0))

        # 图像状态显示
        status_label = ttk.Label(
            status_bar,
            textvariable=self.image_status,  # 关键绑定
            font=('Arial', 9),
            background="#FFD1DC"
        )
        status_label.pack(side="left")

        # 操作提示
        self.operation_hint = tk.StringVar()
        ttk.Label(
            status_bar,
            textvariable=self.operation_hint,
            background="#FFD1DC",
            font=('Arial', 9),
            width=40,
            anchor="e"
        ).pack(side="right", padx=5)

        # 默认显示空白面板
        self.current_panel = None
        self.show_default_panel()

        # 样式配置
        style = ttk.Style()
        style.configure("Pink.TButton", foreground="#FF69B4",
                        font=('Arial', 10))
        style.configure("Pink.TFrame", background="#FFF0F5")

        # 功能模块卡片
        def create_card(title, commands, parent_frame):
            """创建功能卡片"""
            card = ttk.Frame(parent_frame, style="Pink.TFrame",
                             relief="solid", borderwidth=1)
            ttk.Label(card, text=title, font=('Arial', 11, "bold"),
                      background="#FFD1DC").pack(fill="x", pady=2)
            for btn_text, btn_cmd in commands:
                ttk.Button(card, text=btn_text, width=20,
                           command=btn_cmd).pack(pady=2, padx=5)
            return card

        # ===== 所有功能卡片 =====
        # 噪声处理卡片
        noise_card = create_card("🔊 噪声处理", [
            ("添加噪声", self.show_noise_panel),
            ("图像去噪", self.show_denoise_panel)
        ], scrollable_frame)
        noise_card.pack(fill="x", pady=5)

        # 色彩调整卡片
        color_card = create_card("🎨 色彩调整", [
            ("彩色↔灰度", self.toggle_grayscale),
            ("二值化", self.show_binary_panel),
            ("色相调整", self.show_hue_panel),
            ("反色", self.invert_colors)
        ], scrollable_frame)
        color_card.pack(fill="x", pady=5)

        # 几何变换卡片
        geom_card = create_card("🔄 几何变换", [
            ("旋转/翻转", self.show_rotate_panel),
            ("缩放/裁剪", self.show_scale_panel)
        ], scrollable_frame)
        geom_card.pack(fill="x", pady=5)

        # 图片增强卡片
        enhance_card = create_card("✨ 图片增强", [
            ("直方图均衡化", self.hist_equalization),
            ("部分参数调节", self.show_parameter_panel)
        ], scrollable_frame)
        enhance_card.pack(fill="x", pady=5)

        # 图片美化卡片
        beauty_card = create_card("🌟 图片美化", [
            ("加框", self.show_frame_panel),
            ("简单拼图", self.show_simple_stitch_panel),
            ("虚化", self.show_blur_panel),
            ("浮雕", self.show_emboss_panel),
            ("怀旧滤镜", self.show_vintage_panel),
        ], scrollable_frame)
        beauty_card.pack(fill="x", pady=5)

        # 特殊功能卡片
        special_card = create_card("🚀 特殊功能", [
            ("超分辨率", self.show_super_resolution_panel)
        ], scrollable_frame)
        special_card.pack(fill="x", pady=5)

        # 彩色增强卡片
        color_enhance_card = create_card("🌈 彩色增强", [
            ("伪彩色增强", lambda: self.show_color_enhance_panel("pseudo")),
            ("假彩色增强", lambda: self.show_color_enhance_panel("false"))
        ], scrollable_frame)
        color_enhance_card.pack(fill="x", pady=5)

        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # 图像拼接卡片
        special_card = create_card("🖼️ 智能拼图", [
            ("智能拼接", self.show_stitch_panel)  # 高级拼接功能
        ], scrollable_frame)
        special_card.pack(fill="x", pady=5)

    # 0.一些预处理
    def save_to_history(self):
        """将当前图像保存到历史记录"""
        if len(self.history) >= 10:  # 限制历史记录长度
            self.history.pop(0)
        if self.processed_image:
            self.history.append(self.processed_image.copy())
        elif self.image:  # 如果没有处理过，保存原始图像
            self.history.append(self.image.copy())

    def undo(self):
        """撤销上一步操作"""
        if self.history:  # 确保历史记录非空
            if len(self.history) == 1:  # 只剩最后一步时恢复原始图像
                self.processed_image = None
                self.show_image(self.history.pop())
                self.update_status()
            else:
                self.processed_image = self.history.pop()
                self.show_image(self.processed_image)
            self.reset_sliders()  # 调用滑块重置
            self.operation_hint.set(f"撤销成功 (剩余 {len(self.history)} 步)")
            self.update_status()

        else:
            messagebox.showinfo("提示", "没有可撤销的操作")

    def update_status(self):
        """线程安全的增强版状态更新"""
        try:
            # 获取当前图像对象（线程安全方式）
            current_img = None
            if hasattr(self, 'processed_image') and self.processed_image:
                current_img = self.processed_image
            elif hasattr(self, 'image') and self.image:
                current_img = self.image

            # 生成状态文本
            status_text = "🟡 就绪 | 未加载图像"
            if current_img:
                mode = current_img.mode
                w, h = current_img.size
                status_text = f"🟢 {mode} | {w}×{h}"

            # 双重更新保障
            self.image_status.set(status_text)
            self.root.after(10, lambda: self.image_status.set(status_text))

        except Exception as e:
            print(f"状态更新异常: {e}")
            self.root.after(100, self.update_status)  # 自动重试

    def update_undo_button(self):
        """当无历史记录时，禁用撤销按钮"""
        if hasattr(self, 'undo_button'):
            state = "normal" if self.history else "disabled"
            self.undo_button.config(state=state)

    def reset_image(self):
        """完全重置图像"""
        self.processed_image = None
        self.history = []  # 清空历史记录
        if self.image:
            self.show_image(self.image)
        if hasattr(self, 'brightness'):
            self.brightness.set(0)
        if hasattr(self, 'contrast'):
            self.contrast.set(0)
        if hasattr(self, 'saturation'):
            self.saturation.set(0)
        if hasattr(self, 'highlights'):
            self.highlights.set(0)
        if hasattr(self, 'shadows'):
            self.shadows.set(0)
        if hasattr(self, 'binary_threshold'):
            self.binary_threshold.set(128)
        if hasattr(self, 'blur_radius'):
            self.blur_radius.set(5)
        if hasattr(self, 'emboss_strength'):
            self.emboss_strength.set(2)
        if hasattr(self, 'vintage_strength'):
            self.vintage_strength.set(100)
        if self.image:
            self.show_image(self.image)
            self.update_status()

    def reset_sliders(self):
        """统一重置滑块位置"""
        for slider_var in ['brightness', 'contrast', 'saturation', 'highlights', 'shadows', 'binary_threshold']:
            if hasattr(self, slider_var):
                getattr(self, slider_var).set(
                    0 if slider_var != 'binary_threshold' else 128)

    def show_default_panel(self):
        """优化默认面板"""
        if hasattr(self, 'current_panel') and self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        ttk.Label(
            self.current_panel,
            text="🛠️请从左侧选择功能",
            font=('Arial', 10),
            background="#FFF0F5"
        ).pack(pady=20)

        tips = [
            "✨ 提示：",
            "- 先打开图像文件",
            "- 选择处理功能",
            "- 调整参数实时预览"
        ]
        for tip in tips:
            ttk.Label(
                self.current_panel,
                text=tip,
                font=('Arial', 9),
                background="#FFF0F5"
            ).pack(anchor="w", padx=10)

        self.current_panel.pack(fill="both", expand=True)

    # 1.读取、显示、存储
    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.bmp;*.jpg;*.png")])
        if path:
            self.image = Image.open(path)
            self.show_image(self.image)
            self.update_status()

    def save_image(self):
        if self.processed_image:
            path = filedialog.asksaveasfilename(defaultextension=".png")
            self.processed_image.save(path)

    def show_image(self, img):
        self.canvas.delete("all")
        width, height = img.size
        max_size = 800
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            img = img.resize(
                (int(width*ratio), int(height*ratio)), Resampling.LANCZOS)

        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    # 2.预处理功能
    # (1)加噪/去噪
    def show_noise_panel(self):
        """显示噪声添加面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 噪声类型选择
        ttk.Label(self.current_panel, text="噪声类型:").pack(pady=5)
        self.noise_type = tk.StringVar(value="均匀噪声")
        noise_menu = ttk.OptionMenu(
            self.current_panel, self.noise_type, "均匀噪声",
            "均匀噪声", "高斯噪声", "椒盐噪声"
        )
        noise_menu.pack(fill="x", padx=5, pady=2)

        # 噪声强度滑块
        ttk.Label(self.current_panel, text="噪声强度:").pack()
        self.noise_level = tk.IntVar(value=30)
        tk.Scale(
            self.current_panel, variable=self.noise_level,
            from_=1, to=100, orient="horizontal"
        ).pack(fill="x", padx=5)

        # 应用按钮
        ttk.Button(
            self.current_panel,
            text="添加噪声",
            command=self.add_noise
        ).pack(pady=10)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备添加噪声...")

    def add_noise(self):
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            img_array = np.array(src_img)
            noise_type = self.noise_type.get()
            level = self.noise_level.get()

            if noise_type == "高斯噪声":
                sigma = level ** 0.5
                noise = np.random.normal(
                    0, sigma, img_array.shape).astype(np.uint8)

            elif noise_type == "椒盐噪声":
                noisy = np.copy(img_array)
                num_pixels = int(np.ceil(level * 0.01 * img_array.size))

                # 统一处理单通道和多通道
                if len(img_array.shape) == 2:  # 灰度图
                    # 椒噪声（白点）
                    coords = [np.random.randint(0, img_array.shape[0], num_pixels//2),
                              np.random.randint(0, img_array.shape[1], num_pixels//2)]
                    noisy[coords[0], coords[1]] = 255

                    # 盐噪声（黑点）
                    coords = [np.random.randint(0, img_array.shape[0], num_pixels//2),
                              np.random.randint(0, img_array.shape[1], num_pixels//2)]
                    noisy[coords[0], coords[1]] = 0
                else:  # 彩色图
                    # 椒噪声
                    coords = [np.random.randint(0, img_array.shape[0], num_pixels//2),
                              np.random.randint(0, img_array.shape[1], num_pixels//2)]
                    noisy[coords[0], coords[1], :] = 255

                    # 盐噪声
                    coords = [np.random.randint(0, img_array.shape[0], num_pixels//2),
                              np.random.randint(0, img_array.shape[1], num_pixels//2)]
                    noisy[coords[0], coords[1], :] = 0

                self.processed_image = Image.fromarray(noisy)
                self.show_image(self.processed_image)
                return

            else:  # 均匀噪声
                # 修正形状匹配问题
                if len(img_array.shape) == 3:  # RGB图像
                    noise = np.random.randint(
                        0, level, img_array.shape, dtype=np.uint8)
                else:  # 灰度图像
                    noise = np.random.randint(
                        0, level, img_array.shape, dtype=np.uint8)
                    noise = np.expand_dims(
                        noise, axis=-1) if len(img_array.shape) == 2 else noise

            noisy_img = cv2.add(img_array, noise)

            self.processed_image = Image.fromarray(noisy_img)  # 更新结果
            self.show_image(self.processed_image)

    def show_denoise_panel(self):
        """显示去噪面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 去噪方法选择
        ttk.Label(self.current_panel, text="去噪方法:").pack(pady=5)
        self.denoise_method = tk.StringVar(value="中值滤波(空域)")
        denoise_menu = ttk.OptionMenu(
            self.current_panel, self.denoise_method, "中值滤波(空域)",
            "中值滤波(空域)", "非局部均值", "小波变换(频域)", "傅里叶滤波(频域)"
        )
        denoise_menu.pack(fill="x", padx=5, pady=2)

        # 傅里叶参数
        ttk.Label(self.current_panel, text="傅里叶半径:").pack()
        self.fourier_size = tk.IntVar(value=30)
        tk.Scale(
            self.current_panel, variable=self.fourier_size,
            from_=10, to=100, orient="horizontal"
        ).pack(fill="x", padx=5)

        # 应用按钮
        ttk.Button(
            self.current_panel,
            text="执行去噪",
            command=self.denoise_image
        ).pack(pady=10)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备去噪处理...")

    def denoise_image(self):
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        method = self.denoise_method.get()
        if method == "中值滤波(空域)":
            self.denoise_spatial()
        elif method == "非局部均值":
            self.denoise_nlmeans()
        elif method == "小波变换(频域)":
            self.denoise_wavelet()
        elif method == "傅里叶滤波(频域)":
            self.denoise_frequency()

    def denoise_spatial(self):
        """中值滤波（空域）"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            img_array = cv2.cvtColor(np.array(src_img), cv2.COLOR_RGB2BGR)
            denoised = cv2.medianBlur(img_array, 5)
            self.processed_image = Image.fromarray(
                cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
            self.show_image(self.processed_image)

    def _update_fourier_radius(self, event=None):
        """安全更新半径（兼容滑块事件参数）"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if hasattr(self, 'image') and src_img and \
                self.denoise_method.get() == "傅里叶滤波(频域)":
            try:
                self.denoise_frequency()
            except Exception as e:
                print(f"实时更新失败: {e}")

    def denoise_frequency(self):
        """傅里叶去噪"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        try:
            img_array = np.array(src_img)
            rows, cols = img_array.shape[:2]

            # 获取滑块值并确保有效（关键修正）
            mask_size = int(getattr(self, 'fourier_size', 30).get())
            mask_size = max(10, min(mask_size, min(rows, cols)//2))  # 动态上限

            if len(img_array.shape) == 3:  # 彩色图像
                img_yuv = cv2.cvtColor(img_array, cv2.COLOR_RGB2YUV)
                y, u, v = cv2.split(img_yuv)

                dft = cv2.dft(np.float32(y), flags=cv2.DFT_COMPLEX_OUTPUT)
                dft_shift = np.fft.fftshift(dft)

                mask = np.zeros((rows, cols, 2), np.uint8)
                cv2.circle(mask, (cols//2, rows//2), mask_size, (1, 1), -1)

                fshift = dft_shift * mask
                y_denoised = cv2.magnitude(
                    cv2.idft(np.fft.ifftshift(fshift))[:, :, 0],
                    cv2.idft(np.fft.ifftshift(fshift))[:, :, 1]
                )
                y_denoised = cv2.normalize(
                    y_denoised, None, 0, 255, cv2.NORM_MINMAX)

                merged = cv2.merge((np.uint8(y_denoised), u, v))
                self.processed_image = Image.fromarray(
                    cv2.cvtColor(merged, cv2.COLOR_YUV2RGB))

            else:  # 灰度图像
                dft = cv2.dft(np.float32(img_array),
                              flags=cv2.DFT_COMPLEX_OUTPUT)
                dft_shift = np.fft.fftshift(dft)

                mask = np.zeros((rows, cols, 2), np.uint8)
                cv2.circle(mask, (cols//2, rows//2), mask_size, (1, 1), -1)

                fshift = dft_shift * mask
                img_back = cv2.idft(np.fft.ifftshift(fshift))
                denoised = cv2.normalize(
                    cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1]),
                    None, 0, 255, cv2.NORM_MINMAX
                )
                self.processed_image = Image.fromarray(np.uint8(denoised))

            self.show_image(self.processed_image)

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("错误", f"傅里叶去噪失败: {str(e)}")

    def denoise_nlmeans(self):
        """非局部均值去噪"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            img_array = cv2.cvtColor(
                np.array(src_img), cv2.COLOR_RGB2BGR)
            denoised = cv2.fastNlMeansDenoisingColored(
                img_array, None, 10, 10, 7, 21)
            self.processed_image = Image.fromarray(
                cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
            self.show_image(self.processed_image)

    def denoise_wavelet(self):
        """小波去噪"""
        self.save_to_history()
        try:
            import pywt
            src_img = self.processed_image if self.processed_image else self.image
            img_array = np.array(src_img)  # 不再强制转灰度

            if len(img_array.shape) == 3:  # 彩色图像
                # 分通道处理
                channels = []
                for i in range(3):  # R,G,B通道
                    channel = img_array[:, :, i].astype(float)
                    coeffs = pywt.wavedec2(channel, 'sym8', level=2)
                    sigma = np.median(np.abs(coeffs[-1][0])) / 0.6745
                    threshold = sigma * np.sqrt(2 * np.log(channel.size))
                    coeffs_thresh = [coeffs[0]] + [
                        tuple(pywt.threshold(sub, threshold, 'soft')
                              for sub in c)
                        for c in coeffs[1:]
                    ]
                    denoised = pywt.waverec2(coeffs_thresh, 'sym8')
                    channels.append(np.clip(denoised, 0, 255).astype(np.uint8))

                result = np.stack(channels, axis=2)
            else:  # 灰度图像
                img_array = img_array.astype(float)
                coeffs = pywt.wavedec2(img_array, 'haar', level=2)
                sigma = np.median(np.abs(coeffs[-1][0])) / 0.6745
                threshold = sigma * np.sqrt(2 * np.log(img_array.size))
                coeffs_thresh = [coeffs[0]] + [
                    tuple(pywt.threshold(sub, threshold, 'soft') for sub in c)
                    for c in coeffs[1:]
                ]
                result = pywt.waverec2(coeffs_thresh, 'haar')
                result = np.clip(result, 0, 255).astype(np.uint8)

            self.processed_image = Image.fromarray(result)
            self.show_image(self.processed_image)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("错误", f"小波去噪失败: {str(e)}")

    # (2)色彩转换
    def show_color_convert_panel(self):
        """显示色彩转换面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 色彩转换按钮
        ttk.Button(
            self.current_panel,
            text="转化",
            command=self.toggle_grayscale
        ).pack(pady=5)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备色彩转换...")

    def toggle_grayscale(self):
        """增强版彩色↔灰度互转"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        # 首次转换时保存原始图像
        if not hasattr(self, '_original_color_image'):
            self._original_color_image = src_img.copy()

        if src_img.mode == "L":
            # 灰度转彩色（提供三种方案）
            choice = messagebox.askquestion(
                "灰度转彩色",
                "选择转换方式:\n是: 恢复原色\n否: 使用暖色调\n取消: 使用冷色调",
                type='yesnocancel'
            )

            if choice == 'yes':  # 恢复原始颜色
                if hasattr(self, '_original_color_image'):
                    self.processed_image = self._original_color_image.copy()
                else:
                    messagebox.showwarning("警告", "找不到原始彩色图像")
                    return
            else:
                # 创建伪彩色效果
                gray = np.array(src_img)
                if choice == 'no':  # 暖色调
                    colored = np.stack([gray, gray*0.6, gray*0.3], axis=-1)
                else:  # 冷色调
                    colored = np.stack([gray*0.3, gray*0.6, gray], axis=-1)
                self.processed_image = Image.fromarray(np.uint8(colored))
        else:
            # 彩色转灰度（保留原始图像）
            self._original_color_image = src_img.copy()
            self.processed_image = src_img.convert("L")

        self.show_image(self.processed_image)
        self.update_status()
        self.operation_hint.set("正在进行彩色↔灰度互转...")

    def show_binary_panel(self):
        """显示二值化面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 二值化阈值滑块
        ttk.Label(self.current_panel, text="二值化阈值:").pack()
        self.binary_threshold = tk.IntVar(value=128)
        threshold_slider = tk.Scale(
            self.current_panel, variable=self.binary_threshold,
            from_=0, to=255, orient="horizontal",
            command=self.gray_to_binary  # 绑定滑块事件
        )
        threshold_slider.pack(fill="x", padx=5)

        # 二值化按钮组
        btn_frame = ttk.Frame(self.current_panel)
        ttk.Button(
            btn_frame,
            text="应用二值化",
            command=lambda: self.gray_to_binary(None)
        ).pack(side="left", expand=True)
        ttk.Button(
            btn_frame,
            text="自动(Otsu)",
            command=self.auto_binary
        ).pack(side="left", expand=True)
        btn_frame.pack(fill="x", pady=5)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("正在进行二值化...")

    def gray_to_binary(self, event=None):
        """二值化（带实时预览）"""
        self.save_to_history()
        src_img = self.image.copy()
        if not src_img:
            return

        # 统一处理源图像（优先使用processed_image）
        src_img = self.processed_image if self.processed_image else self.image
        if src_img.mode != "L":
            messagebox.showerror("错误", "请先转换为灰度图像")
            return

        # 获取阈值（兼容滑块和手动调用）
        threshold = self.binary_threshold.get() if hasattr(
            self, 'binary_threshold') else 128

        # OpenCV二值化（效果更锐利）
        img_array = np.array(src_img)
        _, binary_arr = cv2.threshold(
            img_array, threshold, 255,
            cv2.THRESH_BINARY
        )

        # 显示结果（但不覆盖原始图像）
        temp_image = Image.fromarray(binary_arr)
        self.show_image(temp_image)

        # 仅当点击按钮时才保存结果
        if event is None:  # 非滑块触发的调用
            self.processed_image = temp_image
            self.update_status()

    def auto_binary(self):
        """自动Otsu阈值二值化"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        src_img = self.processed_image if self.processed_image else self.image
        if src_img.mode != "L":
            messagebox.showerror("错误", "请先转换为灰度图像")
            return

        img_array = np.array(src_img)
        thresh, binary_arr = cv2.threshold(
            img_array, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # 更新结果和滑块
        self.processed_image = Image.fromarray(binary_arr)
        if hasattr(self, 'binary_threshold'):
            self.binary_threshold.set(thresh)
        self.show_image(self.processed_image)
        self.update_status()

    def show_hue_panel(self):
        """色相调整面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")
        ttk.Label(self.current_panel, text="色相旋转:").pack()
        self.hue_shift = tk.IntVar(value=0)
        tk.Scale(
            self.current_panel, variable=self.hue_shift,
            from_=-180, to=180, orient="horizontal",
            command=lambda _: self.adjust_hue()
        ).pack(fill="x", padx=5)
        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备色相调整...")

    def adjust_hue(self):
        """调整色相（HSV空间）"""
        self.save_to_history()
        src_img = self.image.copy()
        if not src_img:
            return

        try:
            img_array = np.array(src_img)
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            hsv[:, :, 0] = (hsv[:, :, 0] + self.hue_shift.get()) % 180  # 色相循环
            adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            self.processed_image = Image.fromarray(adjusted)
            self.show_image(self.processed_image)
        except Exception as e:
            messagebox.showerror("错误", f"色相调整失败: {str(e)}")

    def invert_colors(self):
        """反色（一键操作）"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            self.processed_image = ImageOps.invert(src_img.convert('RGB'))
            self.show_image(self.processed_image)
        self.operation_hint.set("正在进行反色操作...")

    # (3)图像裁剪
    def start_crop(self):
        """进入裁剪模式"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            self.crop_start = None
            self.canvas.config(cursor="cross")  # 更改鼠标指针
            self.canvas.bind("<Button-1>", self._set_crop_start)
            self.canvas.bind("<B1-Motion>", self._draw_crop_rect)
            self.canvas.bind("<ButtonRelease-1>", self._execute_crop)
            self.canvas.bind("<Escape>", self._cancel_crop)
            self.canvas.focus_set()  # 确保接收键盘事件

    def _set_crop_start(self, event):
        """记录起始坐标"""
        self.crop_start = (event.x, event.y)

    def _draw_crop_rect(self, event):
        """实时绘制裁剪框和遮罩"""
        if self.crop_start:
            self.canvas.delete("crop_rect")
            x1, y1 = self.crop_start
            x2, y2 = event.x, event.y

            # 绘制四边遮罩
            mask_kwargs = {"fill": "gray50",
                           "stipple": "gray25", "tag": "crop_rect"}
            self.canvas.create_rectangle(
                0, 0, self.canvas.winfo_width(), y1, **mask_kwargs)
            self.canvas.create_rectangle(0, y1, x1, y2, **mask_kwargs)
            self.canvas.create_rectangle(
                x2, y1, self.canvas.winfo_width(), y2, **mask_kwargs)
            self.canvas.create_rectangle(
                0, y2, self.canvas.winfo_width(), self.canvas.winfo_height(), **mask_kwargs)

            # 绘制边框
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="red", width=2, tag="crop_rect")

    def _execute_crop(self, event):
        """执行裁剪"""
        if self.crop_start:
            x1, y1 = self.crop_start
            x2, y2 = event.x, event.y

            # 计算缩放比例（基于实际显示尺寸）
            scale = min(
                self.tk_image.width() / self.image.width,
                self.tk_image.height() / self.image.height
            )

            # 坐标转换与边界约束
            crop_box = (
                max(0, round(min(x1, x2) / scale)),
                max(0, round(min(y1, y2) / scale)),
                min(self.image.width, round(max(x1, x2) / scale)),
                min(self.image.height, round(max(y1, y2) / scale))
            )

            # 执行裁剪
            if crop_box[2] > crop_box[0] and crop_box[3] > crop_box[1]:  # 有效区域检查
                cropped = self.image.crop(crop_box)
                self.processed_image = cropped
                self.show_image(cropped)

            self._cancel_crop()  # 清理状态
            self.update_status()

    def _cancel_crop(self, event=None):
        """取消裁剪模式"""
        self.canvas.delete("crop_rect")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.unbind("<Escape>")
        self.canvas.config(cursor="")

    # 3.几何变换（旋转、对称变换、缩放）
    def show_rotate_panel(self):
        """显示旋转/翻转面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 旋转按钮组
        rotate_frame = ttk.Frame(self.current_panel)
        ttk.Button(
            rotate_frame,
            text="↻ 90°",
            command=lambda: self.rotate_image(90)
        ).pack(side="left", expand=True)
        ttk.Button(
            rotate_frame,
            text="↺ 90°",
            command=lambda: self.rotate_image(-90)
        ).pack(side="left", expand=True)
        rotate_frame.pack(fill="x", pady=5)

        # 翻转按钮组
        flip_frame = ttk.Frame(self.current_panel)
        ttk.Button(
            flip_frame,
            text="水平翻转",
            command=lambda: self.flip_image('horizontal')
        ).pack(side="left", expand=True)
        ttk.Button(
            flip_frame,
            text="垂直翻转",
            command=lambda: self.flip_image('vertical')
        ).pack(side="left", expand=True)
        flip_frame.pack(fill="x", pady=5)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备旋转/翻转图像...")

    def rotate_image(self, degrees=45):
        """可调角度的旋转"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            rotated = src_img.rotate(
                degrees, expand=True, resample=Resampling.BICUBIC)
            self.processed_image = rotated
            self.show_image(rotated)

    def show_scale_panel(self):
        """显示缩放/裁剪面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 缩放控制
        ttk.Label(self.current_panel, text="比例缩放:").pack(pady=5)
        scale_frame = ttk.Frame(self.current_panel)
        ttk.Button(
            scale_frame,
            text="放大1.5x",
            command=lambda: self.resize_image(1.5)
        ).pack(side="left", expand=True)
        ttk.Button(
            scale_frame,
            text="缩小0.5x",
            command=lambda: self.resize_image(0.5)
        ).pack(side="left", expand=True)
        scale_frame.pack(fill="x", pady=2)

        # 精确缩放
        ttk.Label(self.current_panel, text="精确尺寸:").pack(pady=5)
        resize_frame = ttk.Frame(self.current_panel)
        ttk.Label(resize_frame, text="宽度:").grid(row=0, column=0)
        self.target_width = tk.IntVar()
        ttk.Entry(resize_frame, textvariable=self.target_width,
                  width=5).grid(row=0, column=1)

        ttk.Label(resize_frame, text="高度:").grid(row=0, column=2)
        self.target_height = tk.IntVar()
        ttk.Entry(resize_frame, textvariable=self.target_height,
                  width=5).grid(row=0, column=3)

        ttk.Button(
            resize_frame,
            text="缩放",
            command=self._execute_pixel_resize
        ).grid(row=0, column=4, padx=5)

        self.lock_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            resize_frame,
            text="锁定比例",
            variable=self.lock_aspect
        ).grid(row=1, column=0, columnspan=5)
        resize_frame.pack(fill="x", pady=2)

        # 裁剪按钮
        ttk.Button(
            self.current_panel,
            text="裁剪图像",
            command=self.start_crop
        ).pack(pady=10)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("拖动选择区域 | ESC取消")

    def flip_image(self, mode='horizontal'):
        """对称翻转（水平/垂直）"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            if mode == 'horizontal':
                flipped = src_img.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                flipped = src_img.transpose(Image.FLIP_TOP_BOTTOM)
            self.processed_image = flipped
            self.show_image(flipped)

    def resize_image(self, scale=0.5):
        """根据缩放比例自动选择插值方法"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if src_img:
            width, height = src_img.size
            new_size = (int(width * scale), int(height * scale))
            # 根据缩放方向选择插值
            interpolation = Resampling.LANCZOS if scale < 1 else Image.BILINEAR
            resized = src_img.resize(new_size, interpolation)
            self.processed_image = resized
            self.show_image(resized)
        self.update_status()

    def resize_to_pixel(self, target_width=None, target_height=None):
        """按比例锁定模式缩放图像"""
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        try:
            width, height = src_img.size
            if target_width and not target_height:  # 仅输入宽度
                scale = target_width / width
                new_height = int(height * scale)
                new_size = (target_width, new_height)
            elif target_height and not target_width:  # 仅输入高度
                scale = target_height / height
                new_width = int(width * scale)
                new_size = (new_width, target_height)
            else:  # 同时输入宽高（但比例锁定，以较小比例为准）
                scale_w = target_width / width
                scale_h = target_height / height
                scale = min(scale_w, scale_h)  # 取较小比例避免拉伸
                new_size = (int(width * scale), int(height * scale))
                self.update_status()

            self.processed_image = src_img.resize(new_size, Resampling.LANCZOS)
            self.show_image(self.processed_image)
            self.update_status()
        except Exception as e:
            messagebox.showerror("错误", f"比例缩放失败: {str(e)}")

    def _execute_pixel_resize(self):
        """执行像素级缩放（带输入验证）"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        try:
            # 获取输入值并验证
            width = self.target_width.get() if hasattr(
                self, 'target_width') and self.target_width.get() > 0 else None
            height = self.target_height.get() if hasattr(
                self, 'target_height') and self.target_height.get() > 0 else None

            if not width and not height:
                messagebox.showwarning("提示", "请输入宽度或高度")
                return

            if self.lock_aspect.get():  # 比例锁定模式
                self.resize_to_pixel(width, height)
            else:  # 自由缩放
                if width and height:
                    self.processed_image = src_img.resize(
                        (width, height), Resampling.LANCZOS)
                    self.show_image(self.processed_image)
                    self.update_status()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"缩放失败: {str(e)}")

    # 4.图像增强
    def hist_equalization(self):
        """直方图均衡化（支持彩色和灰度图）"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image

        try:
            img_array = np.array(src_img)
            if len(img_array.shape) == 3:  # 彩色图像
                img_yuv = cv2.cvtColor(img_array, cv2.COLOR_RGB2YUV)
                img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
                result = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2RGB)
            else:  # 灰度图像
                result = cv2.equalizeHist(img_array)

            # 关键修复点：存储处理结果
            self.processed_image = Image.fromarray(result)
            self.show_image(self.processed_image)
            self.update_status()  # 更新状态

        except Exception as e:
            messagebox.showerror("错误", f"直方图均衡化失败: {str(e)}")

    def show_parameter_panel(self):
        """部分参数调整面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")
        # 亮度滑块
        ttk.Label(self.current_panel, text="亮度:").pack()
        self.brightness = tk.IntVar(value=0)
        tk.Scale(
            self.current_panel, variable=self.brightness,
            from_=-100, to=100, orient="horizontal",
            command=lambda _: self.adjust_brightness_contrast()
        ).pack(fill="x", padx=5)

        # 对比度滑块
        ttk.Label(self.current_panel, text="对比度:").pack()
        self.contrast = tk.IntVar(value=0)
        tk.Scale(
            self.current_panel, variable=self.contrast,
            from_=-100, to=100, orient="horizontal",
            command=lambda _: self.adjust_brightness_contrast()
        ).pack(fill="x", padx=5)

        # 饱和度滑块
        ttk.Label(self.current_panel, text="饱和度:").pack()
        self.saturation = tk.IntVar(value=0)
        tk.Scale(
            self.current_panel, variable=self.saturation,
            from_=-100, to=100, orient="horizontal",
            command=lambda _: self.adjust_saturation()
        ).pack(fill="x", padx=5)

        # 高光滑块
        ttk.Label(self.current_panel, text="高光:").pack()
        self.highlights = tk.IntVar(value=0)
        tk.Scale(
            self.current_panel, variable=self.highlights,
            from_=-100, to=100, orient="horizontal",
            command=lambda _: self.adjust_highlights_shadows()
        ).pack(fill="x", padx=5)

        # 阴影滑块
        ttk.Label(self.current_panel, text="阴影:").pack()
        self.shadows = tk.IntVar(value=0)
        tk.Scale(
            self.current_panel, variable=self.shadows,
            from_=-100, to=100, orient="horizontal",
            command=lambda _: self.adjust_highlights_shadows()
        ).pack(fill="x", padx=5)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("正在调节图片参数...")

    def adjust_brightness_contrast(self, event=None):
        """亮度/对比度"""
        self.save_to_history()
        src_img = self.image.copy()  # 关键：始终基于原始图像
        if src_img:
            alpha = 1 + self.contrast.get() / 100
            beta = self.brightness.get()
            img_array = np.array(src_img, dtype=np.float32)
            adjusted = np.clip(alpha * img_array + beta, 0, 255)
            self.processed_image = Image.fromarray(adjusted.astype(np.uint8))
            self.show_image(self.processed_image)

    def adjust_saturation(self):
        """调整饱和度（HSV空间）"""
        self.save_to_history()
        src_img = self.image.copy()
        if not src_img:
            return

        try:
            img_array = np.array(src_img)
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV).astype(np.float32)
            scale = 1 + self.saturation.get() / 100  # 饱和度缩放因子
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * scale, 0, 255)
            adjusted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            self.processed_image = Image.fromarray(adjusted)
            self.show_image(self.processed_image)
        except Exception as e:
            messagebox.showerror("错误", f"饱和度调整失败: {str(e)}")

    def adjust_highlights_shadows(self):
        """高光/阴影优化（非线性调整）"""
        self.save_to_history()
        src_img = self.image.copy()
        if not src_img:
            return

        try:
            img_array = np.array(src_img)
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)

            # 非线性调整（避免极端值）
            highlight_boost = self.highlights.get() * 0.5  # 高光强度减半
            shadow_boost = self.shadows.get() * 0.5       # 阴影强度减半

            # 高光调整（渐进式）
            highlight_mask = l > 128
            l[highlight_mask] = np.clip(
                l[highlight_mask] + (l[highlight_mask] -
                                     128) * (highlight_boost / 100),
                0, 255
            )

            # 阴影调整（渐进式）
            shadow_mask = l <= 128
            l[shadow_mask] = np.clip(
                l[shadow_mask] - (128 - l[shadow_mask]) * (shadow_boost / 100),
                0, 255
            )

            adjusted_lab = cv2.merge((l, a, b))
            adjusted_rgb = cv2.cvtColor(adjusted_lab, cv2.COLOR_LAB2RGB)
            self.processed_image = Image.fromarray(adjusted_rgb)
            self.show_image(self.processed_image)
        except Exception as e:
            messagebox.showerror("错误", f"调整失败: {str(e)}")

    # 5.美化功能
    # (1)加框
    def show_frame_panel(self):
        """边框功能面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 样式选择
        ttk.Label(self.current_panel, text="边框样式:",
                  font=('Arial', 10)).pack(pady=5)
        self.frame_style = tk.StringVar(value="gold")

        styles = [
            ("金色边框", "gold", "#FFD700"),
            ("立体边框", "3d", "#C0C0C0"),
            ("渐变边框", "gradient", "#000000"),
            ("相框效果", "wood", "#8B4513")
        ]

        for name, style, color in styles:
            f = tk.Frame(self.current_panel, bg="#FFF0F5")
            tk.Label(f, bg=color, width=3, height=1, bd=1,
                     relief="solid").pack(side="left")
            ttk.Radiobutton(f, text=name, value=style,
                            variable=self.frame_style).pack(side="left")
            f.pack(anchor="w", pady=2)

        # 边框宽度控制
        ttk.Label(self.current_panel, text="边框宽度 (10-100px):").pack(pady=10)
        self.frame_width = tk.IntVar(value=30)
        tk.Scale(
            self.current_panel, variable=self.frame_width,
            from_=10, to=100, orient="horizontal"
        ).pack(fill="x", padx=5)

        # 应用按钮
        ttk.Button(
            self.current_panel, text="应用边框",
            command=self.apply_frame_style,
            style="Pink.TButton"
        ).pack(pady=10, ipadx=10, ipady=5)

        self.current_panel.pack(fill="both", expand=True)

    def apply_frame_style(self):
        """边框应用"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        try:
            width = self.frame_width.get()
            img = src_img.convert("RGB")

            if self.frame_style.get() == "gold":
                framed = ImageOps.expand(img, border=width, fill=(255, 215, 0))

            elif self.frame_style.get() == "3d":
                # 立体边框
                framed = ImageOps.expand(
                    img, border=width, fill=(220, 220, 220))
                draw = ImageDraw.Draw(framed)
                # 左上角高光
                draw.rectangle([(0, 0), (framed.width-1, width-1)],
                               outline=(255, 255, 255))
                draw.rectangle(
                    [(0, 0), (width-1, framed.height-1)], outline=(255, 255, 255))
                # 右下角阴影
                draw.rectangle([(0, framed.height-width), (framed.width-1, framed.height-1)],
                               outline=(150, 150, 150))
                draw.rectangle([(framed.width-width, 0), (framed.width-1, framed.height-1)],
                               outline=(150, 150, 150))

            elif self.frame_style.get() == "gradient":
                # 渐变边框
                framed = Image.new('RGB',
                                   (img.width+2*width, img.height+2*width),
                                   (0, 0, 0))
                draw = ImageDraw.Draw(framed)
                for i in range(width):
                    alpha = int(255*(i/width))
                    draw.rectangle(
                        [(i, i), (framed.width-i-1, framed.height-i-1)],
                        outline=(alpha, alpha, alpha),
                        width=1
                    )
                framed.paste(img, (width, width))

            else:  # wood
                # 木质相框
                framed = Image.new('RGB',
                                   (img.width+2*width, img.height+2*width),
                                   (139, 69, 19))
                draw = ImageDraw.Draw(framed)
                # 木纹纹理
                for i in range(0, framed.width, 3):
                    draw.line([(i, 0), (i, framed.height)], fill=(160, 82, 45))
                for i in range(0, framed.height, 3):
                    draw.line([(0, i), (framed.width, i)], fill=(160, 82, 45))
                framed.paste(img, (width, width))

            self.processed_image = framed
            self.show_image(framed)
            self.update_status()
        except Exception as e:
            messagebox.showerror("错误", f"加框失败: {str(e)}")

    # (2)简单拼图
    def show_simple_stitch_panel(self):
        """新版简单拼图面板（支持复杂布局）"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 1. 布局选择
        ttk.Label(self.current_panel, text="拼图布局:").pack(pady=5)
        self.layout_type = tk.StringVar(value="horizontal")
        layouts = [
            ("水平拼接", "horizontal"),
            ("垂直拼接", "vertical"),
            ("上2下1", "top2_bottom1"),
            ("左1右2", "left1_right2")
        ]
        for name, layout in layouts:
            ttk.Radiobutton(
                self.current_panel, text=name, value=layout,
                variable=self.layout_type
            ).pack(anchor="w")

        # 2. 边框设置
        ttk.Label(self.current_panel, text="内边距:").pack(pady=(10, 0))
        self.padding_size = tk.IntVar(value=10)
        tk.Scale(
            self.current_panel, variable=self.padding_size,
            from_=0, to=50, orient="horizontal"
        ).pack(fill="x", padx=5)

        ttk.Label(self.current_panel, text="边框颜色:").pack()
        self.border_color = tk.StringVar(value="white")
        colors = [("白色", "white"), ("浅灰", "#F0F0F0"), ("黑色", "black")]
        for name, color in colors:
            ttk.Radiobutton(
                self.current_panel, text=name, value=color,
                variable=self.border_color
            ).pack(anchor="w")

        # 3. 执行按钮
        ttk.Button(
            self.current_panel,
            text="选择图片（按住Ctrl多选）\n并生成拼图",
            command=self._execute_simple_stitch,
            style="Pink.TButton"
        ).pack(pady=15)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("正在进行简单拼图...")

    def _execute_simple_stitch(self):
        """执行复杂布局拼图"""
        paths = filedialog.askopenfilenames(
            filetypes=[("Image Files", "*.bmp;*.jpg;*.png")]
        )
        if not paths:
            return

        try:
            images = [Image.open(path) for path in paths]
            layout = self.layout_type.get()
            padding = self.padding_size.get()
            bg_color = self.border_color.get()

            # 根据布局生成拼图
            if layout == "top2_bottom1" and len(images) >= 3:
                result = self._create_top2_bottom1_layout(
                    images, padding, bg_color)
            elif layout == "left1_right2" and len(images) >= 3:
                result = self._create_left1_right2_layout(
                    images, padding, bg_color)
            else:  # 默认水平/垂直
                result = self._create_basic_layout(
                    images, layout, padding, bg_color)

            self.processed_image = result
            self.show_image(result)
            self.update_status()
        except Exception as e:
            messagebox.showerror("错误", f"拼图失败: {str(e)}")

    def _create_top2_bottom1_layout(self, images, padding, bg_color):
        """上2下1布局"""
        # 1. 调整上方两张图大小（等宽）
        w = min(images[0].width, images[1].width)
        top_images = [img.resize((w, int(img.height * w / img.width)))
                      for img in images[:2]]

        # 2. 创建上方组合
        top_row = Image.new("RGB",
                            (top_images[0].width + top_images[1].width + padding,
                             max(img.height for img in top_images)),
                            bg_color
                            )
        top_row.paste(top_images[0], (0, 0))
        top_row.paste(top_images[1], (top_images[0].width + padding, 0))

        # 3. 调整下方图片宽度匹配上方
        bottom_img = images[2].resize(
            (top_row.width, int(images[2].height *
             top_row.width / images[2].width))
        )

        # 4. 组合最终图片
        result = Image.new("RGB",
                           (top_row.width, top_row.height +
                            bottom_img.height + padding),
                           bg_color
                           )
        result.paste(top_row, (0, 0))
        result.paste(bottom_img, (0, top_row.height + padding))

        return result
        self.update_status()

    def _create_left1_right2_layout(self, images, padding, bg_color):
        """左1右2布局"""
        # 1. 调整右侧两张图高度（等高）
        h = min(images[1].height, images[2].height)
        right_images = [
            img.resize((int(img.width * h / img.height), h))
            for img in images[1:]
        ]

        # 2. 创建右侧组合
        right_col = Image.new("RGB",
                              (max(img.width for img in right_images),
                               right_images[0].height + right_images[1].height + padding),
                              bg_color
                              )
        right_col.paste(right_images[0], (0, 0))
        right_col.paste(right_images[1], (0, right_images[0].height + padding))

        # 3. 调整左侧图片高度匹配右侧
        left_img = images[0].resize(
            (int(images[0].width * right_col.height / images[0].height),
             right_col.height
             ))

        # 4. 组合最终图片
        result = Image.new("RGB",
                           (left_img.width + right_col.width +
                            padding, right_col.height),
                           bg_color
                           )
        result.paste(left_img, (0, 0))
        result.paste(right_col, (left_img.width + padding, 0))

        return result

    def _create_basic_layout(self, images, layout, padding, bg_color):
        """基础水平/垂直布局"""
        if layout == "horizontal":
            total_width = sum(img.width for img in images) + \
                padding*(len(images)-1)
            max_height = max(img.height for img in images)
            result = Image.new("RGB", (total_width, max_height), bg_color)
            x_offset = 0
            for img in images:
                result.paste(img, (x_offset, 0))
                x_offset += img.width + padding
        else:  # vertical
            total_height = sum(img.height for img in images) + \
                padding*(len(images)-1)
            max_width = max(img.width for img in images)
            result = Image.new("RGB", (max_width, total_height), bg_color)
            y_offset = 0
            for img in images:
                result.paste(img, (0, y_offset))
                y_offset += img.height + padding
        return result
        self.update_status()

    # (3)虚化
    def show_blur_panel(self):
        """虚化参数面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")
        ttk.Label(self.current_panel, text="模糊半径:").pack()
        self.blur_radius = tk.IntVar(value=5)
        tk.Scale(
            self.current_panel, variable=self.blur_radius,
            from_=20, to=1, orient="horizontal",  # 反向范围：20（弱）→1（强）
            command=lambda _: self.apply_blur()
        ).pack(fill="x", padx=5)
        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备虚化处理...")

    def apply_blur(self, event=None):
        """根据滑块值虚化"""
        self.save_to_history()
        # 始终使用原始图像作为处理基准
        src_img = self.image.copy()  # 关键修改点

        if src_img:
            radius = 21 - self.blur_radius.get()
            blurred = src_img.filter(ImageFilter.GaussianBlur(radius=radius))
            self.processed_image = blurred
            self.show_image(blurred)
    # (4)浮雕

    def show_emboss_panel(self):
        """浮雕参数面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")
        # 浮雕深度（范围扩大为1-20，效果更明显）
        ttk.Label(self.current_panel, text="浮雕深度:").pack()
        self.emboss_strength = tk.IntVar(value=5)  # 默认值改为5
        tk.Scale(
            self.current_panel, variable=self.emboss_strength,
            from_=1, to=20, orient="horizontal",  # 范围改为1-20
            command=lambda _: self.apply_emboss()
        ).pack(fill="x", padx=5)
        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备浮雕处理...")

    def apply_emboss(self, event=None):
        """改进版浮雕效果"""
        self.save_to_history()
        src_img = self.image.copy()

        if src_img:
            strength = self.emboss_strength.get()
            # 更强烈的浮雕效果
            kernel = np.array([
                [-strength, -strength, 0],
                [-strength,  1,        strength],
                [0,         strength,  strength]
            ])
            embossed = src_img.filter(ImageFilter.Kernel(
                size=(3, 3),
                kernel=kernel.flatten().tolist(),
                scale=max(1, strength),  # 动态缩放
                offset=128
            ))
            self.processed_image = embossed
            self.show_image(embossed)
    # (5)滤镜

    def show_vintage_panel(self):
        """怀旧滤镜参数面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")
        ttk.Label(self.current_panel, text="滤镜强度:").pack()
        self.vintage_strength = tk.IntVar(value=0)  # 默认0%（原图）
        tk.Scale(
            self.current_panel, variable=self.vintage_strength,
            from_=0, to=100, orient="horizontal",  # 0%→100% 线性增强
            command=lambda _: self.apply_vintage()
        ).pack(fill="x", padx=5)
        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备添加怀旧滤镜...")

    def apply_vintage(self, event=None):
        """可调节的怀旧滤镜"""
        self.save_to_history()
        src_img = self.image.copy()
        if src_img:
            strength = self.vintage_strength.get() / 100.0
            img_array = np.array(src_img, dtype=np.float32)
            # 混合原始图像和棕褐色调
            vintage = np.dot(img_array, [[0.393, 0.769, 0.189],
                                         [0.349, 0.686, 0.168],
                                         [0.272, 0.534, 0.131]])
            blended = (1 - strength) * img_array + strength * vintage
            blended = np.clip(blended, 0, 255).astype(np.uint8)
            self.processed_image = Image.fromarray(blended)
            self.show_image(self.processed_image)

    # 6.图像特殊功能
    def load_esrgan_model(self):
        if not self.esrgan_model:
            model_path = "RRDB_ESRGAN_x4.pth"
            if not os.path.exists(model_path):
                messagebox.showerror("错误", "模型文件未找到！")
                return False

            try:
                # 加载模型文件
                state_dict = torch.load(model_path, map_location='cpu')

                # 创建模型实例
                model = RRDBNet(num_in_ch=3, num_out_ch=3,
                                num_feat=64, num_block=23, num_grow_ch=32)

                # 完整的键名映射表
                key_mapping = {
                    # 主干网络部分
                    'trunk_conv.weight': 'conv_body.weight',
                    'trunk_conv.bias': 'conv_body.bias',

                    # 上采样部分
                    'upconv1.weight': 'conv_up1.weight',
                    'upconv1.bias': 'conv_up1.bias',
                    'upconv2.weight': 'conv_up2.weight',
                    'upconv2.bias': 'conv_up2.bias',

                    # 最后输出层
                    'HRconv.weight': 'conv_hr.weight',
                    'HRconv.bias': 'conv_hr.bias',

                    # RRDB块的特殊处理（自动转换）
                    **{f'RRDB_trunk.{i}.RDB{j}.conv{k}.weight': f'body.{i}.rdb{j}.conv{k}.weight'
                       for i in range(23) for j in range(1, 4) for k in range(1, 6)},
                    **{f'RRDB_trunk.{i}.RDB{j}.conv{k}.bias': f'body.{i}.rdb{j}.conv{k}.bias'
                       for i in range(23) for j in range(1, 4) for k in range(1, 6)}
                }

                # 执行键名转换
                new_state_dict = {}
                for old_key, value in state_dict.items():
                    new_key = key_mapping.get(old_key, old_key)
                    new_state_dict[new_key] = value

                # 加载参数（严格模式）
                model.load_state_dict(new_state_dict, strict=True)
                model.eval()
                self.esrgan_model = model
                return True

            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("详细错误",
                                     f"最终加载失败: {str(e)}\n"
                                     "这是模型版本不兼容的终极解决方案\n"
                                     "建议改用OpenCV超分辨率方案")
                return False
        return True

    def show_super_resolution_panel(self):
        """显示超分辨率功能面板"""
        if self.current_panel:
            self.current_panel.destroy()

        # 创建新面板
        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 添加4倍超分辨率按钮
        ttk.Button(
            self.current_panel,
            text="4倍超分辨率",
            command=self.apply_super_resolution
        ).pack(pady=10)

        # 添加说明标签
        ttk.Label(
            self.current_panel,
            text="需下载64MB模型文件",
            foreground="gray"
        ).pack()

        # 添加状态标签（用于显示处理进度）
        self.sr_status = tk.StringVar()
        self.sr_status.set("准备就绪")
        ttk.Label(
            self.current_panel,
            textvariable=self.sr_status,
            foreground="blue"
        ).pack(pady=5)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("选择超分辨率功能...")

    def apply_super_resolution(self):
        """执行超分辨率处理"""
        self.save_to_history()
        print("="*50)
        print("调试信息：")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"模型文件存在: {os.path.exists('RRDB_ESRGAN_x4.pth')}")
        print("="*50)
        if not self.load_esrgan_model():  # 检查模型是否加载成功
            return

        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            messagebox.showwarning("警告", "请先加载图像！")
            return

        try:
            # 确保图像是RGB格式（3通道）
            if src_img.mode != 'RGB':
                src_img = src_img.convert('RGB')

            self.sr_status.set("处理中...")
            self.root.update()  # 强制更新界面显示

            # 添加尺寸限制（建议值）
            max_pixels = 1024 * 1024  # 1MP
            if src_img.width * src_img.height > max_pixels:
                # 等比例缩小
                ratio = (max_pixels / (src_img.width * src_img.height)) ** 0.5
                new_size = (int(src_img.width * ratio),
                            int(src_img.height * ratio))
                src_img = src_img.resize(new_size, Resampling.LANCZOS)
                messagebox.showwarning("尺寸调整",
                                       f"已自动优化处理尺寸\n\n"
                                       f"▪ 原始尺寸: {src_img.width}×{src_img.height}\n"
                                       f"▪ 新尺寸: {new_size[0]}×{new_size[1]}\n\n"
                                       "提示：大尺寸图像会消耗更多内存")

            # 转换图像为Tensor
            img_tensor = ToTensor()(src_img).unsqueeze(0)

            # 使用模型处理
            with torch.no_grad():
                output = self.esrgan_model(img_tensor)

            # 转换回PIL图像
            sr_img = ToPILImage()(output.squeeze().clamp(0, 1))

            self.processed_image = sr_img
            self.show_image(sr_img)
            self.sr_status.set("处理完成！")
            self.operation_hint.set("超分辨率完成（4倍放大）")

        except Exception as e:
            self.sr_status.set("处理失败")
            messagebox.showerror("错误", f"超分辨率失败: {str(e)}")

    # 7.假彩色增强、伪彩色增强
    def show_color_enhance_panel(self, mode="pseudo"):
        """显示彩色增强面板（修正版）"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        if mode == "pseudo":
            # 伪彩色选项
            ttk.Label(self.current_panel, text="伪彩色方案").pack(pady=5)
            self.pseudo_map = tk.StringVar(value="jet")

            colormaps = [
                ("热力图 (Jet)", "jet"),
                ("彩虹 (Rainbow)", "rainbow"),
                ("海洋 (Ocean)", "ocean"),
                ("春季 (Spring)", "spring"),
                ("夏季 (Summer)", "summer")
            ]

            for name, code in colormaps:
                ttk.Radiobutton(
                    self.current_panel, text=name, value=code,
                    variable=self.pseudo_map
                ).pack(anchor="w")

            ttk.Button(
                self.current_panel, text="应用伪彩色",
                command=self._apply_pseudo_color
            ).pack(pady=10)

        else:
            # 假彩色选项
            ttk.Label(self.current_panel, text="假彩色通道映射").pack(pady=5)
            self.false_mapping = tk.StringVar(value="2-1-0")

            mappings = [
                ("红外模拟 (RGB→BGR)", "2-1-0"),
                ("植被增强 (GBR→GRB)", "1-2-0"),
                ("热感增强 (RBG→GRB)", "0-2-1")
            ]

            for name, mapping in mappings:
                ttk.Radiobutton(
                    self.current_panel, text=name, value=mapping,
                    variable=self.false_mapping
                ).pack(anchor="w")

            ttk.Button(
                self.current_panel, text="应用假彩色",
                command=self._apply_false_color
            ).pack(pady=10)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("准备彩色增强处理...")

    def _apply_pseudo_color(self):
        """执行伪彩色增强"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        colormap = {
            "jet": cv2.COLORMAP_JET,
            "rainbow": cv2.COLORMAP_RAINBOW,
            "ocean": cv2.COLORMAP_OCEAN,
            "spring": cv2.COLORMAP_SPRING,
            "summer": cv2.COLORMAP_SUMMER
        }.get(self.pseudo_map.get(), cv2.COLORMAP_JET)

        try:
            # 统一处理灰度/RGB输入
            img_array = np.array(src_img.convert(
                "RGB")) if src_img.mode != "L" else np.array(src_img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(
                img_array.shape) == 3 else img_array
            colored = cv2.applyColorMap(gray, colormap)
            result = Image.fromarray(cv2.cvtColor(colored, cv2.COLOR_BGR2RGB))

            self.processed_image = result
            self.show_image(result)
            self.update_status()
        except Exception as e:
            messagebox.showerror("错误", f"伪彩色处理失败: {str(e)}")

    def _apply_false_color(self):
        """执行假彩色增强"""
        self.save_to_history()
        src_img = self.processed_image if self.processed_image else self.image
        if not src_img:
            return

        try:
            mapping = tuple(map(int, self.false_mapping.get().split('-')))
            arr = np.array(src_img.convert("RGB"))

            # 确保是3通道
            if len(arr.shape) == 2:
                arr = np.stack([arr]*3, axis=-1)

            # 通道重映射
            result = Image.fromarray(arr[:, :, mapping])
            self.processed_image = result
            self.show_image(result)
            self.update_status()
        except Exception as e:
            messagebox.showerror("错误", f"假彩色处理失败: {str(e)}")

    # 8.拼接处理
    def show_stitch_panel(self):
        """拼接功能主面板"""
        if self.current_panel:
            self.current_panel.destroy()

        self.current_panel = tk.Frame(self.param_panel, bg="#FFF0F5")

        # 图片选择按钮
        ttk.Button(
            self.current_panel,
            text="选择多张图片（按住Ctrl多选）",
            command=self._select_stitch_images
        ).pack(pady=10)

        # 拼接方法选择
        ttk.Label(self.current_panel, text="拼接方法:").pack()
        self.stitch_method = tk.StringVar(value="simple")
        ttk.Radiobutton(
            self.current_panel, text="简单拼接",
            variable=self.stitch_method, value="simple"
        ).pack(anchor="w")
        ttk.Radiobutton(
            self.current_panel, text="特征点匹配",
            variable=self.stitch_method, value="feature"
        ).pack(anchor="w")

        # 融合方法选择
        ttk.Label(self.current_panel, text="融合方法:").pack(pady=(10, 0))
        self.blend_method = tk.StringVar(value="alpha")
        blend_methods = [
            ("Alpha融合", "alpha"),
            ("金字塔融合", "pyramid")
        ]
        for text, value in blend_methods:
            ttk.Radiobutton(
                self.current_panel, text=text,
                variable=self.blend_method, value=value
            ).pack(anchor="w")

        # 智能调整选项
        ttk.Label(self.current_panel, text="预处理:").pack(pady=(10, 0))
        self.auto_adjust = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.current_panel, text="自动统一尺寸",
            variable=self.auto_adjust
        ).pack(anchor="w")

        # 状态提示标签
        self.status_label = ttk.Label(
            self.current_panel,
            text="等待选择图片...",
            foreground="blue",
            wraplength=300
        )
        self.status_label.pack(pady=5)

        # 执行按钮
        ttk.Button(
            self.current_panel,
            text="执行拼接",
            command=self._execute_stitch,
            style="Pink.TButton"
        ).pack(pady=15)

        self.current_panel.pack(fill="both", expand=True)
        self.operation_hint.set("请选择2张及以上图片...")

    def _select_stitch_images(self):
        """选择图片并显示信息"""
        paths = filedialog.askopenfilenames(
            filetypes=[("Image Files", "*.bmp;*.jpg;*.png")])
        if len(paths) < 2:
            messagebox.showwarning("提示", "请至少选择2张图片！")
            return

        self.stitch_images = [Image.open(path) for path in paths]
        sizes = [f"{img.width}x{img.height}" for img in self.stitch_images]
        self.status_label.config(
            text=f"已选择 {len(paths)} 张图片\n" +
            "尺寸: " + " | ".join(sizes))
        self.operation_hint.set("请设置拼接参数...")
        self.operation_hint.set("提示：选择相似场景图片可提高特征点融合拼接成功率")

    def _execute_stitch(self):
        """执行拼接的主逻辑"""
        if not hasattr(self, 'stitch_images') or len(self.stitch_images) < 2:
            messagebox.showwarning("错误", "请先选择图片！")
            return

        try:
            # 更新状态栏（使用安全方式）
            self.status_label.config(text="处理中...", foreground="blue")
            self.root.update()  # 强制刷新界面

            # 1. 自动调整尺寸
            if self.auto_adjust.get():
                self._auto_adjust_images()

            # 2. 执行拼接
            if self.stitch_method.get() == "simple":
                result = self._simple_stitch()
            else:
                result = self._feature_based_stitch()

            # 3. 应用融合效果
            if result is not None:
                blended = self._apply_blend(result)
                self.processed_image = blended
                self.image = blended  # 同时更新主图像
                self.show_image(blended)

            # 更新全局状态
            self.update_status()

        except Exception as e:
            self.status_label.config(text=f"错误: {str(e)}", foreground="red")
            # 这里不需要调用 update_status()，因为可能没有有效图像

    # ===== 核心功能实现 =====
    def _auto_adjust_images(self):
        """智能尺寸调整"""
        try:
            # 计算最小公共尺寸
            min_width = min(img.width for img in self.stitch_images)
            min_height = min(img.height for img in self.stitch_images)

            adjusted = []
            for img in self.stitch_images:
                ratio = min(min_width/img.width, min_height/img.height)
                new_size = (int(img.width*ratio), int(img.height*ratio))
                adjusted.append(img.resize(new_size, Image.Resampling.LANCZOS))

            self.stitch_images = adjusted
            self.status_label.config(
                text=f"已自动调整尺寸\n统一尺寸: {min_width}x{min_height}\n" +
                f"缩放比例: {ratio:.2f}")

            # 不需要调用 update_status()
        except Exception as e:
            self.status_label.config(
                text=f"尺寸调整失败: {str(e)}", foreground="orange")

    def _simple_stitch(self):
        """简单拼接（水平/垂直自动选择）"""
        images = [img.convert("RGB") for img in self.stitch_images]
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        # 自动选择拼接方向
        if total_width <= 3000:  # 水平拼接
            result = Image.new("RGB", (total_width, max_height))
            x = 0
            for img in images:
                result.paste(img, (x, 0))
                x += img.width
        else:  # 垂直拼接
            total_height = sum(img.height for img in images)
            max_width = max(img.width for img in images)
            result = Image.new("RGB", (max_width, total_height))
            y = 0
            for img in images:
                result.paste(img, (0, y))
                y += img.height
        return result

    def _feature_based_stitch(self):
        """SIFT特征拼接（自动估算画布大小）"""
        import cv2
        import numpy as np

        try:
            imgs = [np.array(img.convert("RGB"))[:, :, ::-1]
                    for img in self.stitch_images]

            base = imgs[0]
            for next_img in imgs[1:]:
                gray1 = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(next_img, cv2.COLOR_BGR2GRAY)

                sift = cv2.SIFT_create()
                kp1, des1 = sift.detectAndCompute(gray1, None)
                kp2, des2 = sift.detectAndCompute(gray2, None)

                bf = cv2.BFMatcher()
                matches = bf.knnMatch(des1, des2, k=2)

                good = [m for m, n in matches if m.distance < 0.75 * n.distance]
                if len(good) < 4:
                    raise ValueError("特征点不足")

                src_pts = np.float32(
                    [kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32(
                    [kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

                H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)

                # 计算新画布大小
                h1, w1 = base.shape[:2]
                h2, w2 = next_img.shape[:2]
                corners = np.float32(
                    [[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
                warped_corners = cv2.perspectiveTransform(corners, H)
                all_corners = np.concatenate((np.float32([[0, 0], [0, h1], [w1, h1], [
                                             w1, 0]]).reshape(-1, 1, 2), warped_corners), axis=0)
                [xmin, ymin] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
                [xmax, ymax] = np.int32(all_corners.max(axis=0).ravel() + 0.5)

                # 平移变换矩阵，确保所有图都在正坐标
                translation = np.array(
                    [[1, 0, -xmin], [0, 1, -ymin], [0, 0, 1]])

                result = cv2.warpPerspective(
                    next_img, translation @ H, (xmax - xmin, ymax - ymin))
                result[-ymin:h1 - ymin, -xmin:w1 - xmin] = base  # 把base贴上去

                base = result  # 更新base为新的图像

            return Image.fromarray(cv2.cvtColor(base, cv2.COLOR_BGR2RGB))

        except Exception as e:
            raise ValueError(f"拼接失败：{str(e)}")

    def _apply_blend(self, img):
        """应用选择的融合方法"""
        method = self.blend_method.get()
        try:
            if method == "alpha":
                return self._alpha_blend(img)
            else:
                return self._pyramid_blend(img)
            self.update_status()
        except Exception as e:
            messagebox.showwarning(f"{method}融合失败", f"已切换为Alpha融合\n{str(e)}")
            return self._alpha_blend(img)

    # ===== 融合方法实现 =====
    def _alpha_blend(self, img):
        """Alpha通道融合"""
        arr = np.array(img)
        if len(self.stitch_images) < 2:
            return img

        # 创建渐变蒙版
        mask = np.zeros(arr.shape[:2], dtype=np.float32)
        seam = self.stitch_images[0].width  # 假设第一张图的分界位置

        # 创建渐变过渡区
        blend_width = min(100, img.width//10)
        left = max(0, seam - blend_width//2)
        right = min(img.width, seam + blend_width//2)
        mask[:, left:right] = np.linspace(0, 1, right-left)

        # 应用混合
        blended = arr.copy()
        for c in range(3):
            blended[:, :, c] = arr[:, :, c] * (1 - mask) + arr[:, :, c] * mask
        return Image.fromarray(blended.astype(np.uint8))

    def _pyramid_blend(self, img):
        """金字塔融合"""
        try:
            import cv2
            arr = np.array(img)

            # 创建高斯金字塔
            G = arr.astype(np.float32)
            gp = [G]
            for _ in range(3):
                G = cv2.pyrDown(G)
                gp.append(G)

            # 创建拉普拉斯金字塔
            lp = [gp[-1]]
            for i in range(len(gp)-1, 0, -1):
                size = (gp[i-1].shape[1], gp[i-1].shape[0])
                GE = cv2.pyrUp(gp[i], dstsize=size)
                L = cv2.subtract(gp[i-1], GE)
                lp.append(L)

            # 重建图像
            ls = lp[0]
            for i in range(1, len(lp)):
                size = (lp[i].shape[1], lp[i].shape[0])
                ls = cv2.pyrUp(ls, dstsize=size)
                ls = cv2.add(ls, lp[i])

            # 归一化处理
            ls = np.clip(ls, 0, 255)
            return Image.fromarray(ls.astype(np.uint8))
        except Exception as e:
            raise ValueError(f"金字塔融合错误: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
