# Inswift Silabs Flasher GUI - User Guide

The application window, controls, dialogs, and on-screen log are **English**. This guide matches the exact control labels where relevant.

## Detailed Usage Steps

### 1. Connect the Device

- Connect the Zigbee adapter to your computer using a USB cable
- Confirm the port number (e.g., COM3) in Windows Device Manager

### 2. Launch the Application

- Double-click `InswiftSilabsFlasher.exe`
- The application window will open

### 3. Select Firmware

- Click the "Browse..." button
- Select a firmware file in `.gbl` format
- Supported device types will be shown in the log

### 4. Configure the Device

#### Device Port (label **Serial port:**)
- **Auto Scan**: The application automatically scans available serial ports on startup and lists them in the dropdown
- **Select Port**: Choose your device port from the dropdown (e.g., COM1, COM3)
- **Refresh Scan**: Click **Refresh** to rescan available serial ports
- **Manual Entry**: If no port is detected, you can enter the port name manually
- **Windows Check**: In Windows Device Manager, check "Ports (COM & LPT)" to confirm the port number

#### Device Type Probe (Standalone Feature)
The GUI uses a separated workflow:

- **Probe device**: probe only, no flashing (gray hint: *Probe order (Probe device only): …*)
- **Start flashing**: flash only, no pre-probe

Fixed probe order: `EZSP -> ROUTER -> RCP(SPINEL) -> CPC`

Fixed probe baud rates:

| Type | Baud Rate |
|------|-----------|
| EZSP | 115200 |
| ROUTER | 115200 |
| CPC | 115200 |
| SPINEL (RCP) | 460800 |

### 5. Start Flashing

1. Click **Start flashing**
2. The app enters bootloader directly (no device type probe)
3. Watch the log output
4. Wait for flashing to complete

### 6. Flashing Process

The application will automatically perform the following steps:

```
1. Read firmware file ✓
2. Parse firmware info ✓
3. Connect to device ✓
4. Trigger bootloader mode (RTS/DTR) ✓
5. Enter bootloader mode ✓
6. Flash firmware... (progress shown, updated every 1%)
7. Start new firmware ✓
```

**Progress Display**:
- **Progress bar** (section **Flash progress:**): updates in real time, about every 1%
- **Log**: detailed progress about every 1%
  - Format: `Flash progress: X% (X.XX MB / X.XX MB)`
  - Example: `Flash progress: 45% (1.23 MB / 2.75 MB)`

### 7. Device Type Probe (Optional)

To identify the running device type only:

1. Connect device and select serial port
2. Click **Probe device**
3. Check logs for detected type/version/app baud rate

Notes:
- This action does not start flashing
- Probe failure does not block direct flashing

### 8. Write IEEE Address (Optional)

To set a specific IEEE address for the device, use the Write IEEE Address feature:

#### Steps
1. Ensure the device is running **EmberZNet (EZSP) firmware**
   - This feature only supports EmberZNet devices
   - If the device runs other firmware types, this feature will not be available

2. Enter the IEEE address under **5. Write IEEE (EUI-64):**
   - Format 1: `00:3c:84:ff:fe:92:bb:2c` (with colon separators)
   - Format 2: `003c84fffe92bb2c` (no colons, 16 hex digits)
   - Both formats are supported

3. (Optional) Check **Force overwrite**
   - Unchecked by default: skips writing if the address already matches
   - Checked: forces write even when the address already matches

4. Click **Write IEEE**

5. Confirm the operation
   - A **Confirm** dialog will appear
   - ⚠️ **Warning**: On some firmware versions, writing the IEEE address is a **permanent** operation and cannot be undone
   - After confirming, the write will begin

#### Notes
- ⚠️ **Permanent Operation**: Some firmware versions permanently write the IEEE address to the device; it cannot be changed afterward
- ✅ **Smart Detection**: If the device’s current IEEE address already matches the target, the write will be skipped
- ✅ **Error Messages**: If the device type is not supported, a clear message will be shown
- 📝 **Logging**: All operations are recorded in the log window

#### Use Cases
- Keeping the same IEEE address when replacing a device
- Repairing a corrupted IEEE address
- Setting a specific IEEE address for network management

## FAQ

### Q1: Cannot Find Device Port

**Solutions**:
1. The application scans serial ports automatically; check whether the port dropdown lists any available ports
2. Click the "Refresh" button to rescan serial ports
3. Open "Device Manager" (Win+X → Device Manager)
4. Expand "Ports (COM & LPT)"
5. Find your USB serial device and note the COM number
6. Disconnect and reconnect the device to confirm the port number
7. If auto scan finds nothing, enter the port name manually (e.g., COM3)

### Q2: Device Connection Failed

**Possible Causes**:
- Device not connected correctly
- Wrong port number
- Port in use by another application
- Driver not installed

**Solutions**:
1. Check the USB connection
2. Confirm the port number is correct
3. Close other applications that may be using the port
4. Reinstall the USB serial driver

### Q3: Firmware Verification Failed

**Cause**: The firmware file may be corrupted or incompatible.

**Solutions**:
1. Download the firmware file again
2. Confirm the firmware is for your device
3. Try the "Force Flash" option (use with caution)

### Q4: Flashing Progress Stuck

**Solutions**:
1. Wait for a while (large transfers take time)
2. Check USB connection stability
3. If there is no response for a long time, restart the application and try again

### Q5: Firmware Flashed Successfully but Device Not Responding

**Solutions**:
1. Unplug and replug the USB device
2. Check the device LEDs
3. Try other serial tools to verify device status

### Q6: Progress Bar Not Showing or Not Moving

**Solutions**:
- Normal: The progress bar starts updating when the flashing data transfer phase begins
- Check the log window: progress is shown every 1%
- If there is no update for a long time: check the USB connection; you may need to reconnect the device

### Q7: How to Write IEEE Address

**Prerequisites**:
- The device must be running EmberZNet (EZSP) firmware
- Other firmware types (e.g., CPC, Spinel) do not support this feature

**Steps**:
1. Enter the IEEE address under **5. Write IEEE (EUI-64):**
2. (Optional) Check **Force overwrite**
3. Click **Write IEEE**
4. Confirm the operation

**Common Errors**:
- Log: `Error: device is not running EmberZNet; cannot write IEEE` — flash EmberZNet (EZSP) firmware first
- Dialog **Error** / `Invalid IEEE address`: check the format; it must be 8 bytes in hexadecimal

### Q8: Device Type Probe Is Slow or Fails

**Notes**:
- Device type probe is now standalone and does not affect flashing
- Probe baud rates are fixed: `SPINEL=460800`, all others `115200`

**Recommendations**:
1. Use **Start flashing** directly for daily upgrades
2. Use **Probe device** only when you need diagnostics
3. If probe fails but flashing works, proceed with flashing

### Q9: Cannot Enter Bootloader Again After Flashing Router Firmware

**Description**:
- After flashing Router firmware, re-flashing shows "Failed to enter bootloader"
- This is a known issue with Router firmware: the CLI command method may not be reliable

**Solution**:
The application handles this automatically:
1. **Automatic Fallback**: When the Router CLI command (`bootloader reboot`) fails, the application automatically tries RTS/DTR hardware reset
2. **How It Works**:
   - First tries the CLI command to enter bootloader (fastest)
   - If the CLI command fails or times out, it switches to RTS/DTR hardware reset
   - RTS/DTR uses the serial port’s RTS and DTR signals to force the device into bootloader mode
3. **Log Messages**: If hardware reset is used, the log will show:
   - `"Router CLI bootloader command failed. Attempting RTS/DTR hardware reset as fallback..."`
   - `"Successfully entered bootloader using RTS/DTR reset"`

**Notes**:
- Ensure a stable USB connection; hardware reset needs a stable serial link
- If both methods fail, check the device hardware or try unplugging and replugging the USB device

### Q10: Cannot Probe or Enter Bootloader Again After Flashing Multi-PAN (CPC) Firmware

**Description**:
- After flashing Multi-PAN (CPC) firmware, re-flashing shows "Device probe failed" or "Failed to enter bootloader"
- Error messages: `"Failed to probe running application type"` or `"Failed to enter bootloader"`
- This may be due to CPC firmware communication issues or corrupted firmware

**Solution**:
The application handles this automatically:
1. **Automatic Fallback**: When CPC protocol commands fail, the application automatically tries RTS/DTR hardware reset
2. **How It Works**:
   - First tries CPC protocol commands to enter bootloader (PROP_VALUE_SET and RESET)
   - If CPC commands fail or time out, it switches to RTS/DTR hardware reset
   - RTS/DTR uses the serial port’s RTS and DTR signals to force the device into bootloader mode
3. **Log Messages**: If hardware reset is used, the log will show:
   - `"CPC bootloader command failed. Attempting RTS/DTR hardware reset as fallback..."`
   - `"Successfully entered bootloader using RTS/DTR reset"`

**If probe fails** (device not communicating):
1. Probe is identification only and does not trigger flashing
2. You can still click **Start flashing** directly
3. If needed, replug the device and retry flashing

3. **If Hardware Reset Also Fails**:
   - Unplug and replug the USB device (after hardware reset)
   - Check the USB cable (try another cable)
   - Check device power (some devices need external power)
   - Some devices may require **holding the Boot button while power cycling** to enter bootloader
   - Verify that the device driver is installed correctly
   - Try other serial tools (e.g., PuTTY, serial terminal) to see if the device responds

**Notes**:
- Probe failure does not necessarily mean flash failure
- Probe and flash workflows are separated
- Keep USB connection stable; replug if needed

## Supported Firmware Types

- ✅ Zigbee NCP firmware (.gbl)
- ✅ Zigbee Router firmware (.gbl)
- ✅ OpenThread RCP firmware (.gbl)
- ✅ CPC Multi-PAN firmware (.gbl)
- ✅ EBL format firmware (.ebl)

## System Requirements

- **OS**: Windows 10/11
- **Python**: 3.9+ (if running from source)
- **Memory**: At least 100 MB free
- **USB**: USB 2.0 or higher

## Technical Information

- Based on: Universal Silabs Flasher
- GUI framework: Tkinter
- Packaging: PyInstaller
- Protocols: XMODEM, EZSP, CPC, Spinel

## Disclaimer

Using this tool to flash firmware involves risk. Please ensure that:
1. Important data is backed up
2. The correct firmware file is used
3. Power is stable
4. The USB connection is not disconnected during flashing

**By using this tool, you acknowledge that you understand and accept all risks.**
