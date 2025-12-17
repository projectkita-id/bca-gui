import os
import platform
import time
import threading
from datetime import datetime

import customtkinter as ctk
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports


# ------------ Konfigurasi UI - White/Blue Theme ------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Color Palette
BCA_BLUE = "#1454fb"
BCA_DARK_BLUE = "#0d3ea8"
BG_MAIN = "#ffffff"
CARD_BG = "#f8f9ff"
ENTRY_BG = "#ffffff"
ENTRY_BORDER = "#1454fb"
TEXT_PRIMARY = "#1a1a2e"
TEXT_SECONDARY = "#0d3ea8"
HEADER_BG = "#e8ecff"


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_accept_value):
        super().__init__(parent)
        
        self.accept_value = current_accept_value
        self.result = None
        
        # Window setup
        self.title("Settings - Accept Value")
        self.geometry("500x250")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        
        # Center window BEFORE showing
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (250 // 2)
        self.geometry(f"500x250+{x}+{y}")
        
        # PENTING: Urutan yang benar untuk Raspberry Pi
        self.update()  # Force window creation
        self.deiconify()  # Make sure it's visible
        self.attributes('-topmost', True)
        self.lift()
        self.focus_force()
        
        # Wait until window is fully visible before grab_set
        self.after(10, self._finish_init)
        
    def _finish_init(self):
        """Finish initialization after window is shown"""
        self.grab_set()
        self._build_ui()
        
    def _build_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="⚙️ Scanner 1 Validation Settings",
            font=ctk.CTkFont("Segoe UI", 18, "bold"),
            text_color=BCA_BLUE
        )
        title.pack(pady=(0, 15))
        
        # Description
        desc = ctk.CTkLabel(
            main_frame,
            text="Set the value that Scanner 1 should match for PASS decision.\nAny other value will be considered as REJECT (FAIL).",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=TEXT_SECONDARY,
            justify="center"
        )
        desc.pack(pady=(0, 20))
        
        # Accept Value Section
        accept_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=10)
        accept_frame.pack(fill="x", pady=(0, 20))
        
        accept_label_frame = ctk.CTkFrame(accept_frame, fg_color="transparent")
        accept_label_frame.pack(fill="x", padx=15, pady=(12, 8))
        
        ctk.CTkLabel(
            accept_label_frame,
            text="✅ ACCEPT Value (PASS)",
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            text_color="#0f9d58"
        ).pack(side="left")
        
        self.accept_entry = ctk.CTkEntry(
            accept_frame,
            height=40,
            font=ctk.CTkFont("Consolas", 12),
            fg_color=ENTRY_BG,
            border_color="#0f9d58",
            border_width=2
        )
        self.accept_entry.pack(fill="x", padx=15, pady=(0, 12))
        self.accept_entry.insert(0, self.accept_value)
        self.accept_entry.focus()
        
        # Info label
        info_label = ctk.CTkLabel(
            main_frame,
            text="💡 Other values will automatically trigger FAIL",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color="#757575"
        )
        info_label.pack(pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=120,
            height=40,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color="#757575",
            hover_color="#616161",
            command=self._cancel
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Settings",
            width=200,
            height=40,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color=BCA_BLUE,
            hover_color=BCA_DARK_BLUE,
            command=self._save
        )
        save_btn.pack(side="right")
        
    def _save(self):
        self.result = {
            'accept': self.accept_entry.get().strip()
        }
        if self.grab_current() == self:
            self.grab_release()
        self.destroy()
        
    def _cancel(self):
        self.result = None
        if self.grab_current() == self:
            self.grab_release()
        self.destroy()


class ScannerCard(ctk.CTkFrame):
    def __init__(self, master, title, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.configure(
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=3,
            border_color=BCA_BLUE,
        )

        # HEADER dengan Title dan Delete Button
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=50,
        )
        header.pack(fill="x", padx=20, pady=(15, 10))
        header.pack_propagate(False)

        # Title
        self.title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=BCA_BLUE,
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        # Delete Button
        self.delete_btn = ctk.CTkButton(
            header,
            text="🗑️",
            width=50,
            height=50,
            font=ctk.CTkFont(size=22),
            fg_color="#ff4444",
            hover_color="#cc0000",
            corner_radius=10,
            command=self.clear,
        )
        self.delete_btn.pack(side="right")

        # ENTRY FIELD (READONLY)
        self.entry = ctk.CTkEntry(
            self,
            height=60,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            fg_color=ENTRY_BG,
            border_width=3,
            border_color=ENTRY_BORDER,
            text_color=TEXT_PRIMARY,
            placeholder_text="",
            justify="left",
            state="readonly",
        )
        self.entry.pack(fill="x", padx=20, pady=(0, 15))

    def set_value(self, text: str):
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self.entry.configure(state="readonly")

    def clear(self):
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.configure(state="readonly")


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG_MAIN)

        # ---------- ROOT CONFIG ----------
        self.title("Envelope Sorting System")
        
        # FULLSCREEN KIOSK MODE
        self.attributes('-fullscreen', True)
        self.overrideredirect(True)
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        # fonts
        self.font_big_bold = ctk.CTkFont("Segoe UI", 16, "bold")
        self.font_med = ctk.CTkFont("Segoe UI", 12)
        self.font_med_bold = ctk.CTkFont("Segoe UI", 12, "bold")

        # serial
        self.arduino = None
        self.serial_thread = None
        self.system_running = False
        self.current_item_id = None

        # buffer scanner
        self.buffer = ""
        self.flush_job = None

        # *** Settings untuk Accept/Reject Values ***
        self.accept_value = "BCA0"  # Default accept value - selain ini akan dianggap REJECT

        # *** TAMBAHAN: Tracking scanner status untuk AUTO PASS FALLBACK ***
        self.scanner1_received = False
        self.scanner2_received = False
        self.scanner3_received = False
        self.scanner1_timeout_job = None
        self.SCANNER1_TIMEOUT = 5000  # 5 detik timeout

        # ---------- EXIT BUTTON ----------
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<Control-q>", lambda e: self.on_close())

        # ---------- UI BUILD ----------
        self._build_header()
        self._build_scanners()
        self._build_control_panel()

        # ---------- SERIAL ----------
        self._refresh_ports()
        self._connect_arduino()
        self._start_status_loop()

        # keybinding scanner
        self.bind_all("<Key>", self.on_key)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def exit_fullscreen(self, event=None):
        """Toggle fullscreen mode with ESC key"""
        if self.attributes('-fullscreen'):
            self.attributes('-fullscreen', False)
            self.overrideredirect(False)
            self.geometry("1024x600")
        else:
            self.attributes('-fullscreen', True)
            self.overrideredirect(True)

    # ================== UI BUILD ==================

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=70)
        header.pack(fill="x", pady=(10, 10))
        header.pack_propagate(False)

        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30)

        # Logo di kiri
        logo_frame = ctk.CTkFrame(content, fg_color="transparent")
        logo_frame.pack(side="left", fill="y")

        logo_path = os.path.join("assets", "img", "logo.png")
        if os.path.exists(logo_path):
            img = ctk.CTkImage(Image.open(logo_path), size=(140, 45))
            logo = ctk.CTkLabel(logo_frame, image=img, text="")
            logo.image = img
            logo.pack()
        else:
            title = ctk.CTkLabel(
                logo_frame,
                text="BCA",
                font=ctk.CTkFont("Segoe UI", 36, "bold"),
                text_color=BCA_BLUE,
            )
            title.pack()

        # Status indicators di kanan
        status_frame = ctk.CTkFrame(content, fg_color="transparent")
        status_frame.pack(side="right", fill="y")

        # Arduino Connection Status
        arduino_container = ctk.CTkFrame(
            status_frame,
            fg_color="#f0f0f0",
            corner_radius=8,
            border_width=2,
            border_color="#cccccc",
        )
        arduino_container.pack(pady=(0, 6))

        arduino_inner = ctk.CTkFrame(arduino_container, fg_color="transparent")
        arduino_inner.pack(padx=10, pady=6)

        self.arduino_status_indicator = ctk.CTkLabel(
            arduino_inner,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color="#ff4444",
            width=25,
        )
        self.arduino_status_indicator.pack(side="left", padx=(0, 6))

        arduino_text_frame = ctk.CTkFrame(arduino_inner, fg_color="transparent")
        arduino_text_frame.pack(side="left")

        ctk.CTkLabel(
            arduino_text_frame,
            text="Arduino",
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        self.arduino_port_label = ctk.CTkLabel(
            arduino_text_frame,
            text="Disconnected",
            font=ctk.CTkFont("Segoe UI", 8),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.arduino_port_label.pack(anchor="w")

        # System Status
        system_container = ctk.CTkFrame(
            status_frame,
            fg_color="#f0f0f0",
            corner_radius=8,
            border_width=2,
            border_color="#cccccc",
        )
        system_container.pack()

        system_inner = ctk.CTkFrame(system_container, fg_color="transparent")
        system_inner.pack(padx=10, pady=6)

        self.system_status_indicator = ctk.CTkLabel(
            system_inner,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color="#ff4444",
            width=25,
        )
        self.system_status_indicator.pack(side="left", padx=(0, 6))

        system_text_frame = ctk.CTkFrame(system_inner, fg_color="transparent")
        system_text_frame.pack(side="left")

        ctk.CTkLabel(
            system_text_frame,
            text="System",
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        self.system_status_label = ctk.CTkLabel(
            system_text_frame,
            text="STOPPED",
            font=ctk.CTkFont("Segoe UI", 8),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.system_status_label.pack(anchor="w")

    def _build_scanners(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=(10, 10))

        self.scanner1 = ScannerCard(container, "SCANNER 1")
        self.scanner1.pack(fill="both", expand=True, pady=(0, 15))

        self.scanner2 = ScannerCard(container, "SCANNER 2")
        self.scanner2.pack(fill="both", expand=True, pady=(0, 15))

        self.scanner3 = ScannerCard(container, "SCANNER 3")
        self.scanner3.pack(fill="both", expand=True)

    def _build_control_panel(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=(20, 30))

        btn_container = ctk.CTkFrame(frame, fg_color="transparent")
        btn_container.pack(expand=True)

        self.btn_start = ctk.CTkButton(
            btn_container,
            text="START SYSTEM",
            fg_color="#0f9d58",
            hover_color="#0b7c45",
            height=80,
            width=300,
            font=ctk.CTkFont("Segoe UI", 24, "bold"),
            corner_radius=12,
            command=self.start_system,
        )
        self.btn_start.pack(side="left", padx=15)

        self.btn_stop = ctk.CTkButton(
            btn_container,
            text="STOP SYSTEM",
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            height=80,
            width=300,
            font=ctk.CTkFont("Segoe UI", 24, "bold"),
            corner_radius=12,
            command=self.stop_system,
            state="disabled",
        )
        self.btn_stop.pack(side="left", padx=15)

        # *** SETTINGS BUTTON ***
        self.btn_settings = ctk.CTkButton(
            btn_container,
            text="⚙️ SETTINGS",
            fg_color=BCA_BLUE,
            hover_color=BCA_DARK_BLUE,
            height=80,
            width=280,
            font=ctk.CTkFont("Segoe UI", 24, "bold"),
            corner_radius=12,
            command=self.open_settings,
        )
        self.btn_settings.pack(side="left", padx=15)

    # ================== SETTINGS ==================

    def open_settings(self):
        """Open settings dialog - Raspberry Pi optimized"""
        # Temporarily disable overrideredirect AND fullscreen
        was_override = self.overrideredirect()
        was_fullscreen = self.attributes('-fullscreen')
        
        # IMPORTANT: Disable window locking FIRST
        if was_fullscreen:
            self.attributes('-fullscreen', False)
        if was_override:
            self.overrideredirect(False)
        
        # CRITICAL: Withdraw main window completely
        self.withdraw()
        
        # Force update
        self.update_idletasks()
        self.update()
        
        # Small delay
        time.sleep(0.1)
        
        # Create and show dialog
        dialog = SettingsDialog(self, self.accept_value)
        
        # Wait for dialog to close
        self.wait_window(dialog)
        
        # Show main window again
        self.deiconify()
        
        # Restore main window state
        if was_override:
            self.overrideredirect(True)
        if was_fullscreen:
            self.attributes('-fullscreen', True)
        
        # Force focus back to main window
        self.lift()
        self.focus_force()
        
        # Process result
        if dialog.result:
            self.accept_value = dialog.result['accept']
            print("=" * 50)
            print("⚙️ SETTINGS UPDATED")
            print(f"✅ Accept Value: {self.accept_value}")
            print(f"❌ Reject: Any other value")
            print("=" * 50)

    # ================== SERIAL ==================

    def _refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        print(f"🔄 Found {len(ports)} COM ports")

    def _connect_to_port(self, port_name):
        try:
            if self.arduino and self.arduino.is_open:
                self.arduino.close()
                
            self.arduino = serial.Serial(port_name, 9600, timeout=1)
            time.sleep(2)
            
            self.arduino_status_indicator.configure(text_color="#4caf50")
            self.arduino_port_label.configure(text=port_name)
            
            print("=" * 50)
            print(f"✓ Connected to Arduino on {port_name}")
            print("=" * 50)
            
            self._start_serial_thread()
            
        except Exception as e:
            print(f"❌ Failed to connect to {port_name}: {e}")
            self.arduino = None

    def _connect_arduino(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if "Arduino" in p.description or "USB-SERIAL" in p.description or "USB Serial" in p.description or "CH340" in p.description:
                self._connect_to_port(p.device)
                return
                
        print("=" * 50)
        print("⚠ No Arduino found. Select port manually.")
        print("=" * 50)
        self.arduino = None

    def _start_serial_thread(self):
        t = threading.Thread(target=self._serial_reader, daemon=True)
        t.start()
        self.serial_thread = t

    def _serial_reader(self):
        while self.arduino and self.arduino.is_open:
            try:
                line = self.arduino.readline().decode(errors="ignore").strip()
                if line:
                    self.after(0, lambda l=line: self._handle_serial_line(l))
            except Exception:
                break

    def _handle_serial_line(self, line: str):
        if not line.strip():
            return

        if line.startswith("SCAN1_OK:"):
            item_id = line.split(":")[-1]
            print(f"✓ Arduino: Scanner 1 OK (ID: {item_id})")
            
        elif line.startswith("SCAN2_OK:"):
            item_id = line.split(":")[-1]
            print(f"✓ Arduino: Scanner 2 OK (ID: {item_id})")
            
        elif line.startswith("SCAN3_OK:"):
            item_id = line.split(":")[-1]
            print(f"✓ Arduino: Scanner 3 OK (ID: {item_id})")
            
        elif line.startswith("RESULT:PASS:"):
            item_id = line.split(":")[-1]
            print(f"🟢 HASIL: BENAR (Mengandung {self.accept_value}) - ID: {item_id}")
            self._show_result_notification("BENAR", True)
            
        elif line.startswith("RESULT:FAIL:"):
            item_id = line.split(":")[-1]
            print(f"🔴 HASIL: SALAH (Tidak mengandung {self.accept_value}) - ID: {item_id}")
            self._show_result_notification("SALAH", False)
            
        elif line.startswith("RESULT:UNKNOWN:"):
            item_id = line.split(":")[-1]
            print(f"⚠ HASIL: TIDAK DIKENAL - ID: {item_id}")
            
        elif line.startswith("SERVO:"):
            angle = line.split(":")[-1]
            print(f"🔧 Servo digerakkan ke: {angle}")
            
        elif line.startswith("COMPLETE:"):
            item_id = line.split(":")[-1]
            print(f"✓ Proses selesai untuk ID: {item_id}")
            print("=" * 50)
            self.current_item_id = None

    def _show_result_notification(self, result: str, is_pass: bool):
        if is_pass:
            self.scanner1.configure(border_color="#4caf50")
            self.after(2000, lambda: self.scanner1.configure(border_color=ENTRY_BORDER))
        else:
            self.scanner1.configure(border_color="#ff4444")
            self.after(2000, lambda: self.scanner1.configure(border_color=ENTRY_BORDER))

    def _send_cmd(self, cmd: str):
        if self.arduino and self.arduino.is_open:
            full_cmd = cmd + "\n"
            bytes_sent = self.arduino.write(full_cmd.encode("utf-8"))
            print(f">> SENT: '{cmd}' ({bytes_sent} bytes)")
            self.arduino.flush()
        else:
            print("❌ Arduino belum terhubung")

    def _start_status_loop(self):
        if self.arduino and self.arduino.is_open:
            self._send_cmd("status")
        self.after(3000, self._start_status_loop)

    # ================== START / STOP ==================

    def start_system(self):
        if not self.arduino or not self.arduino.is_open:
            print("❌ Tidak bisa START: Arduino belum terhubung!")
            return
            
        self.system_running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        
        self.system_status_indicator.configure(text_color="#4caf50")
        self.system_status_label.configure(text="RUNNING")
        self._send_cmd("start")
        print("=" * 50)
        print("🚀 SYSTEM STARTED - Siap menerima barcode")
        print(f"✅ Accept Value: {self.accept_value}")
        print(f"❌ Reject: Any other value")
        print("=" * 50)
        
        self.scanner1.clear()
        self.scanner2.clear()
        self.scanner3.clear()
        self.current_item_id = None
        self._reset_scanner_tracking()

    def stop_system(self):
        self.system_running = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        
        self.system_status_indicator.configure(text_color="#ff4444")
        self.system_status_label.configure(text="STOPPED")
        self._send_cmd("stop")
        print("=" * 50)
        print("⏸ SYSTEM STOPPED")
        print("=" * 50)
        self._send_cmd("reset")
        self.current_item_id = None
        self._reset_scanner_tracking()

    # ================== SCANNER TRACKING (AUTO PASS FALLBACK) ==================

    def _reset_scanner_tracking(self):
        """Reset tracking status semua scanner"""
        self.scanner1_received = False
        self.scanner2_received = False
        self.scanner3_received = False
        
        # Cancel timeout job jika ada
        if self.scanner1_timeout_job:
            self.after_cancel(self.scanner1_timeout_job)
            self.scanner1_timeout_job = None

    def _start_scanner1_timeout(self):
        """Mulai timeout counter untuk Scanner 1"""
        # Cancel timeout sebelumnya jika ada
        if self.scanner1_timeout_job:
            self.after_cancel(self.scanner1_timeout_job)
        
        # Start timeout baru
        self.scanner1_timeout_job = self.after(
            self.SCANNER1_TIMEOUT, 
            self._handle_scanner1_timeout
        )
        print(f"⏲ Scanner 1 timeout started ({self.SCANNER1_TIMEOUT/1000}s)")

    def _handle_scanner1_timeout(self):
        """Handle ketika Scanner 1 timeout - auto PASS jika Scanner 2 & 3 sudah dapat"""
        self.scanner1_timeout_job = None
        
        if not self.scanner1_received:
            print("=" * 50)
            print("⚠ SCANNER 1 TIMEOUT!")
            
            # Cek apakah Scanner 2 dan 3 sudah dapat input
            if self.scanner2_received and self.scanner3_received:
                print("✓ Scanner 2 & 3 terdeteksi")
                print(f"🔄 AUTO FALLBACK: Dianggap sebagai {self.accept_value} (PASS)")
                
                # Set Scanner 1 dengan placeholder
                self.scanner1.set_value("[AUTO PASS - NO SCAN]")
                
                # Generate Item ID jika belum ada
                if not self.current_item_id:
                    self.current_item_id = int(time.time() * 1000) % 100000
                
                # Kirim command PASS ke Arduino
                self._send_cmd("test_pass")
                print(f"🟢 Servo akan ke posisi 160° (PASS)")
                print("=" * 50)
                
            else:
                print("❌ Scanner 2 atau 3 belum lengkap - Menunggu input...")
                print("=" * 50)

    def _check_auto_pass_condition(self):
        """Cek kondisi untuk auto PASS ketika Scanner 2 atau 3 dapat input"""
        # Jika Scanner 1 belum dapat tapi Scanner 2 dan 3 sudah dapat
        if not self.scanner1_received and self.scanner2_received and self.scanner3_received:
            # Cancel timeout karena kondisi sudah terpenuhi
            if self.scanner1_timeout_job:
                self.after_cancel(self.scanner1_timeout_job)
                self.scanner1_timeout_job = None
            
            print("=" * 50)
            print("⚠ SCANNER 1 BELUM SCAN")
            print("✓ Scanner 2 & 3 sudah terdeteksi")
            print(f"🔄 AUTO FALLBACK: Dianggap sebagai {self.accept_value} (PASS)")
            
            # Set Scanner 1 dengan placeholder
            self.scanner1.set_value("[AUTO PASS - NO SCAN]")
            
            # Generate Item ID jika belum ada
            if not self.current_item_id:
                self.current_item_id = int(time.time() * 1000) % 100000
            
            # Kirim command PASS ke Arduino
            self._send_cmd("test_pass")
            print(f"🟢 Servo akan ke posisi 160° (PASS)")
            print("=" * 50)

    # ================== SCANNER INPUT ==================

    def on_key(self, event):
        ch = event.char

        if event.keysym == "Return":
            self._process_buffer()
            self.buffer = ""
            return

        if ch and ch.isprintable():
            self.buffer += ch
            self._schedule_flush(120)

    def _schedule_flush(self, delay_ms: int):
        if self.flush_job:
            self.after_cancel(self.flush_job)
        self.flush_job = self.after(delay_ms, self._process_if_pending)

    def _process_if_pending(self):
        self.flush_job = None
        if self.buffer:
            self._process_buffer()
            self.buffer = ""

    def _identify_scanner(self, code: str) -> str:
        """Identifikasi scanner berdasarkan format barcode"""
        code = code.strip()
        
        # Scanner 1: 16 karakter (harus mengandung accept_value atau reject_value)
        if len(code) == 16:
            return "scanner1"
        
        # Scanner 2: Lebih dari 16 karakter dan diawali BCA
        if len(code) > 16 and code.startswith("BCA"):
            return "scanner2"
        
        # Scanner 3: 10 digit angka
        if len(code) == 10 and code.isdigit():
            return "scanner3"
        
        return "unknown"

    def _process_buffer(self):
        code = self.buffer.strip()
        if not code:
            return

        scanner = self._identify_scanner(code)

        if scanner == "scanner1":
            # *** Scanner 1 berhasil scan ***
            self.scanner1_received = True
            
            # Cancel timeout karena Scanner 1 sudah dapat
            if self.scanner1_timeout_job:
                self.after_cancel(self.scanner1_timeout_job)
                self.scanner1_timeout_job = None
            
            self.scanner1.set_value(code)
            self.current_item_id = int(time.time() * 1000) % 100000
            self._send_cmd(f"SCAN1:{self.current_item_id}:{code}")
            print(f"✓ Scanner 1: {code} (ID: {self.current_item_id})")
            
            # *** DETEKSI BERDASARKAN SETTINGS VALUE ***
            if self.accept_value in code:
                print(f"🔍 Terdeteksi: LULUS (Mengandung {self.accept_value}) - Servo akan ke 160°")
                self._send_cmd("test_pass")
            else:
                print(f"🔍 Terdeteksi: GAGAL (Tidak mengandung {self.accept_value}) - Servo akan ke 120°")
                time.sleep(3)
                self._send_cmd("test_fail")
                
        elif scanner == "scanner2":
            # *** Scanner 2 berhasil scan ***
            self.scanner2_received = True
            self.scanner2.set_value(code)
            
            # Start timeout untuk Scanner 1 jika belum ada
            if not self.scanner1_received and not self.scanner1_timeout_job:
                self._start_scanner1_timeout()
            
            # Generate Item ID jika belum ada (untuk kasus Scanner 1 belum scan)
            if not self.current_item_id:
                self.current_item_id = int(time.time() * 1000) % 100000
            
            self._send_cmd(f"SCAN2:{self.current_item_id}:{code}")
            print(f"✓ Scanner 2: {code}")
            
            # Cek kondisi auto PASS
            self._check_auto_pass_condition()
                
        elif scanner == "scanner3":
            # *** Scanner 3 berhasil scan ***
            self.scanner3_received = True
            self.scanner3.set_value(code)
            
            # Start timeout untuk Scanner 1 jika belum ada
            if not self.scanner1_received and not self.scanner1_timeout_job:
                self._start_scanner1_timeout()
            
            # Generate Item ID jika belum ada (untuk kasus Scanner 1 belum scan)
            if not self.current_item_id:
                self.current_item_id = int(time.time() * 1000) % 100000
            
            self._send_cmd(f"SCAN3:{self.current_item_id}:{code}")
            print(f"✓ Scanner 3: {code}")
            
            # Cek kondisi auto PASS
            self._check_auto_pass_condition()
        else:
            print(f"❌ Format tidak dikenali: {code} (Panjang: {len(code)})")

    # ================== CLOSE ==================

    def on_close(self):
        if self.arduino and self.arduino.is_open:
            self._send_cmd("reset")
            time.sleep(0.5)
            self.arduino.close()
            print("Arduino connection closed.")
        self.destroy()


# ==================== MAIN ====================

if __name__ == "__main__":
    app = App()
    app.mainloop