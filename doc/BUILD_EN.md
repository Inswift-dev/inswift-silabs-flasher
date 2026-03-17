# Inswift Silabs Flasher — Environment Setup and Build Guide (English)

## 1. Requirements

- **OS**: Windows 10/11
- **Python**: 3.9 or newer
- **Network**: PyPI access for installing dependencies

## 2. Environment Setup

### 2.1 Install Python

1. Download Python 3.9+ from [python.org/downloads](https://www.python.org/downloads/).
2. During installation, **check “Add Python to PATH”**.
3. In Command Prompt or PowerShell run `python --version` to confirm.

### 2.2 Get Project Files (Minimal Port Checklist)

Copy the following into your new project directory, keeping the same relative layout:

| Type        | Path |
|-------------|------|
| Entry script | `gui_app.py` |
| Core package | Entire folder `universal_silabs_flasher/` |
| Pack config  | `InswiftSilabsFlasher.spec` |
| Build script | `build_windows.bat` |
| Dependencies | `requirements_gui.txt` |
| Project config | `pyproject.toml` (optional) |
| Icon        | `logo.png` or `logo.ico` (optional) |

Example layout:

```
project_root/
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
├── pyproject.toml          (optional)
└── logo.png                 (optional)
```

### 2.3 Install Dependencies

From the project root in Command Prompt or PowerShell:

```batch
python -m pip install --upgrade pip
python -m pip install -r requirements_gui.txt
```

If using `pyproject.toml` in the same repo:

```batch
pip install -e .
pip install pyserial Pillow
```

## 3. Build Steps

### Option A: Build script (recommended)

1. From the project root, run `build_windows.bat` (double-click or from command line).
2. The script will upgrade pip, install dependencies, install PyInstaller, and run the build.
3. Output: `dist\InswiftSilabsFlasher.exe`.

### Option B: PyInstaller command line

```batch
pip install pyinstaller
pyinstaller --clean InswiftSilabsFlasher.spec
```

Output is again `dist\InswiftSilabsFlasher.exe`.

### Option C: Using another spec (e.g. UniversalSilabsFlasher)

If you use `UniversalSilabsFlasher.spec`:

```batch
pyinstaller --clean UniversalSilabsFlasher.spec
```

Output: `dist\UniversalSilabsFlasher.exe`.

## 4. Verification and Distribution

- **Verify**: Run `dist\InswiftSilabsFlasher.exe` (or the exe from your spec) and confirm the GUI starts and flashing works.
- **Distribution**: Share only the single exe; no Python or extra dependencies are required. For a custom window icon, place `logo.png` or `logo.ico` next to the exe.

## 5. Troubleshooting

- **Python not found**: Ensure “Add Python to PATH” was selected, or run `python` by full path.
- **Dependency install fails**: Check network and PyPI; try a mirror, e.g.  
  `pip install -r requirements_gui.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- **Build error “gui_app.py not found”**: Run the script from the project root where `gui_app.py` exists.
- **Exe fails at runtime**: Ensure the full `universal_silabs_flasher` folder is present and the spec’s `datas` includes `('universal_silabs_flasher', 'universal_silabs_flasher')`.
