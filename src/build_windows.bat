@echo off
chcp 65001 >nul
echo ==========================================
echo Inswift Silabs Flasher Windows打包脚本
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python版本:
python --version
echo.

REM 检查是否在正确的目录
if not exist "gui_app.py" (
    echo 错误: 找不到gui_app.py文件
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 升级pip
echo [1/4] 升级pip...
python -m pip install --upgrade pip --quiet

REM 安装依赖
echo [2/4] 安装依赖包...
if exist requirements_gui.txt (
    python -m pip install -r requirements_gui.txt --quiet
) else if exist requirements_test.txt (
    python -m pip install -r requirements_test.txt --quiet
) else (
    echo 错误: 未找到 requirements_gui.txt 或 requirements_test.txt
    pause
    exit /b 1
)
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

REM 安装打包工具
echo [3/4] 安装PyInstaller...
python -m pip install pyinstaller --quiet

echo [4/4] 开始打包...
REM 检查logo文件是否存在
if exist "logo.png" (
    echo 找到logo.png，将包含在打包中
    set LOGO_DATA=logo.png;.
) else if exist "logo.ico" (
    echo 找到logo.ico，将包含在打包中
    set LOGO_DATA=logo.ico;.
) else (
    echo 警告: 未找到logo文件，图标将使用默认图标
    set LOGO_DATA=
)

if defined LOGO_DATA (
    python -m PyInstaller --clean --onefile --windowed ^
        --name "InswiftSilabsFlasher" ^
        --add-data "universal_silabs_flasher;universal_silabs_flasher" ^
        --add-data "%LOGO_DATA%" ^
        --hidden-import "pyserial_asyncio_fast" ^
        --hidden-import "zigpy.types" ^
        --hidden-import "zigpy.serial" ^
        --hidden-import "coloredlogs" ^
        --hidden-import "PIL._tkinter_finder" ^
        gui_app.py
) else (
    python -m PyInstaller --clean --onefile --windowed ^
        --name "InswiftSilabsFlasher" ^
        --add-data "universal_silabs_flasher;universal_silabs_flasher" ^
        --hidden-import "pyserial_asyncio_fast" ^
        --hidden-import "zigpy.types" ^
        --hidden-import "zigpy.serial" ^
        --hidden-import "coloredlogs" ^
        --hidden-import "PIL._tkinter_finder" ^
        gui_app.py
)

if errorlevel 1 (
    echo.
    echo 打包失败，查看上方错误信息
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 打包完成！
echo.
echo 可执行文件位置: dist\InswiftSilabsFlasher.exe
echo 文件大小: 
if exist dist\InswiftSilabsFlasher.exe (
    for %%A in (dist\InswiftSilabsFlasher.exe) do echo   %%~zA 字节
)
echo.
echo 测试运行: dist\InswiftSilabsFlasher.exe
echo.
echo 分发说明:
echo   - 只需提供 dist\InswiftSilabsFlasher.exe 这一个文件即可
echo   - 用户可以直接双击运行，无需安装Python或其他依赖
echo   - 如果logo未显示，请将logo.png或logo.ico放在exe同目录下
echo ==========================================
pause
