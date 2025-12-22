import os
import platform
import time
import threading
import json
from datetime import datetime
import requests

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
    def __init__(self, parent, current_settings):
        super().__init__(parent)
        
        self.validation_settings = current_settings.copy()
        self.result = None
        
        # Window setup
        self.title("Settings - Scanner Validation")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.batch_record_id = None  # Simpan record_id dari API start
        self.api_base_url = "http://127.0.0.1:8000"  # Base URL API

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"600x400+{x}+{y}")
        
        self.update()
        self.deiconify()
        self.attributes('-topmost', True)
        self.lift()
        self.focus_force()
        
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
            text="⚙️ Scanner Validation Settings",
            font=ctk.CTkFont("Segoe UI", 20, "bold"),
            text_color=BCA_BLUE
        )
        title.pack(pady=(0, 10))
        
        # Description
        desc = ctk.CTkLabel(
            main_frame,
            text="Select which scanners should be validated against the database.\nChecked scanners will be compared with JSON data for PASS/FAIL decision.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=TEXT_SECONDARY,
            justify="center"
        )
        desc.pack(pady=(0, 20))
        
        # Checkbox Section
        checkbox_container = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=12)
        checkbox_container.pack(fill="x", pady=(0, 15))
        
        # Header
        header_label = ctk.CTkLabel(
            checkbox_container,
            text="📋 Select Scanners for Validation",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=BCA_BLUE
        )
        header_label.pack(pady=(15, 10))
        
        # Checkboxes
        self.checkbox_frame = ctk.CTkFrame(checkbox_container, fg_color="transparent")
        self.checkbox_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Scanner 1
        scanner1_frame = ctk.CTkFrame(self.checkbox_frame, fg_color="#ffffff", corner_radius=8, height=50)
        scanner1_frame.pack(fill="x", pady=5)
        scanner1_frame.pack_propagate(False)
        
        self.check_scanner1 = ctk.CTkCheckBox(
            scanner1_frame,
            text="Scanner 1 - Primary Barcode (16 chars)",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT_PRIMARY,
            fg_color=BCA_BLUE,
            hover_color=BCA_DARK_BLUE,
            checkbox_width=22,
            checkbox_height=22,
        )
        self.check_scanner1.pack(side="left", padx=15, pady=12)
        if self.validation_settings.get("scanner1", True):
            self.check_scanner1.select()
        
        # Scanner 2
        scanner2_frame = ctk.CTkFrame(self.checkbox_frame, fg_color="#ffffff", corner_radius=8, height=50)
        scanner2_frame.pack(fill="x", pady=5)
        scanner2_frame.pack_propagate(False)
        
        self.check_scanner2 = ctk.CTkCheckBox(
            scanner2_frame,
            text="Scanner 2 - Long Barcode (BCA prefix)",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT_PRIMARY,
            fg_color=BCA_BLUE,
            hover_color=BCA_DARK_BLUE,
            checkbox_width=22,
            checkbox_height=22,
        )
        self.check_scanner2.pack(side="left", padx=15, pady=12)
        if self.validation_settings.get("scanner2", False):
            self.check_scanner2.select()
        
        # Scanner 3
        scanner3_frame = ctk.CTkFrame(self.checkbox_frame, fg_color="#ffffff", corner_radius=8, height=50)
        scanner3_frame.pack(fill="x", pady=5)
        scanner3_frame.pack_propagate(False)
        
        self.check_scanner3 = ctk.CTkCheckBox(
            scanner3_frame,
            text="Scanner 3 - Numeric Code (10 digits)",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT_PRIMARY,
            fg_color=BCA_BLUE,
            hover_color=BCA_DARK_BLUE,
            checkbox_width=22,
            checkbox_height=22,
        )
        self.check_scanner3.pack(side="left", padx=15, pady=12)
        if self.validation_settings.get("scanner3", False):
            self.check_scanner3.select()
        
        # Info box
        info_frame = ctk.CTkFrame(main_frame, fg_color="#e3f2fd", corner_radius=8, border_width=1, border_color="#2196f3")
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Only selected scanners will be compared with database entries.\nUnchecked scanners will be ignored during validation.",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color="#01579b",
            justify="left"
        )
        info_label.pack(padx=15, pady=12)
        
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
            text="💾 Save Settings",
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
            'scanner1': self.check_scanner1.get(),
            'scanner2': self.check_scanner2.get(),
            'scanner3': self.check_scanner3.get(),
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
            border_width=2,
            border_color=BCA_BLUE,
        )

        # HEADER dengan Title dan Delete Button
        header = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=35,
        )
        header.pack(fill="x", padx=12, pady=(8, 5))
        header.pack_propagate(False)

        # Title
        self.title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=BCA_BLUE,
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        # Delete Button
        self.delete_btn = ctk.CTkButton(
            header,
            text="🗑️",
            width=32,
            height=32,
            font=ctk.CTkFont(size=16),
            fg_color="#ff4444",
            hover_color="#cc0000",
            corner_radius=6,
            command=self.clear,
        )
        self.delete_btn.pack(side="right")

        # ENTRY FIELD (READONLY)
        self.entry = ctk.CTkEntry(
            self,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=ENTRY_BG,
            border_width=2,
            border_color=ENTRY_BORDER,
            text_color=TEXT_PRIMARY,
            placeholder_text="",
            justify="left",
            state="readonly",
        )
        self.entry.pack(fill="x", padx=12, pady=(0, 10))

    def set_value(self, text: str):
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self.entry.configure(state="readonly")
    
    def get_value(self):
        """Get current value in entry"""
        return self.entry.get()

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

        # *** SESSION DATA LOGGING ***
        self.session_data = []  # Array untuk menyimpan semua scan
        self.session_start_time = None
        self.session_end_time = None

        # *** ANTI-DOUBLE SCAN MECHANISM ***
        self.last_scan_data = {
            "scanner1": "",
            "scanner2": "",
            "scanner3": ""
        }
        self.last_scan_time = {
            "scanner1": 0,
            "scanner2": 0,
            "scanner3": 0
        }
        self.DEBOUNCE_TIME = 2000  # 2 detik cooldown

        # *** Validation Settings ***
        self.validation_settings = {
            "scanner1": True,
            "scanner2": False,
            "scanner3": False,
        }

        # *** Database JSON ***
        self.database = []
        self._load_database()

        # Tracking scanner status
        self.scanner1_received = False
        self.scanner2_received = False
        self.scanner3_received = False
        self.scanner1_timeout_job = None
        self.SCANNER1_TIMEOUT = 5000

        # Current scan data
        self.current_scan_data = {
            "SCANER 1": None,
            "SCANER 2": None,
            "SCANER 3": None,
        }

        # ---------- EXIT BUTTON ----------
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<Control-q>", lambda e: self.on_close())

        # ---------- UI BUILD ----------
        self._build_header()
        self._build_scanners()
        self._build_control_panel()

        # ---------- SERIAL ----------
        self._connect_arduino()
        self._start_status_loop()

        # keybinding scanner
        self.bind_all("<Key>", self.on_key)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _load_database(self):
        """Load database dari file JSON"""
        db_file = "dummy.json"
        
        # Default data
        default_data = [
            {
                "SCANER 1": "BCA0210003500725",
                "SCANER 2": "BCA100000000000000003246",
                "SCANER 3": "1013800463"
            },
            {
                "SCANER 1": "BCA0210003550725",
                "SCANER 2": "BCA100000000000000003242",
                "SCANER 3": "0071848463"
            },
            {
                "SCANER 1": "BCA0210003500725",
                "SCANER 2": "BCA100000000000000003241",
                "SCANER 3": "3743345679"
            },
            {
                "SCANER 1": "BCA0210003530725",
                "SCANER 2": "BCA100000000000000003244",
                "SCANER 3": "0670520768"
            },
            {
                "SCANER 1": "BCAK210003490725",
                "SCANER 2": "BCA100000000000000003245",
                "SCANER 3": "3421724431"
            },
            {
                "SCANER 1": "BCA0210003480725",
                "SCANER 2": "BCA100000000000000003243",
                "SCANER 3": "0349232675"
            },
            {
                "SCANER 1": "BCA0210003550725",
                "SCANER 2": "BCA100000000000000003228",
                "SCANER 3": "2335274255"
            }
        ]
        
        if os.path.exists(db_file):
            try:
                with open(db_file, 'r') as f:
                    self.database = json.load(f)
                print(f"✓ Database loaded: {len(self.database)} entries")
            except Exception as e:
                print(f"❌ Error loading database: {e}")
                self.database = default_data
        else:
            self.database = default_data
            with open(db_file, 'w') as f:
                json.dump(self.database, f, indent=2)
            print(f"✓ Database created: {len(self.database)} entries")

    def _save_session_data(self):
        """Save session data to JSON file when STOP"""
        if not self.session_data:
            print("⚠ No session data to save")
            return
        
        # Generate filename dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_data_{timestamp}.json"
        
        # Prepare session metadata
        session_summary = {
            "session_info": {
                "start_time": self.session_start_time,
                "end_time": self.session_end_time,
                "total_items": len(self.session_data),
                "duration_seconds": (datetime.fromisoformat(self.session_end_time) - 
                                   datetime.fromisoformat(self.session_start_time)).total_seconds()
            },
            "scan_data": self.session_data
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_summary, f, indent=2, ensure_ascii=False)
            
            print("=" * 70)
            print("💾 SESSION DATA SAVED")
            print(f"📁 File: {filename}")
            print(f"📊 Total items: {len(self.session_data)}")
            print(f"⏱ Duration: {session_summary['session_info']['duration_seconds']:.2f}s")
            print("=" * 70)
            
            # Print preview data
            print("\n📋 DATA PREVIEW (First 3 items):")
            for i, item in enumerate(self.session_data[:3], 1):
                print(f"\nItem #{i} (ID: {item.get('item_id', 'N/A')}):")
                if 'scanner_1' in item:
                    print(f"  Scanner 1: {item['scanner_1']['value']} - Valid: {item['scanner_1']['valid']}")
                if 'scanner_2' in item:
                    print(f"  Scanner 2: {item['scanner_2']['value']} - Valid: {item['scanner_2']['valid']}")
                if 'scanner_3' in item:
                    print(f"  Scanner 3: {item['scanner_3']['value']} - Valid: {item['scanner_3']['valid']}")
                print(f"  Overall Result: {item.get('validation_result', 'N/A')}")
                print(f"  Timestamp: {item.get('timestamp', 'N/A')}")
            
            if len(self.session_data) > 3:
                print(f"\n... and {len(self.session_data) - 3} more items")
            
            print("\n" + "=" * 70)
            
            return filename
            
        except Exception as e:
            print(f"❌ Error saving session data: {e}")
            return None

    def _add_to_session(self, scan_data, validation_details, overall_result):
        """Add completed scan to session array with individual scanner validation"""
        session_entry = {
            "item_id": self.current_item_id,
            "timestamp": datetime.now().isoformat(),
            "validation_result": overall_result
        }
        
        # Add scanner data only if they were scanned
        if scan_data.get("SCANER 1"):
            session_entry["scanner_1"] = {
                "value": scan_data["SCANER 1"],
                "valid": validation_details["scanner_1"]
            }
        
        if scan_data.get("SCANER 2"):
            session_entry["scanner_2"] = {
                "value": scan_data["SCANER 2"],
                "valid": validation_details["scanner_2"]
            }
        
        if scan_data.get("SCANER 3"):
            session_entry["scanner_3"] = {
                "value": scan_data["SCANER 3"],
                "valid": validation_details["scanner_3"]
            }
        
        self.session_data.append(session_entry)
        
        print(f"📝 Session entry #{len(self.session_data)} added:")
        for key, value in session_entry.items():
            if key.startswith("scanner_"):
                print(f"   {key}: {value['value']} - Valid: {value['valid']}")
        print(f"   Overall Result: {overall_result}")

    def _is_duplicate_scan(self, scanner_name, code):
        """Cek apakah scan adalah duplikat (debouncing)"""
        current_time = int(time.time() * 1000)
        
        if self.last_scan_data[scanner_name] == code:
            time_diff = current_time - self.last_scan_time[scanner_name]
            if time_diff < self.DEBOUNCE_TIME:
                print(f"⚠ DUPLICATE SCAN BLOCKED - {scanner_name}: {code} (dalam {time_diff}ms)")
                return True
        
        self.last_scan_data[scanner_name] = code
        self.last_scan_time[scanner_name] = current_time
        return False

    def _validate_individual_scanner(self, scanner_key, scanner_value):
        """Validate individual scanner value against database"""
        if not scanner_value:
            return None  # Not scanned
        
        # Check if this value exists in database for this scanner
        for entry in self.database:
            if entry.get(scanner_key) == scanner_value:
                return True
        
        return False

    def _validate_scan_data(self):
        """Validasi data scan dengan database - individual scanner validation"""
        active_scanners = []
        if self.validation_settings["scanner1"]:
            active_scanners.append("SCANER 1")
        if self.validation_settings["scanner2"]:
            active_scanners.append("SCANER 2")
        if self.validation_settings["scanner3"]:
            active_scanners.append("SCANER 3")
        
        if not active_scanners:
            print("⚠ No scanners enabled for validation - AUTO PASS")
            validation_details = {
                "scanner_1": None,
                "scanner_2": None,
                "scanner_3": None
            }
            return True, "No validation enabled", validation_details
        
        # Check if all active scanners have data
        for scanner in active_scanners:
            if not self.current_scan_data[scanner]:
                print(f"⚠ {scanner} not scanned yet")
                return None, "Waiting for data", None
        
        print("=" * 60)
        print("🔍 VALIDATING AGAINST DATABASE (Individual Scanner Mode)")
        print(f"Active scanners: {', '.join(active_scanners)}")
        
        # Validate each scanner individually
        validation_details = {
            "scanner_1": None,
            "scanner_2": None,
            "scanner_3": None
        }
        
        # Validate Scanner 1
        if self.current_scan_data["SCANER 1"]:
            validation_details["scanner_1"] = self._validate_individual_scanner(
                "SCANER 1", 
                self.current_scan_data["SCANER 1"]
            )
            print(f"Scanner 1: {self.current_scan_data['SCANER 1']} - Valid: {validation_details['scanner_1']}")
        
        # Validate Scanner 2
        if self.current_scan_data["SCANER 2"]:
            validation_details["scanner_2"] = self._validate_individual_scanner(
                "SCANER 2", 
                self.current_scan_data["SCANER 2"]
            )
            print(f"Scanner 2: {self.current_scan_data['SCANER 2']} - Valid: {validation_details['scanner_2']}")
        
        # Validate Scanner 3
        if self.current_scan_data["SCANER 3"]:
            validation_details["scanner_3"] = self._validate_individual_scanner(
                "SCANER 3", 
                self.current_scan_data["SCANER 3"]
            )
            print(f"Scanner 3: {self.current_scan_data['SCANER 3']} - Valid: {validation_details['scanner_3']}")
        
        # Determine overall PASS/FAIL based on active scanners
        all_valid = True
        checked_count = 0
        
        if self.validation_settings["scanner1"] and validation_details["scanner_1"] is not None:
            checked_count += 1
            if not validation_details["scanner_1"]:
                all_valid = False
        
        if self.validation_settings["scanner2"] and validation_details["scanner_2"] is not None:
            checked_count += 1
            if not validation_details["scanner_2"]:
                all_valid = False
        
        if self.validation_settings["scanner3"] and validation_details["scanner_3"] is not None:
            checked_count += 1
            if not validation_details["scanner_3"]:
                all_valid = False
        
        if all_valid and checked_count > 0:
            print(f"✅ OVERALL: PASS - All {checked_count} active scanner(s) valid")
            print("=" * 60)
            return True, f"All {checked_count} scanner(s) valid", validation_details
        else:
            print(f"❌ OVERALL: FAIL - One or more scanners invalid")
            print("=" * 60)
            return False, "One or more scanners invalid", validation_details

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

        status_frame = ctk.CTkFrame(content, fg_color="transparent")
        status_frame.pack(side="right", fill="y")

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
        container.pack(fill="both", expand=True, padx=30, pady=(0, 8))

        self.scanner1 = ScannerCard(container, "SCANNER 1")
        self.scanner1.pack(fill="both", expand=True, pady=(0, 8))

        self.scanner2 = ScannerCard(container, "SCANNER 2")
        self.scanner2.pack(fill="both", expand=True, pady=(0, 8))

        self.scanner3 = ScannerCard(container, "SCANNER 3")
        self.scanner3.pack(fill="both", expand=True)

    def _build_control_panel(self):
        frame = ctk.CTkFrame(self, fg_color="transparent", height=55)
        frame.pack(fill="x", padx=30, pady=(5, 15))
        frame.pack_propagate(False)

        btn_container = ctk.CTkFrame(frame, fg_color="transparent")
        btn_container.pack(expand=True)

        self.btn_start = ctk.CTkButton(
            btn_container,
            text="START SYSTEM",
            fg_color="#0f9d58",
            hover_color="#0b7c45",
            height=40,
            width=160,
            font=self.font_big_bold,
            corner_radius=8,
            command=self.start_system,
        )
        self.btn_start.pack(side="left", padx=8)

        self.btn_stop = ctk.CTkButton(
            btn_container,
            text="STOP SYSTEM",
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            height=40,
            width=160,
            font=self.font_big_bold,
            corner_radius=8,
            command=self.stop_system,
            state="disabled",
        )
        self.btn_stop.pack(side="left", padx=8)

        self.btn_settings = ctk.CTkButton(
            btn_container,
            text="⚙️ SETTINGS",
            fg_color=BCA_BLUE,
            hover_color=BCA_DARK_BLUE,
            height=40,
            width=140,
            font=self.font_big_bold,
            corner_radius=8,
            command=self.open_settings,
        )
        self.btn_settings.pack(side="left", padx=8)

    # ================== SETTINGS ==================

    def open_settings(self):
        """Open settings dialog"""
        was_override = self.overrideredirect()
        was_fullscreen = self.attributes('-fullscreen')
        
        if was_fullscreen:
            self.attributes('-fullscreen', False)
        if was_override:
            self.overrideredirect(False)
        
        self.withdraw()
        self.update_idletasks()
        self.update()
        time.sleep(0.1)
        
        dialog = SettingsDialog(self, self.validation_settings)
        self.wait_window(dialog)
        
        self.deiconify()
        
        if was_override:
            self.overrideredirect(True)
        if was_fullscreen:
            self.attributes('-fullscreen', True)
        
        self.lift()
        self.focus_force()
        
        if dialog.result:
            self.validation_settings = dialog.result
            print("=" * 60)
            print("⚙️ VALIDATION SETTINGS UPDATED")
            print(f"Scanner 1: {'✓ ENABLED' if self.validation_settings['scanner1'] else '✗ DISABLED'}")
            print(f"Scanner 2: {'✓ ENABLED' if self.validation_settings['scanner2'] else '✗ DISABLED'}")
            print(f"Scanner 3: {'✓ ENABLED' if self.validation_settings['scanner3'] else '✗ DISABLED'}")
            print("=" * 60)

    # ================== SERIAL ==================

    def _connect_to_port(self, port_name):
        try:
            if self.arduino and self.arduino.is_open:
                self.arduino.close()
                
            self.arduino = serial.Serial(port_name, 9600, timeout=1)
            time.sleep(2)
            
            self.arduino_status_indicator.configure(text_color="#4caf50")
            self.arduino_port_label.configure(text=port_name)
            
            print(f"✓ Connected to Arduino on {port_name}")
            
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
                
        print("⚠ No Arduino found")
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

        if line.startswith("RESULT:PASS:"):
            item_id = line.split(":")[-1]
            print(f"🟢 Arduino PASS - ID: {item_id}")
            
        elif line.startswith("RESULT:FAIL:"):
            item_id = line.split(":")[-1]
            print(f"🔴 Arduino FAIL - ID: {item_id}")

    def _show_result_notification(self, is_pass: bool):
        if is_pass:
            self.scanner1.configure(border_color="#4caf50")
            self.scanner2.configure(border_color="#4caf50")
            self.scanner3.configure(border_color="#4caf50")
            self.after(2000, lambda: self.scanner1.configure(border_color=ENTRY_BORDER))
            self.after(2000, lambda: self.scanner2.configure(border_color=ENTRY_BORDER))
            self.after(2000, lambda: self.scanner3.configure(border_color=ENTRY_BORDER))
        else:
            self.scanner1.configure(border_color="#ff4444")
            self.scanner2.configure(border_color="#ff4444")
            self.scanner3.configure(border_color="#ff4444")
            self.after(2000, lambda: self.scanner1.configure(border_color=ENTRY_BORDER))
            self.after(2000, lambda: self.scanner2.configure(border_color=ENTRY_BORDER))
            self.after(2000, lambda: self.scanner3.configure(border_color=ENTRY_BORDER))

    def _send_cmd(self, cmd: str):
        if self.arduino and self.arduino.is_open:
            full_cmd = cmd + "\n"
            self.arduino.write(full_cmd.encode("utf-8"))
            self.arduino.flush()
            print(f">> SENT: '{cmd}'")
        else:
            print("❌ Arduino belum terhubung")

    def _start_status_loop(self):
        if self.arduino and self.arduino.is_open:
            self._send_cmd("status")
        self.after(3000, self._start_status_loop)

    # ================== START / STOP ==================

    def start_system(self):
        if not self.arduino or not self.arduino.is_open:
          print("Tidak bisa START - Arduino belum terhubung!")
          return
    
    # ========== API CALL START ==========
        try:
            # Ambil scanner_used dari settings yang dicentang
            scanner_used = []
            if self.validation_settings.get('scanner1', False):
                scanner_used.append(1)
            if self.validation_settings.get('scanner2', False):
                scanner_used.append(2)
            if self.validation_settings.get('scanner3', False):
                scanner_used.append(3)
            
            # Generate dummy batch_code
            import random
            batch_code = f"BCA-2025{int(time.time() * 1000) % 1000000:06d}"
            
            payload = {
                "scanner_used": scanner_used,
                "batch_code": batch_code
            }
            
            response = requests.post(
                f"http://127.0.0.1:8000/batch/start",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                self.batch_record_id = result.get('id')  # Asumsi API return {'id': 123}
                print(f"✅ BATCH START SUCCESS - Record ID: {self.batch_record_id}")
                print(f"   Scanner used: {scanner_used}")
                print(f"   Batch code: {batch_code}")
            else:
                print(f"❌ BATCH START FAILED - {response.status_code}: {response.text}")
                return  # Stop jika API gagal
            
        except Exception as e:
            print(f"❌ API START ERROR: {e}")
            return
        
        # ========== Lanjutkan logic START asli ==========
        self.systemrunning = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.system_status_indicator.configure(textcolor="4caf50")
        self.system_status_label.configure(text="RUNNING")
        self.sessionstarttime = datetime.now().isoformat()
        
        # Reset session data
        self.sessiondata = []
        self.send_cmd("start")
        
        print("60")
        print("SYSTEM STARTED")
        print(f"Session started: {self.sessionstarttime}")
        print(f"Batch Record ID: {self.batch_record_id}")
        print("60")

    def stop_system(self):
        if not self.batch_record_id:
            print("❌ No batch record ID - START dulu!")
            return
    
    # ========== API CALL FINISH ==========
        try:
            # Format data sesuai struktur yang diminta
            finish_data = []
            for item in self.sessiondata:
                item_entry = {
                    "item_id": item.get("itemid"),
                }
                
                # Scanner 1
                if "scanner1" in item:
                    item_entry["scanner_1"] = {
                        "value": item["scanner1"]["value"],
                        "valid": item["scanner1"]["valid"]
                    }
                
                # Scanner 2  
                if "scanner2" in item:
                    item_entry["scanner_2"] = {
                        "value": item["scanner2"]["value"],
                        "valid": item["scanner2"]["valid"]
                    }
                
                # Scanner 3
                if "scanner3" in item:
                    item_entry["scanner_3"] = {
                        "value": item["scanner3"]["value"],
                        "valid": item["scanner3"]["valid"]
                    }
                
                finish_data.append(item_entry)
            
            response = requests.post(
                f"http://127.0.0.1:8000/batch/{self.batch_record_id}/finish",
                json=finish_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ BATCH FINISH SUCCESS - Record ID: {self.batch_record_id}")
                print(f"   Total items: {len(finish_data)}")
                print("   Data sent:", json.dumps(finish_data[:2], indent=2))  # Preview 2 items
            else:
                print(f"❌ BATCH FINISH FAILED - {response.status_code}: {response.text}")
            
            # Save local file juga
            savedfile = self.savesessiondata()
            if savedfile:
                print(f"   Local backup: {savedfile}")
                
        except Exception as e:
            print(f"❌ API FINISH ERROR: {e}")
        
        # ========== Reset semua state ==========
        self.systemrunning = False
        self.batch_record_id = None
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.system_status_indicator.configure(textcolor="#ff4444")
        self.system_status_label.configure(text="FINISHED")
        
        self.sessionendtime = datetime.now().isoformat()
        print("60")
        print("SYSTEM FINISHED")
        print(f"Session ended: {self.sessionendtime}")
        print("60")
        
        self.scanner1.clear()
        self.scanner2.clear()
        self.scanner3.clear()
        self.currentitemid = None
        self.reset_scanner_tracking()
        self.send_cmd("reset")

    # ================== SCANNER TRACKING ==================

    def _reset_scanner_tracking(self):
        self.scanner1_received = False
        self.scanner2_received = False
        self.scanner3_received = False
        
        self.current_scan_data = {
            "SCANER 1": None,
            "SCANER 2": None,
            "SCANER 3": None,
        }
        
        self.last_scan_data = {
            "scanner1": "",
            "scanner2": "",
            "scanner3": ""
        }
        self.last_scan_time = {
            "scanner1": 0,
            "scanner2": 0,
            "scanner3": 0
        }
        
        if self.scanner1_timeout_job:
            self.after_cancel(self.scanner1_timeout_job)
            self.scanner1_timeout_job = None

    def _check_validation_complete(self):
        """Cek apakah semua scanner yang aktif sudah terisi"""
        self.after(500, self._perform_validation)

    def _perform_validation(self):
        """Lakukan validasi terhadap database"""
        is_valid, message, validation_details = self._validate_scan_data()
        
        if is_valid is None:
            return
        
        if not self.current_item_id:
            self.current_item_id = int(time.time() * 1000) % 100000
        
        # Determine result string
        validation_result = "PASS" if is_valid else "FAIL"
        
        # *** ADD TO SESSION DATA WITH INDIVIDUAL SCANNER VALIDATION ***
        self._add_to_session(self.current_scan_data.copy(), validation_details, validation_result)
        
        if is_valid:
            print(f"🟢 VALIDATION RESULT: PASS - {message}")
            self._send_cmd("test_pass")
            self._show_result_notification(True)
        else:
            print(f"🔴 VALIDATION RESULT: FAIL - {message}")
            self._send_cmd("test_fail")
            self._show_result_notification(False)
        
        # Reset untuk item berikutnya
        self._reset_current_item()

    def _reset_current_item(self):
        """Reset current item setelah validasi selesai"""
        self.scanner1.clear()
        self.scanner2.clear()
        self.scanner3.clear()
        
        self.scanner1_received = False
        self.scanner2_received = False
        self.scanner3_received = False
        
        self.current_scan_data = {
            "SCANER 1": None,
            "SCANER 2": None,
            "SCANER 3": None,
        }

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
        code = code.strip()
        
        if len(code) == 16:
            return "scanner1"
        
        if len(code) > 16 and code.startswith("BCA"):
            return "scanner2"
        
        if len(code) == 10 and code.isdigit():
            return "scanner3"
        
        return "unknown"

    def _process_buffer(self):
        code = self.buffer.strip()
        if not code:
            return

        scanner = self._identify_scanner(code)

        if scanner == "scanner1":
            if self._is_duplicate_scan("scanner1", code):
                return
            
            current_value = self.scanner1.get_value()
            if current_value and current_value != "":
                print(f"⚠ Scanner 1 sudah terisi: {current_value} - Scan diabaikan")
                return
            
            self.scanner1_received = True
            self.scanner1.set_value(code)
            self.current_scan_data["SCANER 1"] = code
            
            if not self.current_item_id:
                self.current_item_id = int(time.time() * 1000) % 100000
            
            self._send_cmd(f"SCAN1:{self.current_item_id}:{code}")
            print(f"✓ Scanner 1: {code}")
            
            self._check_validation_complete()
                
        elif scanner == "scanner2":
            if self._is_duplicate_scan("scanner2", code):
                return
            
            current_value = self.scanner2.get_value()
            if current_value and current_value != "":
                print(f"⚠ Scanner 2 sudah terisi: {current_value} - Scan diabaikan")
                return
            
            self.scanner2_received = True
            self.scanner2.set_value(code)
            self.current_scan_data["SCANER 2"] = code
            
            if not self.current_item_id:
                self.current_item_id = int(time.time() * 1000) % 100000
            
            self._send_cmd(f"SCAN2:{self.current_item_id}:{code}")
            print(f"✓ Scanner 2: {code}")
            
            self._check_validation_complete()
                
        elif scanner == "scanner3":
            if self._is_duplicate_scan("scanner3", code):
                return
            
            current_value = self.scanner3.get_value()
            if current_value and current_value != "":
                print(f"⚠ Scanner 3 sudah terisi: {current_value} - Scan diabaikan")
                return
            
            self.scanner3_received = True
            self.scanner3.set_value(code)
            self.current_scan_data["SCANER 3"] = code
            
            if not self.current_item_id:
                self.current_item_id = int(time.time() * 1000) % 100000
            
            self._send_cmd(f"SCAN3:{self.current_item_id}:{code}")
            print(f"✓ Scanner 3: {code}")
            
            self._check_validation_complete()
        else:
            print(f"❌ Format tidak dikenali: {code}")

    # ================== CLOSE ==================

    def on_close(self):
        if self.arduino and self.arduino.is_open:
            self._send_cmd("reset")
            time.sleep(0.5)
            self.arduino.close()
        self.destroy()


# ==================== MAIN ====================

if __name__ == "__main__":
    app = App()
    app.mainloop()