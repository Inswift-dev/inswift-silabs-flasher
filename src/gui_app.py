#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inswift Silabs Flasher GUI - Zigbee固件烧录工具
"""

import asyncio
import logging
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading

# 导入串口扫描模块
try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    _LOGGER.warning("pyserial未安装，无法自动扫描串口")

# 导入烧录相关的模块
from universal_silabs_flasher.flasher import Flasher
from universal_silabs_flasher.const import ApplicationType, DEFAULT_BAUDRATES
import zigpy.types

# 配置日志
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

class FlasherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Inswift Silabs Flasher - Zigbee固件烧录工具")
        self.root.geometry("800x600")
        
        # 变量
        self.firmware_path = tk.StringVar()
        self.device_port = tk.StringVar(value="")  # 初始为空，等待扫描后自动选择
        self.probe_method = tk.StringVar(value="ezsp")  # 默认使用ezsp
        self.ieee_address = tk.StringVar(value="")  # IEEE地址
        self.force_write_ieee = tk.BooleanVar(value=False)  # 强制写入IEEE地址
        
        self.is_running = False
        
        # 默认波特率配置
        self.default_baudrates = {
            "ezsp": "115200",
            "router": "115200",
            "bootloader": "115200",
            "cpc": "115200",
            "spinel": "460800",
        }
        
        self.create_widgets()
    
    def set_window_icon(self):
        """设置窗口图标（显示在标题栏和任务栏）"""
        try:
            # 尝试加载logo图片，从多个可能的位置查找
            # 处理PyInstaller打包后的资源路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的exe，使用sys._MEIPASS
                base_path = sys._MEIPASS
            else:
                # 如果是Python脚本，使用脚本所在目录
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            current_dir = os.getcwd()
            
            possible_paths = [
                os.path.join(base_path, "logo.ico"),  # 打包后的资源目录.ico（优先）
                os.path.join(base_path, "logo.png"),  # 打包后的资源目录.png
                os.path.join(current_dir, "logo.ico"),  # 工作目录.ico（exe同目录）
                os.path.join(current_dir, "logo.png"),  # 工作目录.png（exe同目录）
                "logo.ico",  # 当前目录.ico
                "logo.png",  # 当前目录.png
            ]
            
            logo_path = None
            for path in possible_paths:
                full_path = os.path.abspath(path)
                if os.path.exists(full_path):
                    logo_path = full_path
                    _LOGGER.debug(f"找到logo文件: {logo_path}")
                    break
            
            if logo_path:
                try:
                    # 确保使用绝对路径
                    abs_logo_path = os.path.abspath(logo_path)
                    
                    # 如果是.ico文件，使用iconbitmap（Windows标准方法）
                    if abs_logo_path.lower().endswith('.ico'):
                        try:
                            self.root.iconbitmap(abs_logo_path)
                            _LOGGER.debug(f"成功设置.ico图标: {abs_logo_path}")
                        except Exception as e:
                            _LOGGER.warning(f"使用iconbitmap设置.ico失败: {e}")
                            # 如果失败，尝试使用iconphoto
                            try:
                                from PIL import Image, ImageTk
                                logo_image = Image.open(abs_logo_path)
                                self.logo_photo = ImageTk.PhotoImage(logo_image)
                                self.root.iconphoto(True, self.logo_photo)
                                _LOGGER.debug(f"使用iconphoto成功设置.ico图标")
                            except Exception as e2:
                                _LOGGER.warning(f"使用iconphoto设置.ico也失败: {e2}")
                    else:
                        # PNG或其他格式，使用PIL加载
                        try:
                            from PIL import Image, ImageTk
                            logo_image = Image.open(abs_logo_path)
                            
                            # 在Windows上，尝试创建临时.ico文件以获得更好的兼容性
                            if sys.platform == 'win32':
                                try:
                                    import tempfile
                                    # 创建临时.ico文件
                                    temp_dir = tempfile.gettempdir()
                                    temp_ico = os.path.join(temp_dir, 'inswift_logo_temp.ico')
                                    
                                    # 确保图片是RGBA模式（支持透明度）
                                    if logo_image.mode != 'RGBA':
                                        logo_image = logo_image.convert('RGBA')
                                    
                                    # 保存为.ico格式
                                    # 调整到标准图标尺寸（48x48，Windows推荐）
                                    icon_48 = logo_image.resize((48, 48), Image.Resampling.LANCZOS)
                                    icon_48.save(temp_ico, format='ICO')
                                    
                                    # 使用临时.ico文件设置图标
                                    self.root.iconbitmap(temp_ico)
                                    _LOGGER.debug(f"成功创建临时ICO并设置图标: {temp_ico}")
                                except Exception as ico_error:
                                    _LOGGER.debug(f"创建临时ICO失败，尝试直接使用PNG: {ico_error}")
                                    # 如果创建ICO失败，直接使用PNG
                                    self.logo_photo = ImageTk.PhotoImage(logo_image)
                                    self.root.iconphoto(True, self.logo_photo)
                                    _LOGGER.debug(f"使用iconphoto设置PNG图标成功")
                            else:
                                # 非Windows系统，直接使用iconphoto
                                self.logo_photo = ImageTk.PhotoImage(logo_image)
                                self.root.iconphoto(True, self.logo_photo)
                                _LOGGER.debug(f"使用iconphoto设置PNG图标成功")
                        except ImportError:
                            _LOGGER.warning("PIL库未安装，无法加载PNG图片作为窗口图标")
                            _LOGGER.warning("请安装Pillow库: pip install Pillow")
                        except Exception as e:
                            _LOGGER.warning(f"设置PNG图标失败: {e}")
                            import traceback
                            _LOGGER.debug(f"详细错误: {traceback.format_exc()}")
                except Exception as e:
                    _LOGGER.warning(f"设置窗口图标失败: {e}")
            else:
                _LOGGER.debug("未找到logo文件，使用默认图标")
                # 列出查找过的路径，方便调试
                _LOGGER.debug(f"查找路径: {possible_paths}")
        except Exception as e:
            _LOGGER.warning(f"窗口图标加载过程出错: {e}")
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 设置窗口图标（显示在标题栏和任务栏）
        self.set_window_icon()
        
        # ========== 固件选择 ==========
        ttk.Label(main_frame, text="1. 选择固件文件 (.gbl):", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        
        firmware_frame = ttk.Frame(main_frame)
        firmware_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        firmware_frame.columnconfigure(1, weight=1)
        
        self.firmware_entry = ttk.Entry(firmware_frame, textvariable=self.firmware_path, state="readonly")
        self.firmware_entry.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(firmware_frame, text="浏览...", command=self.browse_firmware).grid(row=0, column=2)
        
        # ========== 设备配置 ==========
        ttk.Label(main_frame, text="2. 设备配置:", font=("", 10, "bold")).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )
        
        # COM端口
        ttk.Label(main_frame, text="串口:").grid(row=3, column=0, sticky=tk.W, pady=5)
        port_frame = ttk.Frame(main_frame)
        port_frame.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.device_port, width=18, state="readonly")
        self.port_combo.grid(row=0, column=0, padx=(0, 5))
        
        # 刷新串口按钮
        refresh_btn = ttk.Button(port_frame, text="刷新", command=self.scan_ports, width=8)
        refresh_btn.grid(row=0, column=1)
        
        # Probe Method选择
        ttk.Label(main_frame, text="探测方法:").grid(row=4, column=0, sticky=tk.W, pady=5)
        probe_frame = ttk.Frame(main_frame)
        probe_frame.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        probe_combo = ttk.Combobox(probe_frame, textvariable=self.probe_method, 
                                   state="readonly", width=20)
        probe_combo['values'] = ("ezsp", "router", "bootloader", "cpc", "spinel")
        probe_combo.grid(row=0, column=0)
        
        # 自动扫描串口
        self.scan_ports()
        
        # ========== 进度条 ==========
        ttk.Label(main_frame, text="3. 烧录进度:", font=("", 10, "bold")).grid(
            row=5, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )
        
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', variable=self.progress_var, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="等待开始...")
        self.progress_label.grid(row=0, column=1, sticky=tk.W)
        
        # ========== 日志输出 ==========
        ttk.Label(main_frame, text="4. 运行日志:", font=("", 10, "bold")).grid(
            row=7, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ========== 写入IEEE地址 ==========
        ttk.Label(main_frame, text="5. 写入IEEE地址:", font=("", 10, "bold")).grid(
            row=11, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )
        
        ieee_frame = ttk.Frame(main_frame)
        ieee_frame.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ieee_frame.columnconfigure(1, weight=1)
        
        ttk.Label(ieee_frame, text="IEEE地址:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        ieee_entry_frame = ttk.Frame(ieee_frame)
        ieee_entry_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.ieee_entry = ttk.Entry(ieee_entry_frame, textvariable=self.ieee_address, width=25)
        self.ieee_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # IEEE地址格式提示
        ttk.Label(ieee_frame, text="格式: 00:3c:84:ff:fe:92:bb:2c 或 003c84fffe92bb2c", 
                  font=("", 8), foreground="gray").grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
        
        # 强制写入选项
        force_frame = ttk.Frame(ieee_frame)
        force_frame.grid(row=0, column=2, sticky=tk.W)
        
        self.force_checkbox = ttk.Checkbutton(force_frame, text="强制写入", variable=self.force_write_ieee)
        self.force_checkbox.grid(row=0, column=0)
        
        # 写入IEEE按钮
        write_ieee_btn = ttk.Button(force_frame, text="写入IEEE地址", command=self.start_write_ieee, width=15)
        write_ieee_btn.grid(row=0, column=1, padx=(10, 0))
        
        # ========== 控制按钮 ==========
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始烧录", command=self.start_flashing, width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="清空日志", command=self.clear_log, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="退出", command=self.root.quit, width=20).pack(side=tk.LEFT, padx=10)
    
    def scan_ports(self):
        """扫描可用串口"""
        if not SERIAL_AVAILABLE:
            # 如果pyserial未安装，显示默认值或用户输入的值
            current_value = self.device_port.get()
            self.port_combo['values'] = (current_value,) if current_value else ()
            self.port_combo.config(state="normal")  # 允许手动输入
            return
        
        try:
            # 扫描所有可用串口
            ports = serial.tools.list_ports.comports()
            port_list = []
            
            for port in sorted(ports):
                # 获取端口设备名（Windows: COM1, COM3等；Linux/Mac: /dev/ttyUSB0等）
                port_name = port.device
                port_list.append(port_name)
            
            # 更新Combobox的选项
            if port_list:
                self.port_combo['values'] = port_list
                # 如果当前值不在列表中，自动选择第一个可用串口
                current_value = self.device_port.get()
                if current_value not in port_list:
                    self.device_port.set(port_list[0])
                    if len(port_list) > 1:
                        self.log(f"检测到 {len(port_list)} 个串口，已自动选择: {port_list[0]}")
                else:
                    # 保持当前选择
                    self.device_port.set(current_value)
                # 设置为只读模式，只能从列表中选择
                self.port_combo.config(state="readonly")
            else:
                # 没有找到串口
                self.port_combo['values'] = ()
                current_value = self.device_port.get()
                if not current_value:
                    self.device_port.set("")  # 清空
                self.log("未检测到可用串口，请检查设备连接")
                # 允许手动输入串口名
                self.port_combo.config(state="normal")
                
        except Exception as e:
            _LOGGER.error(f"扫描串口时出错: {e}")
            self.log(f"串口扫描失败: {e}")
            # 出错时允许手动输入
            current_value = self.device_port.get()
            if current_value:
                self.port_combo['values'] = (current_value,)
            self.port_combo.config(state="normal")
    
    def browse_firmware(self):
        """浏览固件文件"""
        filename = filedialog.askopenfilename(
            title="选择固件文件",
            filetypes=[("GBL文件", "*.gbl"), ("EBL文件", "*.ebl"), ("所有文件", "*.*")]
        )
        if filename:
            self.firmware_path.set(filename)
            self.log(f"选择固件: {filename}")
    
    def log(self, message):
        """添加日志消息（线程安全）"""
        def update():
            try:
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
                # 不调用self.root.update()，避免阻塞，使用update_idletasks更安全
                self.root.update_idletasks()
            except Exception as e:
                # 如果更新失败，记录但不中断程序
                _LOGGER.debug(f"Log update error: {e}")
        
        # 如果不在主线程，需要调度到主线程执行
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update)
        else:
            update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def validate_ieee_address(self, ieee_str: str) -> zigpy.types.EUI64 | None:
        """验证和转换IEEE地址字符串"""
        if not ieee_str:
            return None
        
        try:
            # 使用zigpy的EUI64.convert来验证和转换IEEE地址
            # 支持格式: "00:3c:84:ff:fe:92:bb:2c" 或 "003c84fffe92bb2c"
            ieee = zigpy.types.EUI64.convert(ieee_str.strip())
            return ieee
        except (ValueError, TypeError) as e:
            _LOGGER.error(f"无效的IEEE地址格式: {ieee_str}, 错误: {e}")
            return None
    
    def start_write_ieee(self):
        """开始写入IEEE地址"""
        if self.is_running:
            messagebox.showwarning("警告", "其他任务正在运行中，请等待完成")
            return
        
        # 验证设备端口
        if not self.device_port.get():
            messagebox.showerror("错误", "请选择设备端口")
            return
        
        # 验证IEEE地址
        ieee_str = self.ieee_address.get().strip()
        if not ieee_str:
            messagebox.showerror("错误", "请输入IEEE地址")
            return
        
        ieee = self.validate_ieee_address(ieee_str)
        if ieee is None:
            messagebox.showerror("错误", f"无效的IEEE地址格式: {ieee_str}\n请使用格式: 00:3c:84:ff:fe:92:bb:2c 或 003c84fffe92bb2c")
            return
        
        # 确认操作（因为写入IEEE地址可能是永久操作）
        force = self.force_write_ieee.get()
        confirm_msg = f"确定要写入IEEE地址吗？\n\n新地址: {ieee}\n强制写入: {'是' if force else '否'}\n\n注意: 某些固件版本下，写入IEEE地址是永久操作！"
        if not messagebox.askyesno("确认", confirm_msg):
            return
        
        # 启动写入线程
        self.is_running = True
        self.start_button.config(state="disabled")
        self.log(f"开始写入IEEE地址: {ieee}")
        self.update_progress(0, "准备写入IEEE地址...")
        
        threading.Thread(target=self.run_write_ieee, daemon=True, args=(ieee, force)).start()
    
    def run_write_ieee(self, ieee: zigpy.types.EUI64, force: bool):
        """在后台线程中运行写入IEEE地址"""
        try:
            asyncio.run(self.async_write_ieee(ieee, force))
        except Exception as e:
            self.log(f"写入IEEE地址失败: {str(e)}")
            import traceback
            self.log(f"错误详情:\n{traceback.format_exc()}")
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
    
    async def async_write_ieee(self, ieee: zigpy.types.EUI64, force: bool):
        """异步写入IEEE地址函数"""
        self.log(f"准备连接设备并写入IEEE地址...")
        
        # 创建Flasher实例
        device = self.device_port.get()
        
        # 写入IEEE地址功能使用EZSP模式，自动使用EZSP的默认波特率
        baudrates = DEFAULT_BAUDRATES.copy()
        default_baudrate = int(self.default_baudrates.get("ezsp", "115200"))
        baudrates[ApplicationType.EZSP] = [default_baudrate]
        self.log(f"使用默认波特率: {default_baudrate} (EZSP模式)")
        
        # 创建Flasher，允许探测EZSP和Bootloader（写入IEEE需要EZSP）
        flasher = Flasher(
            device=device,
            baudrates=baudrates,
            probe_methods=(ApplicationType.EZSP, ApplicationType.GECKO_BOOTLOADER),
            bootloader_reset=(),  # 不使用reset方法
        )
        
        self.log(f"连接设备: {device}")
        
        try:
            # 探测设备类型
            self.log("探测设备类型...")
            await flasher.probe_app_type(try_first=[ApplicationType.GECKO_BOOTLOADER, ApplicationType.EZSP])
            
            self.log(f"检测到设备类型: {flasher.app_type}")
            
            # 写入IEEE地址
            self.update_progress(50, "正在写入IEEE地址...")
            result = await flasher.write_emberznet_eui64(ieee, force=force)
            
            if result:
                self.update_progress(100, "IEEE地址写入成功！")
                self.log(f"✅ IEEE地址写入成功: {ieee}")
            else:
                self.update_progress(100, "IEEE地址已匹配，无需写入")
                self.log(f"ℹ️ 设备IEEE地址已与目标地址匹配，无需写入")
                
        except RuntimeError as e:
            error_msg = str(e)
            if "not running EmberZNet" in error_msg:
                self.log(f"❌ 错误: 设备未运行EmberZNet固件，无法写入IEEE地址")
                self.log(f"当前设备类型: {flasher.app_type}")
                self.log(f"提示: 写入IEEE地址需要设备运行EmberZNet (EZSP) 固件")
            else:
                self.log(f"❌ 错误: {error_msg}")
            self.update_progress(0, f"写入失败: {error_msg}")
            raise
        except Exception as e:
            self.log(f"❌ 写入IEEE地址时发生错误: {e}")
            self.update_progress(0, f"写入失败: {e}")
            raise
    
    def update_progress(self, percent, status=""):
        """更新进度条（线程安全）"""
        def update():
            try:
                # 确保进度值在0-100范围内
                percent_clamped = max(0, min(100, percent))
                self.progress_var.set(percent_clamped)
                if status:
                    self.progress_label.config(text=status)
                # 强制更新UI
                self.root.update_idletasks()
            except Exception as e:
                # 如果更新失败，记录但不中断程序
                _LOGGER.debug(f"Progress update error: {e}")
        
        # 如果不在主线程，需要调度到主线程执行
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update)
        else:
            update()
    
    def start_flashing(self):
        """开始烧录"""
        if self.is_running:
            messagebox.showwarning("警告", "烧录任务正在运行中，请等待完成")
            return
        
        # 验证固件文件
        if not self.firmware_path.get():
            messagebox.showerror("错误", "请选择固件文件")
            return
        
        if not os.path.exists(self.firmware_path.get()):
            messagebox.showerror("错误", "固件文件不存在")
            return
        
        # 验证设备端口
        if not self.device_port.get():
            messagebox.showerror("错误", "请输入设备端口")
            return
        
        # 启动烧录线程
        self.is_running = True
        self.start_button.config(state="disabled")
        self.clear_log()
        self.update_progress(0, "准备开始...")
        
        threading.Thread(target=self.run_flashing, daemon=True).start()
    
    def run_flashing(self):
        """在后台线程中运行烧录"""
        try:
            asyncio.run(self.async_flash())
        except Exception as e:
            self.log(f"烧录失败: {str(e)}")
            import traceback
            self.log(f"错误详情:\n{traceback.format_exc()}")
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
    
    async def async_flash(self):
        """异步烧录函数"""
        self.log("开始烧录流程...")
        # 进度条在烧录前保持0%，只显示在日志中
        self.update_progress(0, "准备中...")
        
        # 读取固件文件
        firmware_file = self.firmware_path.get()
        self.log(f"读取固件文件: {firmware_file}")
        
        try:
            with open(firmware_file, 'rb') as f:
                firmware_data = f.read()
        except Exception as e:
            self.log(f"读取固件文件失败: {e}")
            self.update_progress(0, "读取失败")
            return
        
        self.log(f"固件文件大小: {len(firmware_data)} 字节")
        
        # 解析固件
        from universal_silabs_flasher.firmware import parse_firmware_image
        try:
            fw_image = parse_firmware_image(firmware_data)
            self.log("固件解析成功")
        except Exception as e:
            self.log(f"固件解析失败: {e}")
            self.update_progress(0, "解析失败")
            return
        
        # 获取元数据
        metadata = None
        try:
            metadata = fw_image.get_nabucasa_metadata()
            if metadata:
                self.log(f"固件类型: {metadata.fw_type}")
                self.log(f"固件版本: {metadata.get_public_version()}")
                if metadata.baudrate:
                    self.log(f"波特率: {metadata.baudrate}")
        except Exception:
            self.log("无法读取固件元数据")
        
        # 创建Flasher实例
        device = self.device_port.get()
        probe_method_str = self.probe_method.get()
        
        # 转换probe_method字符串为ApplicationType
        probe_method_map = {
            "ezsp": ApplicationType.EZSP,
            "router": ApplicationType.ROUTER,
            "bootloader": ApplicationType.GECKO_BOOTLOADER,
            "cpc": ApplicationType.CPC,
            "spinel": ApplicationType.SPINEL,
        }
        probe_method_type = probe_method_map.get(probe_method_str, ApplicationType.EZSP)
        
        # 根据探测方法自动设置默认波特率
        baudrates = DEFAULT_BAUDRATES.copy()
        default_baudrate = int(self.default_baudrates.get(probe_method_str, "115200"))
        baudrates[probe_method_type] = [default_baudrate]
        self.log(f"使用默认波特率: {default_baudrate} (探测方法: {probe_method_str})")
        
        # 创建Flasher，只探测指定的类型
        flasher = Flasher(
            device=device,
            baudrates=baudrates,
            probe_methods=(probe_method_type,),
            bootloader_reset=(),  # 不使用reset方法
        )
        
        self.log(f"连接设备: {device}")
        self.log(f"探测方法: {probe_method_str}")
        self.log(f"波特率: {baudrates[probe_method_type]}")
        
        # 探测设备
        self.log("探测设备类型...")
        try:
            await flasher.probe_app_type(types=[probe_method_type])
        except RuntimeError as e:
            error_msg = str(e)
            self.log(f"设备探测失败: {error_msg}")
            
            # 如果探测失败，提供更友好的错误提示和解决方案
            self.log("")
            self.log("=" * 60)
            self.log("设备探测失败 - 故障排除指南")
            self.log("=" * 60)
            
            if probe_method_type == ApplicationType.GECKO_BOOTLOADER:
                # Bootloader模式探测失败 - 尝试硬件复位
                self.log("")
                self.log("检测到：引导模式探测失败")
                self.log("")
                self.log("正在尝试使用RTS/DTR硬件复位强制进入引导模式...")
                self.log("")
                
                try:
                    from universal_silabs_flasher.const import ResetTarget
                    # 尝试使用RTS/DTR硬件复位
                    await flasher.trigger_bootloader(ResetTarget.RTS_DTR)
                    await asyncio.sleep(1.0)  # 给设备时间进入引导模式
                    
                    # 再次尝试探测引导模式
                    self.log("硬件复位完成，重新探测引导模式...")
                    try:
                        await flasher.probe_gecko_bootloader(
                            run_firmware=False,
                            baudrate=baudrates[ApplicationType.GECKO_BOOTLOADER][0]
                        )
                        self.log("✓ 成功！通过硬件复位进入引导模式")
                        # 设置设备类型为引导模式
                        flasher.app_type = ApplicationType.GECKO_BOOTLOADER
                        flasher.app_baudrate = baudrates[ApplicationType.GECKO_BOOTLOADER][0]
                        flasher.bootloader_baudrate = baudrates[ApplicationType.GECKO_BOOTLOADER][0]
                        self.log("")
                        self.log("可以继续烧录固件了")
                        # 跳过后续的enter_bootloader调用，因为已经在引导模式了
                        flasher._skip_enter_bootloader = True
                    except Exception as probe_error:
                        self.log(f"⚠ 硬件复位后探测仍然失败: {probe_error}")
                        self.log("")
                        self.log("可能的解决方案：")
                        self.log("1. 检查设备硬件连接（USB线、端口）")
                        self.log("2. 尝试重新插拔USB设备")
                        self.log("3. 某些设备可能需要按住Boot按钮并重启")
                        self.log("4. 检查设备驱动程序是否正确安装")
                        self.log("5. 尝试使用其他串口工具验证设备是否响应")
                        self.update_progress(0, "硬件复位后探测失败")
                        return
                except Exception as reset_error:
                    self.log(f"✗ 硬件复位失败: {reset_error}")
                    self.log("")
                    self.log("硬件复位也需要稳定的串口连接")
                    self.log("请检查USB连接和驱动程序")
                    self.update_progress(0, "硬件复位失败")
                    return
            
            elif probe_method_type in (ApplicationType.CPC, ApplicationType.ROUTER):
                # CPC或Router模式探测失败 - 尝试硬件复位
                self.log("")
                self.log("检测到：固件通信问题")
                self.log("")
                self.log("正在尝试使用RTS/DTR硬件复位强制进入引导模式...")
                self.log("")
                
                try:
                    from universal_silabs_flasher.const import ResetTarget
                    # 尝试使用RTS/DTR硬件复位
                    await flasher.trigger_bootloader(ResetTarget.RTS_DTR)
                    await asyncio.sleep(1.0)  # 给设备时间进入引导模式
                    
                    # 再次尝试探测引导模式
                    self.log("硬件复位完成，重新探测引导模式...")
                    try:
                        await flasher.probe_gecko_bootloader(
                            run_firmware=False,
                            baudrate=baudrates[ApplicationType.GECKO_BOOTLOADER][0]
                        )
                        self.log("✓ 成功！通过硬件复位进入引导模式")
                        # 设置设备类型为引导模式
                        flasher.app_type = ApplicationType.GECKO_BOOTLOADER
                        flasher.app_baudrate = baudrates[ApplicationType.GECKO_BOOTLOADER][0]
                        flasher.bootloader_baudrate = baudrates[ApplicationType.GECKO_BOOTLOADER][0]
                        self.log("")
                        self.log("可以继续烧录固件了")
                        # 跳过后续的enter_bootloader调用，因为已经在引导模式了
                        flasher._skip_enter_bootloader = True
                    except Exception as probe_error:
                        self.log(f"⚠ 硬件复位后探测仍然失败: {probe_error}")
                        self.log("")
                        self.log("可能的解决方案：")
                        self.log("1. 检查设备硬件连接（USB线、端口）")
                        self.log("2. 尝试重新插拔USB设备")
                        self.log("3. 某些设备可能需要按住Boot按钮并重启")
                        self.log("4. 检查设备驱动程序是否正确安装")
                        self.log("5. 尝试使用其他串口工具验证设备是否响应")
                        self.update_progress(0, "硬件复位后探测失败")
                        return
                except Exception as reset_error:
                    self.log(f"✗ 硬件复位失败: {reset_error}")
                    self.log("")
                    self.log("硬件复位也需要稳定的串口连接")
                    self.log("请检查USB连接和驱动程序")
                    self.update_progress(0, "硬件复位失败")
                    return
            
            else:
                self.log("")
                self.log("建议尝试以下方法：")
                self.log("1. 检查设备连接和电源")
                self.log("2. 重新插拔USB设备")
                self.log("3. 尝试其他探测方法（如bootloader或cpc）")
                self.log("4. 检查串口驱动和权限")
            
            if probe_method_type not in (ApplicationType.GECKO_BOOTLOADER, ApplicationType.CPC, ApplicationType.ROUTER):
                self.update_progress(0, "设备探测失败")
                return
        
        self.log(f"检测到设备类型: {flasher.app_type}")
        
        # 检查是否已经通过硬件复位进入引导模式
        if hasattr(flasher, '_skip_enter_bootloader') and flasher._skip_enter_bootloader:
            # 已经在引导模式了（通过硬件复位进入的）
            self.log("设备已在引导模式（通过硬件复位）")
            delattr(flasher, '_skip_enter_bootloader')
        else:
            if flasher.app_version:
                self.log(f"当前固件版本: {flasher.app_version}")
            self.log(f"应用波特率: {flasher.app_baudrate}")
            
            # 进入引导模式
            self.log("进入引导模式...")
            try:
                await flasher.enter_bootloader()
                self.log("成功进入引导模式")
            except Exception as e:
                self.log(f"进入引导模式失败: {e}")
                self.update_progress(0, "进入引导模式失败")
                return
        
        # 烧录固件
        self.log("开始烧录固件...")
        # 进度条重置为0%，开始显示烧录进度
        self.update_progress(0, "准备烧录...")
        
        try:
            from universal_silabs_flasher.xmodemcrc import BLOCK_SIZE
            from universal_silabs_flasher.gecko_bootloader import NoFirmwareError
            
            last_update_percent = -1  # 初始值设为-1，确保第一次0%时会更新
            last_log_percent = -1
            
            def progress_callback(current, total):
                """进度回调函数（同步函数，会被xmodemcrc同步调用）"""
                nonlocal last_update_percent, last_log_percent
                if total == 0:
                    return
                
                # 计算固件数据传输的实际百分比 (0-100%)
                upload_percent = (current / total) * 100
                
                # 格式化已传输数据大小
                current_mb = current / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                
                # 计算当前整数百分比
                current_percent = int(upload_percent)
                
                # 每隔1%更新一次进度条
                # 例如：0%, 1%, 2%, 3%... 或者进度达到100%时也更新
                should_update = False
                if upload_percent >= 100:
                    # 到达100%时强制更新
                    should_update = True
                    last_update_percent = 100
                else:
                    # 计算当前进度属于哪个1%区间（向下取整到1%的倍数）
                    # 例如：0.3% -> 0%, 1.7% -> 1%, 12.5% -> 12%
                    display_percent = current_percent
                    if display_percent > last_update_percent:
                        # 进度跨越了新的1%阈值，需要更新
                        should_update = True
                        last_update_percent = display_percent
                
                # 在开始时记录一次总大小信息
                if current == 0 and total > 0:
                    total_mb_display = total / (1024 * 1024)
                    self.log(f"开始传输固件数据... 总大小: {total_mb_display:.2f}MB")
                
                # 每 1% 在日志中记录一次，显示烧录进度
                if current_percent > last_log_percent:
                    last_log_percent = current_percent
                    self.log(f"烧录进度: {current_percent}% ({current_mb:.2f}MB / {total_mb:.2f}MB)")
                
                # 每1%更新进度条和状态文本
                if should_update:
                    # 进度条使用精确的上传百分比（0-100%），这样进度条会平滑显示
                    # 状态文本显示当前实际进度和传输数据量
                    status_text = f"{current_percent}% ({current_mb:.2f}MB / {total_mb:.2f}MB)"
                    self.update_progress(upload_percent, status_text)
            
            await flasher.flash_firmware(
                fw_image,
                run_firmware=True,
                progress_callback=progress_callback
            )
            self.update_progress(100, "烧录完成！")
            self.log("固件烧录完成！")
            self.log("设备将自动启动新固件")
            
        except NoFirmwareError as e:
            # 固件烧录成功，但运行时出现问题
            self.update_progress(95, "固件已烧录，但启动时出现问题")
            self.log("⚠️ 警告：固件已成功烧录到设备")
            self.log("⚠️ 但设备未能自动启动固件")
            self.log("💡 建议：")
            self.log("   1. 断开并重新连接USB设备")
            self.log("   2. 手动重启设备（如需要）")
            self.log("   3. 固件应该会在下次启动时自动运行")
            self.log("")
            self.log(f"详细错误: {e}")
            
        except Exception as e:
            self.log(f"烧录失败: {e}")
            self.update_progress(0, f"烧录失败: {e}")
            import traceback
            self.log(f"错误详情:\n{traceback.format_exc()}")


def main():
    root = tk.Tk()
    app = FlasherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
