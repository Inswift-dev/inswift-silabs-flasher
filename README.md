## Overview

Inswift Silabs Flasher is a Windows GUI tool for flashing firmware to Silicon Labs-based wireless chips/dongles.  
It supports multiple protocols (Zigbee NCP, Zigbee Router, OpenThread RCP, Multi-PAN CPC, etc.) and is optimized for the Inswift range of USB dongle products.  
This project is based on the open-source `universal-silabs-flasher` project with localized GUI and workflow enhancements.

## Repository Layout

- **`doc/`** – Environment setup, build guides, GUI usage manuals and future operational guides  
  - Build & environment (Chinese)：[`doc/BUILD_CN.md`](doc/BUILD_CN.md)  
  - Build & environment (English)：[`doc/BUILD_EN.md`](doc/BUILD_EN.md)  
  - GUI User Guide (Chinese)：[`doc/Inswift_Silabs_Flasher_GUI_CN.md`](doc/Inswift_Silabs_Flasher_GUI_CN.md)  
  - GUI User Guide (English)：[`doc/Inswift_Silabs_Flasher_GUI_EN.md`](doc/Inswift_Silabs_Flasher_GUI_EN.md)

- **`firmware_bin/`** – Pre-built firmware images for production/maintenance flashing, organized by protocol and platform.  
  All firmware files are in `.gbl` format, grouped as:
  - `zigbee-ncp/` – Zigbee NCP firmware (EmberZNet NCP mode)  
  - `zigbee-router/` – Zigbee Router firmware  
  - `thread-rcp/` – OpenThread RCP firmware  
  - `multipan/` – Multi-PAN CPC firmware  
  - Typical subdirectories: `ZBM-MG21/`, `ZBM-MG24/`, etc., representing different chip platforms/products.  
    Example filenames:
    - `zigbee-ncp/ZBM-MG24/ncp_uart_hw_dongle_v8.2.1.0.gbl`  
    - `thread-rcp/ZBM-MG21/ot-rcp_dongle_v2.6.1.0.gbl`  
    - `multipan/ZBM-MG24/rcp-uart_dongle_v4.6.0.gbl`

- **`src/`** – Source code and build scripts for the flasher tool  
  - `gui_app.py` – Tkinter-based GUI entry point  
  - `universal_silabs_flasher/` – Core flashing logic, derived from upstream `universal-silabs-flasher`, implementing protocol handling, device probing, progress callbacks, etc.  
  - `build_windows.bat` – One-click Windows build script using PyInstaller  
  - `InswiftSilabsFlasher.spec` – PyInstaller spec file (data files and hidden imports, etc.)  
  - `requirements_gui.txt` – Dependency list for the GUI build (including `zigpy`, `bellows`, `pyserial-asyncio-fast`, `Pillow`, etc.)  
  - `pyproject.toml` – Project metadata and dependencies; `project.urls.repository` points to the upstream repo `https://github.com/NabuCasa/universal-silabs-flasher`.

- **`tools/`** – Prebuilt executable tools  
  - e.g. `tools/InswiftSilabsFlasher.exe` – ready-to-use GUI flasher for end users.

## Quick Start

### 1. Requirements

- OS: Windows 10 / Windows 11  
- Python: 3.9 or newer  
- Network: PyPI access (or a configured mirror)

For full environment setup and dependency installation details, see: [`doc/BUILD_EN.md`](doc/BUILD_EN.md).  
Key steps (summary):

1. Install Python 3.9+ and enable “Add Python to PATH” during installation.  
2. From the project root (containing `src/` and `requirements_gui.txt`), run:

```bash
python -m pip install --upgrade pip
python -m pip install -r src/requirements_gui.txt
```

Or follow the `pyproject.toml` based installation shown in `doc/BUILD_EN.md`.

### 2. Build the Windows Executable

To build your own GUI executable using PyInstaller, run the helper script from `src/`:

```bash
cd src
build_windows.bat
```

The script will:

- Upgrade `pip`  
- Install build-time dependencies from `requirements_gui.txt`  
- Install PyInstaller  
- Run PyInstaller using `InswiftSilabsFlasher.spec`

After a successful build, the main executable will be located at:

- `dist\InswiftSilabsFlasher.exe`

Alternatively, you can directly use the prebuilt binary shipped in this repo:

- `tools/InswiftSilabsFlasher.exe`

### 3. Basic GUI Workflow

Typical flashing workflow:

1. Connect an Inswift dongle (e.g., ZBM-MG21 / ZBM-MG24) to the PC via USB.  
2. Launch the tool by double-clicking `InswiftSilabsFlasher.exe` (either from `dist\` or from `tools\`).  
3. In the GUI:
   - Select a firmware file (`.gbl`) from the appropriate subdirectory under `firmware_bin/`  
   - Select the serial port (auto-scanned or manually entered, e.g., COM3)  
   - Choose the probe method (`ezsp`, `router`, `bootloader`, `cpc`, or `spinel`)  
   - Click **Start Flashing** and monitor the progress bar and log window

For detailed button descriptions, progress behavior, and advanced features such as writing IEEE addresses, please refer to:

- GUI User Guide (Chinese)：[`doc/Inswift_Silabs_Flasher_GUI_CN.md`](doc/Inswift_Silabs_Flasher_GUI_CN.md)  
- GUI User Guide (English)：[`doc/Inswift_Silabs_Flasher_GUI_EN.md`](doc/Inswift_Silabs_Flasher_GUI_EN.md)

## Firmware Directory & Versioning

The `firmware_bin/` folder is organized for quick selection of the correct image:

- **By protocol**:  
  - `zigbee-ncp/` – Zigbee NCP firmware (typically for coordinator/gateway)  
  - `zigbee-router/` – Zigbee Router firmware (router/end-device roles)  
  - `thread-rcp/` – OpenThread RCP firmware  
  - `multipan/` – Multi-PAN CPC firmware (multi-protocol support)

- **By platform/product**:  
  - Subdirectories such as `ZBM-MG21/`, `ZBM-MG24/` correspond to different chip platforms or product SKUs.

- **File naming (examples)**:  
  - `ncp_uart_hw_dongle_v8.2.1.0.gbl` – Zigbee NCP firmware, version v8.2.1.0  
  - `ot-rcp_dongle_v2.6.1.0.gbl` – OpenThread RCP firmware, version v2.6.1.0  
  - `light_devtype_dongle_v8.0.2.0.gbl` – Zigbee Router (light device type) firmware, version v8.0.2.0  
  - `rcp-uart_dongle_v4.6.0.gbl` – Multi-PAN CPC RCP firmware, version v4.6.0

Before flashing, always confirm:

- The protocol type matches your use case (e.g., NCP for coordinator/gateway, Router for router nodes).  
- The firmware version is compatible with your gateway software and network requirements.

## Upstream Project & Licensing

- The core flashing logic is derived from the open-source project **Universal Silabs Flasher**:  
  - GitHub: `https://github.com/NabuCasa/universal-silabs-flasher`

- This repository adds:  
  - A localized Windows GUI (`src/gui_app.py`, Tkinter-based)  
  - Convenience build script `src/build_windows.bat` and PyInstaller spec file  
  - Firmware packaging and directory layout tailored for Inswift dongle products  
  - Enhanced probe/reset logic and more user-friendly messages/logging

For license details, please refer to the upstream repository and this project’s `pyproject.toml` and future LICENSE file.

## Purchase & Support

We provide the full range of Inswift dongle products on AliExpress, ready to be used with this tool:

- **We use our entire range of dongle products, AliExpress collects inswift dongle**  

- **Link to AliExpress Store**: <https://www.aliexpress.com/item/1005009387100041.html>

  ![image-20260317164603244](C:\Users\C\AppData\Roaming\Typora\typora-user-images\image-20260317164603244.png)

For additional guidance or firmware updates, please watch for updates under the `doc/` directory or contact technical support via the AliExpress store.

