#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inswift Silabs Flasher GUI - Silicon Labs firmware flashing tool (Zigbee / multipan / etc.)
"""

import asyncio
import logging
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

try:
    import serial.tools.list_ports

    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    _LOGGER.warning("pyserial is not installed; serial port auto-scan is disabled")

from universal_silabs_flasher.flasher import Flasher
from universal_silabs_flasher.const import ApplicationType, DEFAULT_BAUDRATES, ResetTarget
import zigpy.types


class FlasherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Inswift Silabs Flasher - Firmware flashing tool")
        self.root.geometry("800x600")

        self.firmware_path = tk.StringVar()
        self.device_port = tk.StringVar(value="")
        self.ieee_address = tk.StringVar(value="")
        self.force_write_ieee = tk.BooleanVar(value=False)

        self.is_running = False

        self.default_baudrates = {
            "ezsp": "115200",
            "router": "115200",
            "bootloader": "115200",
            "cpc": "115200",
            "spinel": "460800",
        }

        self.create_widgets()

    def set_window_icon(self):
        """Set window icon (title bar and taskbar)."""
        try:
            if getattr(sys, "frozen", False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            current_dir = os.getcwd()

            possible_paths = [
                os.path.join(base_path, "logo.ico"),
                os.path.join(base_path, "logo.png"),
                os.path.join(current_dir, "logo.ico"),
                os.path.join(current_dir, "logo.png"),
                "logo.ico",
                "logo.png",
            ]

            logo_path = None
            for path in possible_paths:
                full_path = os.path.abspath(path)
                if os.path.exists(full_path):
                    logo_path = full_path
                    _LOGGER.debug("Found logo file: %s", logo_path)
                    break

            if logo_path:
                try:
                    abs_logo_path = os.path.abspath(logo_path)

                    if abs_logo_path.lower().endswith(".ico"):
                        try:
                            self.root.iconbitmap(abs_logo_path)
                            _LOGGER.debug("Set .ico icon: %s", abs_logo_path)
                        except Exception as e:
                            _LOGGER.warning("iconbitmap failed for .ico: %s", e)
                            try:
                                from PIL import Image, ImageTk

                                logo_image = Image.open(abs_logo_path)
                                self.logo_photo = ImageTk.PhotoImage(logo_image)
                                self.root.iconphoto(True, self.logo_photo)
                                _LOGGER.debug("Set .ico via iconphoto")
                            except Exception as e2:
                                _LOGGER.warning("iconphoto also failed for .ico: %s", e2)
                    else:
                        try:
                            from PIL import Image, ImageTk

                            logo_image = Image.open(abs_logo_path)

                            if sys.platform == "win32":
                                try:
                                    import tempfile

                                    temp_dir = tempfile.gettempdir()
                                    temp_ico = os.path.join(temp_dir, "inswift_logo_temp.ico")

                                    if logo_image.mode != "RGBA":
                                        logo_image = logo_image.convert("RGBA")

                                    icon_48 = logo_image.resize((48, 48), Image.Resampling.LANCZOS)
                                    icon_48.save(temp_ico, format="ICO")

                                    self.root.iconbitmap(temp_ico)
                                    _LOGGER.debug("Created temp ICO and set icon: %s", temp_ico)
                                except Exception as ico_error:
                                    _LOGGER.debug("Temp ICO failed, using PNG: %s", ico_error)
                                    self.logo_photo = ImageTk.PhotoImage(logo_image)
                                    self.root.iconphoto(True, self.logo_photo)
                                    _LOGGER.debug("Set PNG via iconphoto")
                            else:
                                self.logo_photo = ImageTk.PhotoImage(logo_image)
                                self.root.iconphoto(True, self.logo_photo)
                                _LOGGER.debug("Set PNG via iconphoto")
                        except ImportError:
                            _LOGGER.warning("PIL not installed; cannot load PNG as window icon")
                            _LOGGER.warning("Install Pillow: pip install Pillow")
                        except Exception as e:
                            _LOGGER.warning("Failed to set PNG icon: %s", e)
                            import traceback

                            _LOGGER.debug("Details: %s", traceback.format_exc())
                except Exception as e:
                    _LOGGER.warning("Failed to set window icon: %s", e)
            else:
                _LOGGER.debug("No logo file found; using default icon")
                _LOGGER.debug("Searched paths: %s", possible_paths)
        except Exception as e:
            _LOGGER.warning("Window icon load error: %s", e)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        self.set_window_icon()

        ttk.Label(main_frame, text="1. Select firmware (.gbl):", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )

        firmware_frame = ttk.Frame(main_frame)
        firmware_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        firmware_frame.columnconfigure(1, weight=1)

        self.firmware_entry = ttk.Entry(firmware_frame, textvariable=self.firmware_path, state="readonly")
        self.firmware_entry.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(firmware_frame, text="Browse...", command=self.browse_firmware).grid(row=0, column=2)

        ttk.Label(main_frame, text="2. Device:", font=("", 10, "bold")).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )

        ttk.Label(main_frame, text="Serial port:").grid(row=3, column=0, sticky=tk.W, pady=5)
        port_frame = ttk.Frame(main_frame)
        port_frame.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        self.port_combo = ttk.Combobox(port_frame, textvariable=self.device_port, width=18, state="readonly")
        self.port_combo.grid(row=0, column=0, padx=(0, 5))

        refresh_btn = ttk.Button(port_frame, text="Refresh", command=self.scan_ports, width=8)
        refresh_btn.grid(row=0, column=1)

        ttk.Label(
            main_frame,
            text="Probe order (Probe device only): EZSP -> ROUTER -> RCP(SPINEL) -> CPC",
            foreground="gray",
        ).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)

        self.scan_ports()

        ttk.Label(main_frame, text="3. Flash progress:", font=("", 10, "bold")).grid(
            row=5, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )

        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, mode="determinate", variable=self.progress_var, length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.progress_label = ttk.Label(progress_frame, text="Idle")
        self.progress_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(main_frame, text="4. Log:", font=("", 10, "bold")).grid(
            row=7, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )

        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="5. Write IEEE (EUI-64):", font=("", 10, "bold")).grid(
            row=11, column=0, columnspan=3, sticky=tk.W, pady=(15, 5)
        )

        ieee_frame = ttk.Frame(main_frame)
        ieee_frame.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ieee_frame.columnconfigure(1, weight=1)

        ttk.Label(ieee_frame, text="IEEE address:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        ieee_entry_frame = ttk.Frame(ieee_frame)
        ieee_entry_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        self.ieee_entry = ttk.Entry(ieee_entry_frame, textvariable=self.ieee_address, width=25)
        self.ieee_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Label(
            ieee_frame,
            text="Format: 00:3c:84:ff:fe:92:bb:2c or 003c84fffe92bb2c",
            font=("", 8),
            foreground="gray",
        ).grid(row=1, column=1, sticky=tk.W, pady=(2, 0))

        force_frame = ttk.Frame(ieee_frame)
        force_frame.grid(row=0, column=2, sticky=tk.W)

        self.force_checkbox = ttk.Checkbutton(force_frame, text="Force overwrite", variable=self.force_write_ieee)
        self.force_checkbox.grid(row=0, column=0)

        write_ieee_btn = ttk.Button(force_frame, text="Write IEEE", command=self.start_write_ieee, width=15)
        write_ieee_btn.grid(row=0, column=1, padx=(10, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, columnspan=3, pady=20)

        self.start_button = ttk.Button(button_frame, text="Start flashing", command=self.start_flashing, width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.probe_button = ttk.Button(button_frame, text="Probe device", command=self.start_probe, width=20)
        self.probe_button.pack(side=tk.LEFT, padx=10)

        ttk.Button(button_frame, text="Clear log", command=self.clear_log, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Exit", command=self.root.quit, width=20).pack(side=tk.LEFT, padx=10)

    def scan_ports(self):
        """Scan available serial ports."""
        if not SERIAL_AVAILABLE:
            current_value = self.device_port.get()
            self.port_combo["values"] = (current_value,) if current_value else ()
            self.port_combo.config(state="normal")
            return

        try:
            ports = serial.tools.list_ports.comports()
            port_list = []

            for port in sorted(ports):
                port_name = port.device
                port_list.append(port_name)

            if port_list:
                self.port_combo["values"] = port_list
                current_value = self.device_port.get()
                if current_value not in port_list:
                    self.device_port.set(port_list[0])
                    if len(port_list) > 1:
                        self.log(f"Found {len(port_list)} port(s); selected: {port_list[0]}")
                else:
                    self.device_port.set(current_value)
                self.port_combo.config(state="readonly")
            else:
                self.port_combo["values"] = ()
                current_value = self.device_port.get()
                if not current_value:
                    self.device_port.set("")
                self.log("No serial ports found; check the USB connection")
                self.port_combo.config(state="normal")

        except Exception as e:
            _LOGGER.error("Serial scan failed: %s", e)
            self.log(f"Serial scan failed: {e}")
            current_value = self.device_port.get()
            if current_value:
                self.port_combo["values"] = (current_value,)
            self.port_combo.config(state="normal")

    def browse_firmware(self):
        filename = filedialog.askopenfilename(
            title="Select firmware",
            filetypes=[("GBL", "*.gbl"), ("EBL", "*.ebl"), ("All files", "*.*")],
        )
        if filename:
            self.firmware_path.set(filename)
            self.log(f"Firmware selected: {filename}")

    def log(self, message):
        def update():
            try:
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
            except Exception as e:
                _LOGGER.debug("Log update error: %s", e)

        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update)
        else:
            update()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def validate_ieee_address(self, ieee_str: str) -> zigpy.types.EUI64 | None:
        if not ieee_str:
            return None

        try:
            ieee = zigpy.types.EUI64.convert(ieee_str.strip())
            return ieee
        except (ValueError, TypeError) as e:
            _LOGGER.error("Invalid IEEE address %r: %s", ieee_str, e)
            return None

    def start_write_ieee(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Another task is running; please wait.")
            return

        if not self.device_port.get():
            messagebox.showerror("Error", "Please select a serial port.")
            return

        ieee_str = self.ieee_address.get().strip()
        if not ieee_str:
            messagebox.showerror("Error", "Please enter an IEEE address.")
            return

        ieee = self.validate_ieee_address(ieee_str)
        if ieee is None:
            messagebox.showerror(
                "Error",
                f"Invalid IEEE address: {ieee_str}\n"
                f"Use format: 00:3c:84:ff:fe:92:bb:2c or 003c84fffe92bb2c",
            )
            return

        force = self.force_write_ieee.get()
        confirm_msg = (
            f"Write this IEEE (EUI-64) address to the device?\n\n"
            f"New address: {ieee}\n"
            f"Force overwrite: {'Yes' if force else 'No'}\n\n"
            f"Note: on some firmware builds this change may be permanent."
        )
        if not messagebox.askyesno("Confirm", confirm_msg):
            return

        self.is_running = True
        self.start_button.config(state="disabled")
        self.log(f"Starting IEEE write: {ieee}")
        self.update_progress(0, "Preparing to write IEEE...")

        threading.Thread(target=self.run_write_ieee, daemon=True, args=(ieee, force)).start()

    def run_write_ieee(self, ieee: zigpy.types.EUI64, force: bool):
        try:
            asyncio.run(self.async_write_ieee(ieee, force))
        except Exception as e:
            self.log(f"IEEE write failed: {str(e)}")
            import traceback

            self.log(f"Details:\n{traceback.format_exc()}")
        finally:
            self.is_running = False
            self.start_button.config(state="normal")

    async def async_write_ieee(self, ieee: zigpy.types.EUI64, force: bool):
        self.log("Connecting to device to write IEEE address...")

        device = self.device_port.get()

        baudrates = DEFAULT_BAUDRATES.copy()
        default_baudrate = int(self.default_baudrates.get("ezsp", "115200"))
        baudrates[ApplicationType.EZSP] = [default_baudrate]
        self.log(f"Using default baud rate: {default_baudrate} (EZSP)")

        flasher = Flasher(
            device=device,
            baudrates=baudrates,
            probe_methods=(ApplicationType.EZSP, ApplicationType.GECKO_BOOTLOADER),
            bootloader_reset=(),
        )

        self.log(f"Device: {device}")

        try:
            self.log("Probing application type...")
            await flasher.probe_app_type(try_first=[ApplicationType.GECKO_BOOTLOADER, ApplicationType.EZSP])

            self.log(f"Detected application type: {flasher.app_type}")

            self.update_progress(50, "Writing IEEE address...")
            result = await flasher.write_emberznet_eui64(ieee, force=force)

            if result:
                self.update_progress(100, "IEEE write succeeded")
                self.log(f"IEEE address written: {ieee}")
            else:
                self.update_progress(100, "IEEE already matches; no write needed")
                self.log("Device IEEE already matches target; skipped write")

        except RuntimeError as e:
            error_msg = str(e)
            if "not running EmberZNet" in error_msg:
                self.log("Error: device is not running EmberZNet; cannot write IEEE")
                self.log(f"Current application type: {flasher.app_type}")
                self.log("IEEE write requires EmberZNet (EZSP) firmware")
            else:
                self.log(f"Error: {error_msg}")
            self.update_progress(0, f"Write failed: {error_msg}")
            raise
        except Exception as e:
            self.log(f"IEEE write error: {e}")
            self.update_progress(0, f"Write failed: {e}")
            raise

    def update_progress(self, percent, status=""):
        def update():
            try:
                percent_clamped = max(0, min(100, percent))
                self.progress_var.set(percent_clamped)
                if status:
                    self.progress_label.config(text=status)
                self.root.update_idletasks()
            except Exception as e:
                _LOGGER.debug("Progress update error: %s", e)

        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update)
        else:
            update()

    def start_flashing(self):
        if self.is_running:
            messagebox.showwarning("Warning", "A flash operation is already running.")
            return

        if not self.firmware_path.get():
            messagebox.showerror("Error", "Please select a firmware file.")
            return

        if not os.path.exists(self.firmware_path.get()):
            messagebox.showerror("Error", "Firmware file does not exist.")
            return

        if not self.device_port.get():
            messagebox.showerror("Error", "Please enter or select a serial port.")
            return

        self.is_running = True
        self.start_button.config(state="disabled")
        self.probe_button.config(state="disabled")
        self.clear_log()
        self.update_progress(0, "Starting...")

        threading.Thread(target=self.run_flashing, daemon=True).start()

    def run_flashing(self):
        try:
            asyncio.run(self.async_flash())
        except Exception as e:
            self.log(f"Flash failed: {str(e)}")
            import traceback

            self.log(f"Details:\n{traceback.format_exc()}")
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
            self.probe_button.config(state="normal")

    def start_probe(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Another task is running; please wait.")
            return

        if not self.device_port.get():
            messagebox.showerror("Error", "Please select a serial port.")
            return

        self.is_running = True
        self.start_button.config(state="disabled")
        self.probe_button.config(state="disabled")
        self.clear_log()
        self.update_progress(0, "Preparing probe...")
        threading.Thread(target=self.run_probe, daemon=True).start()

    def run_probe(self):
        try:
            asyncio.run(self.async_probe())
        except Exception as e:
            self.log(f"Probe failed: {str(e)}")
            import traceback

            self.log(f"Details:\n{traceback.format_exc()}")
        finally:
            self.is_running = False
            self.start_button.config(state="normal")
            self.probe_button.config(state="normal")

    async def async_probe(self):
        device = self.device_port.get()
        self.log("Starting application probe...")
        self.log(f"Device: {device}")
        self.log("Probe order: EZSP -> ROUTER -> RCP(SPINEL) -> CPC")

        probe_baudrates = {
            ApplicationType.GECKO_BOOTLOADER: [115200],
            ApplicationType.EZSP: [115200],
            ApplicationType.ROUTER: [115200],
            ApplicationType.SPINEL: [460800],
            ApplicationType.CPC: [115200],
        }

        flasher = Flasher(
            device=device,
            baudrates=probe_baudrates,
            probe_methods=(
                ApplicationType.EZSP,
                ApplicationType.ROUTER,
                ApplicationType.SPINEL,
                ApplicationType.CPC,
            ),
            bootloader_reset=(),
        )

        try:
            await flasher.probe_app_type(
                types=[
                    ApplicationType.EZSP,
                    ApplicationType.ROUTER,
                    ApplicationType.SPINEL,
                    ApplicationType.CPC,
                ]
            )
        except Exception as e:
            self.update_progress(0, "Probe failed")
            self.log(f"Application probe failed: {e}")
            return

        self.update_progress(100, "Probe complete")
        self.log(f"Detected application type: {flasher.app_type}")
        if flasher.app_version:
            self.log(f"Firmware version: {flasher.app_version}")
        if flasher.app_baudrate:
            self.log(f"Application baud rate: {flasher.app_baudrate}")
        self.log("Probe finished (no firmware was written)")

    async def async_flash(self):
        self.log("Starting flash workflow...")
        self.update_progress(0, "Preparing...")

        firmware_file = self.firmware_path.get()
        self.log(f"Reading firmware: {firmware_file}")

        try:
            with open(firmware_file, "rb") as f:
                firmware_data = f.read()
        except Exception as e:
            self.log(f"Failed to read firmware: {e}")
            self.update_progress(0, "Read failed")
            return

        self.log(f"Firmware size: {len(firmware_data)} bytes")

        from universal_silabs_flasher.firmware import parse_firmware_image

        try:
            fw_image = parse_firmware_image(firmware_data)
            self.log("Firmware image parsed OK")
        except Exception as e:
            self.log(f"Firmware parse failed: {e}")
            self.update_progress(0, "Parse failed")
            return

        metadata = None
        try:
            metadata = fw_image.get_nabucasa_metadata()
            if metadata:
                self.log(f"Firmware type: {metadata.fw_type}")
                self.log(f"Firmware version: {metadata.get_public_version()}")
                if metadata.baudrate:
                    self.log(f"Baud rate: {metadata.baudrate}")
        except Exception:
            self.log("Could not read firmware metadata")

        device = self.device_port.get()

        baudrates = DEFAULT_BAUDRATES.copy()
        baudrates[ApplicationType.GECKO_BOOTLOADER] = [115200]
        baudrates[ApplicationType.EZSP] = [115200]
        baudrates[ApplicationType.ROUTER] = [115200]
        baudrates[ApplicationType.CPC] = [115200]
        baudrates[ApplicationType.SPINEL] = [460800]

        flasher = Flasher(
            device=device,
            baudrates=baudrates,
            probe_methods=(
                ApplicationType.EZSP,
                ApplicationType.ROUTER,
                ApplicationType.SPINEL,
                ApplicationType.CPC,
            ),
            bootloader_reset=(ResetTarget.RTS_DTR,),
        )

        self.log(f"Device: {device}")

        self.log("Skipping app probe; entering bootloader directly")
        try:
            await flasher.trigger_bootloader(ResetTarget.RTS_DTR)
            flasher.app_type = ApplicationType.GECKO_BOOTLOADER
            flasher.app_baudrate = baudrates[ApplicationType.GECKO_BOOTLOADER][0]
            flasher.bootloader_baudrate = baudrates[ApplicationType.GECKO_BOOTLOADER][0]
        except Exception as e:
            self.log(f"Failed to enter bootloader: {e}")
            self.update_progress(0, "Bootloader entry failed")
            return

        self.log("Entering bootloader...")
        try:
            await flasher.enter_bootloader()
            self.log("Bootloader ready")
        except Exception as e:
            self.log(f"Failed to enter bootloader: {e}")
            self.update_progress(0, "Bootloader entry failed")
            return

        self.log("Flashing firmware...")
        self.update_progress(0, "Flashing...")

        try:
            from universal_silabs_flasher.gecko_bootloader import NoFirmwareError

            last_update_percent = -1
            last_log_percent = -1

            def progress_callback(current, total):
                nonlocal last_update_percent, last_log_percent
                if total == 0:
                    return

                upload_percent = (current / total) * 100

                current_mb = current / (1024 * 1024)
                total_mb = total / (1024 * 1024)

                current_percent = int(upload_percent)

                should_update = False
                if upload_percent >= 100:
                    should_update = True
                    last_update_percent = 100
                else:
                    display_percent = current_percent
                    if display_percent > last_update_percent:
                        should_update = True
                        last_update_percent = display_percent

                if current == 0 and total > 0:
                    total_mb_display = total / (1024 * 1024)
                    self.log(f"Starting firmware transfer... total: {total_mb_display:.2f} MB")

                if current_percent > last_log_percent:
                    last_log_percent = current_percent
                    self.log(f"Flash progress: {current_percent}% ({current_mb:.2f} MB / {total_mb:.2f} MB)")

                if should_update:
                    status_text = f"{current_percent}% ({current_mb:.2f} MB / {total_mb:.2f} MB)"
                    self.update_progress(upload_percent, status_text)

            await flasher.flash_firmware(
                fw_image,
                run_firmware=True,
                progress_callback=progress_callback,
            )
            self.update_progress(100, "Flash complete")
            self.log("Firmware flash complete")
            self.log("Device should restart with the new firmware")

        except NoFirmwareError as e:
            self.update_progress(95, "Flashed, but startup issue")
            self.log("Warning: firmware was written successfully")
            self.log("Warning: the application did not start automatically")
            self.log("Suggestions:")
            self.log("  1. Unplug and reconnect the USB device")
            self.log("  2. Power-cycle the device if needed")
            self.log("  3. The new firmware should run on the next boot")
            self.log("")
            self.log(f"Details: {e}")

        except Exception as e:
            self.log(f"Flash failed: {e}")
            self.update_progress(0, f"Flash failed: {e}")
            import traceback

            self.log(f"Details:\n{traceback.format_exc()}")


def main():
    root = tk.Tk()
    FlasherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
