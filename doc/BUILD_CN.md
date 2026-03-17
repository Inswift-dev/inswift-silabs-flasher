# Inswift Silabs Flasher 环境搭建与编译教程（中文）

## 一、环境要求

- **操作系统**: Windows 10/11
- **Python**: 3.9 或更高版本
- **网络**: 能访问 PyPI（用于安装依赖）

## 二、环境搭建

### 2.1 安装 Python

1. 打开 [Python 官网](https://www.python.org/downloads/) 下载 Python 3.9+ 安装包。
2. 安装时**勾选 “Add Python to PATH”**。
3. 在命令提示符或 PowerShell 中执行 `python --version` 确认安装成功。

### 2.2 获取项目文件（最小移植清单）

将以下文件/目录复制到新工程目录中，保持相对路径一致：

| 类型     | 路径 |
|----------|------|
| 入口脚本 | `gui_app.py` |
| 核心包   | 整个目录 `universal_silabs_flasher/` |
| 打包配置 | `InswiftSilabsFlasher.spec` |
| 打包脚本 | `build_windows.bat` |
| 依赖列表 | `requirements_gui.txt` |
| 项目配置 | `pyproject.toml`（可选，用于 pip 安装） |
| 图标     | `logo.png` 或 `logo.ico`（可选） |

目录结构示例：

```
新工程根目录/
├── gui_app.py
├── universal_silabs_flasher/
│   ├── __init__.py
│   ├── __main__.py
│   ├── flasher.py
│   ├── const.py
│   ├── common.py
│   ├── emberznet.py
│   ├── gecko_bootloader.py
│   ├── firmware.py
│   ├── flash.py
│   ├── router.py
│   ├── spinel.py
│   ├── spinel_types.py
│   ├── cpc.py
│   ├── cpc_types.py
│   ├── xmodemcrc.py
│   └── gpio.py
├── InswiftSilabsFlasher.spec
├── build_windows.bat
├── requirements_gui.txt
├── pyproject.toml          （可选）
└── logo.png                 （可选）
```

### 2.3 安装依赖

在项目根目录打开命令提示符或 PowerShell，执行：

```batch
python -m pip install --upgrade pip
python -m pip install -r requirements_gui.txt
```

若使用 `pyproject.toml` 安装（需在含 `pyproject.toml` 的目录下）：

```batch
pip install -e .
pip install pyserial Pillow
```

## 三、编译步骤

### 方法一：使用打包脚本（推荐）

1. 在项目根目录双击运行 `build_windows.bat`，或在命令行执行：
   ```batch
   build_windows.bat
   ```
2. 脚本会自动：升级 pip、安装依赖、安装 PyInstaller、执行打包。
3. 完成后可执行文件位于：`dist\InswiftSilabsFlasher.exe`。

### 方法二：使用 PyInstaller 命令行

```batch
pip install pyinstaller
pyinstaller --clean InswiftSilabsFlasher.spec
```

生成的可执行文件同样在 `dist\InswiftSilabsFlasher.exe`。

### 方法三：使用 spec 指定名称（如 UniversalSilabsFlasher）

若项目中有 `UniversalSilabsFlasher.spec`（输出名为 `UniversalSilabsFlasher.exe`），执行：

```batch
pyinstaller --clean UniversalSilabsFlasher.spec
```

## 四、验证与分发

- **本地验证**：双击 `dist\InswiftSilabsFlasher.exe`（或对应的 exe）确认能正常启动和烧录。
- **分发**：只需将 `dist` 下的单个 exe 提供给用户即可，无需再安装 Python 或依赖；若需窗口图标，可将 `logo.png` 或 `logo.ico` 与 exe 放在同一目录。

## 五、常见问题

- **找不到 Python**：确认已勾选 “Add Python to PATH”，或使用完整路径运行 `python`。
- **依赖安装失败**：检查网络与 PyPI 访问，必要时使用国内镜像：  
  `pip install -r requirements_gui.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- **打包报错 “找不到 gui_app.py”**：确保在项目根目录执行脚本，且根目录下存在 `gui_app.py`。
- **打包后运行报错**：检查是否包含整个 `universal_silabs_flasher` 目录，且 spec 中 `datas` 包含 `('universal_silabs_flasher', 'universal_silabs_flasher')`。
