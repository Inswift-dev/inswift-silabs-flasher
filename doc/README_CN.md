## 项目简介

Inswift Silabs Flasher 是一款基于 Windows 的图形化固件烧录工具，用于给 Silicon Labs 平台的无线芯片/模组烧录多种协议固件（Zigbee NCP、Zigbee Router、OpenThread RCP、Multi-PAN CPC 等）。  
本工程在开源项目 `universal-silabs-flasher` 的基础上进行了本地化与功能增强，配套 Inswift 系列 USB Dongle 产品使用。

## 仓库目录结构

- **`doc/`**：工程软件环境搭建、工具使用教程以及后续会更新的操作指导文档  
  - 构建与环境搭建（中文）：[`doc/BUILD_CN.md`](doc/BUILD_CN.md)  
  - Build & environment (English)：[`doc/BUILD_EN.md`](doc/BUILD_EN.md)  
  - GUI 使用说明（中文）：[`doc/Inswift_Silabs_Flasher_GUI_CN.md`](doc/Inswift_Silabs_Flasher_GUI_CN.md)  
  - GUI User Guide (English)：[`doc/Inswift_Silabs_Flasher_GUI_EN.md`](doc/Inswift_Silabs_Flasher_GUI_EN.md)

- **`firmware_bin/`**：产品出厂/维护时用于烧录的固件存放目录，已按协议和芯片型号划分子目录，所有固件目前均为 `.gbl` 格式  
  - `zigbee-ncp/`：Zigbee NCP 固件（适配 EmberZNet NCP 模式）  
  - `zigbee-router/`：Zigbee Router 固件  
  - `thread-rcp/`：OpenThread RCP 固件  
  - `multipan/`：CPC Multi-PAN 固件  
  - 典型子目录示例：`ZBM-MG21/`、`ZBM-MG24/` 等，以具体产品/芯片平台区分；文件名中包含协议类型与版本号，例如：
    - `zigbee-ncp/ZBM-MG24/ncp_uart_hw_dongle_v8.2.1.0.gbl`
    - `thread-rcp/ZBM-MG21/ot-rcp_dongle_v2.6.1.0.gbl`
    - `multipan/ZBM-MG24/rcp-uart_dongle_v4.6.0.gbl`

- **`src/`**：烧录工具的源代码与构建脚本  
  - `gui_app.py`：GUI 程序入口（Tkinter 图形界面）  
  - `universal_silabs_flasher/`：核心烧录逻辑包，基于上游开源项目 `universal-silabs-flasher`，支持多种协议、自动探测和进度回调等  
  - `build_windows.bat`：Windows 一键打包脚本，使用 PyInstaller 生成单文件可执行程序  
  - `InswiftSilabsFlasher.spec`：PyInstaller 打包配置（含数据文件、隐藏依赖等）  
  - `requirements_gui.txt`：GUI 版本依赖列表（包含 `zigpy`、`bellows`、`pyserial-asyncio-fast`、`Pillow` 等）  
  - `pyproject.toml`：Python 包元信息与依赖配置，其中 `project.urls.repository` 指向上游仓库 `https://github.com/NabuCasa/universal-silabs-flasher`。

- **`tools/`**：编译/打包后生成的可执行工具目录  
  - 例如：`tools/InswiftSilabsFlasher.exe`（可直接分发给最终用户使用）。

## 快速开始（推荐阅读顺序）

### 1. 环境准备

- 操作系统：Windows 10 / Windows 11  
- Python：3.9 及以上版本  
- 网络：能访问 PyPI（或已配置国内镜像）

详细环境搭建与依赖安装说明请参考：[`doc/BUILD_CN.md`](doc/BUILD_CN.md)。  
核心要点概览：

1. 安装 Python 3.9+，安装时勾选 “Add Python to PATH”  
2. 在项目根目录（包含 `src/` 与 `requirements_gui.txt` 的目录）执行：

```bash
python -m pip install --upgrade pip
python -m pip install -r src/requirements_gui.txt
```

或按 `doc/BUILD_CN.md` 中给出的方式使用 `pyproject.toml` 进行安装。

### 2. Windows 打包生成可执行文件

如需自行打包生成 GUI 工具 exe，可在 `src/` 目录执行 `build_windows.bat`（推荐）：

```bash
cd src
build_windows.bat
```

脚本会自动完成：

- 升级 pip  
- 安装构建所需依赖（读取 `requirements_gui.txt`）  
- 安装 PyInstaller  
- 调用 PyInstaller 按 `InswiftSilabsFlasher.spec` 完成打包

打包完成后，生成的可执行文件位置：

- `dist\InswiftSilabsFlasher.exe`

也可以直接运行仓库中提供的二进制：

- `tools/InswiftSilabsFlasher.exe`

### 3. GUI 使用概览

典型使用流程：

1. 使用 USB 线将 Inswift Dongle（如 ZBM-MG21 / ZBM-MG24 等）连接到电脑  
2. 启动工具：双击 `InswiftSilabsFlasher.exe`（来自 `dist\` 或 `tools\` 目录）  
3. 在 GUI 中：
   - 选择固件文件（`firmware_bin/` 目录下对应协议和型号的 `.gbl` 文件）  
   - 选择串口号（自动扫描或手动输入，如 COM3）  
   - 选择探测方法（`ezsp` / `router` / `bootloader` / `cpc` / `spinel`）  
   - 点击 “开始烧录”，观察进度条与日志输出

详细的按钮说明、进度显示、写入 IEEE 地址等高级功能，请参考：

- 中文 GUI 使用说明：[`doc/Inswift_Silabs_Flasher_GUI_CN.md`](doc/Inswift_Silabs_Flasher_GUI_CN.md)  
- English GUI User Guide：[`doc/Inswift_Silabs_Flasher_GUI_EN.md`](doc/Inswift_Silabs_Flasher_GUI_EN.md)

## 固件目录与版本说明

`firmware_bin/` 目录中的固件已按协议和平台进行分类，便于快速定位：

- **按协议划分**：  
  - `zigbee-ncp/`：适用于 NCP 模式（一般用于网关/协调器场景）  
  - `zigbee-router/`：适用于路由器/子设备场景  
  - `thread-rcp/`：OpenThread RCP 固件  
  - `multipan/`：Multi-PAN CPC 固件，可同时支持多协议

- **按平台/产品划分**：  
  - 如 `ZBM-MG21/`、`ZBM-MG24/` 等目录，代表不同芯片平台或产品型号

- **文件命名约定（示例）**：  
  - `ncp_uart_hw_dongle_v8.2.1.0.gbl`：Zigbee NCP 固件，v8.2.1.0 版本  
  - `ot-rcp_dongle_v2.6.1.0.gbl`：OpenThread RCP 固件，v2.6.1.0 版本  
  - `light_devtype_dongle_v8.0.2.0.gbl`：Zigbee Router 固件（灯设备类型），v8.0.2.0 版本  
  - `rcp-uart_dongle_v4.6.0.gbl`：Multi-PAN CPC RCP 固件，v4.6.0 版本

在烧录前，请确保：

- 选择的固件协议类型与实际用途匹配（如网关使用 NCP，路由器使用 Router 固件等）  
- 版本号符合项目/网关软件的兼容性要求

## 源码来源与开源说明

- 本工程的核心烧录逻辑来自开源项目 **Universal Silabs Flasher**：  
  - GitHub 仓库：`https://github.com/NabuCasa/universal-silabs-flasher`
- 本仓库在其基础上做了以下工作：  
  - 增加 Windows 图形化界面（`src/gui_app.py`，Tkinter）  
  - 封装一键打包脚本 `src/build_windows.bat` 以及对应的 PyInstaller spec 文件  
  - 提供针对 Inswift 系列 Dongle 的固件打包与目录组织  
  - 增强部分探测/复位逻辑以及更友好的中文提示与文档

许可证相关信息请参考上游仓库及本工程的 `pyproject.toml` / 后续 LICENSE 文件。

## 产品购买与支持

我们在速卖通上提供完整的 Inswift Dongle 产品线，可直接搭配本工具使用：

- **We use our entire range of dongle products, AliExpress collects inswift dongle**  

- **Link to AliExpress Store**：<https://www.aliexpress.com/item/1005009387100041.html>
  
  ![image-20260317164830819](C:\Users\C\AppData\Roaming\Typora\typora-user-images\image-20260317164830819.png)

如需更多使用指导或固件更新，请关注本仓库的 `doc/` 文档更新，或在店铺页面联系商家技术支持。

