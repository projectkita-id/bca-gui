import os
import time
import json
from datetime import datetime

import customtkinter as ctk
from PIL import Image


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

        self.title("Settings - Scanner Validation")
        self.geometry("600x400")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.transient(parent)

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

    def on_close(self):
        self.result = {
            "scanner1": self.check_scanner1.get(),
            "scanner2": self.check_scanner2.get(),
            "scanner3": self.check_scanner3.get(),
        }
        self.destroy()

    def _finish_init(self):
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            main_frame,
            text="⚙️ Scanner Validation Settings",
            font=ctk.CTkFont("Segoe UI", 20, "bold"),
            text_color=BCA_BLUE
        )
        title.pack(pady=(0, 10))

        desc = ctk.CTkLabel(
            main_frame,
            text="Demo Mode - Scanner Configuration",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=TEXT_SECONDARY,
            justify="center"
        )
        desc.pack(pady=(0, 20))

        checkbox_container = ctk.CTkFrame(main_frame, fg_color=CARD_BG, corner_radius=12)
        checkbox_container.pack(fill="x", pady=(0, 15))

        header_label = ctk.CTkLabel(
            checkbox_container,
            text="📋 Select Scanners for Validation",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=BCA_BLUE
        )
        header_label.pack(pady=(15, 10))

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

        info_frame = ctk.CTkFrame(main_frame, fg_color="#e3f2fd", corner_radius=8, border_width=1, border_color="#2196f3")
        info_frame.pack(fill="x", pady=(0, 15))

        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Demo Mode - Configuration saved locally",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color="#01579b",
            justify="left"
        )
        info_label.pack(padx=15, pady=12)

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

        header = ctk.CTkFrame(self, fg_color="transparent", height=35)
        header.pack(fill="x", padx=12, pady=(8, 5))
        header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=BCA_BLUE,
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True)

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
        return self.entry.get()

    def clear(self):
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.configure(state="readonly")


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG_MAIN)

        self.title("Envelope Sorting System")

        # FULLSCREEN KIOSK MODE
        self.attributes('-fullscreen', True)
        self.overrideredirect(True)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        self.font_big_bold = ctk.CTkFont("Segoe UI", 16, "bold")
        self.font_med = ctk.CTkFont("Segoe UI", 12)
        self.font_med_bold = ctk.CTkFont("Segoe UI", 12, "bold")

        self.system_running = False
        self.current_item_id = None
        self.current_item = None

        self.session_data = []
        self.session_start_time = None
        self.session_end_time = None

        # Demo samples sesuai gambar
        self.demo_samples = [
            {
                "scanner1": "BCA0210003500725",
                "scanner2": "BCA100000000000000003242",
                "scanner3": "1013800463",
                "result": "Fail"
            },
            {
                "scanner1": "BCA0210003550725",
                "scanner2": "BCA100000000000000003228",
                "scanner3": "2335274255",
                "result": "Pass"
            }
        ]

        self.validation_settings = {"scanner1": True, "scanner2": True, "scanner3": True}

        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<Control-q>", lambda e: self.on_close())

        self._build_header()
        self._build_scanners()
        self._build_control_panel()

        self.bind_all("<Key>", self.on_key)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        print("=" * 60)
        print("✅ Demo Mode Started")
        print("=" * 60)

    def _start_new_item(self):
        item_id = int(time.time() * 1000) % 100000
        self.current_item = {
            "item_id": item_id,
            "timestamp": datetime.now().isoformat(),
            "scanner_1": None,
            "scanner_2": None,
            "scanner_3": None,
            "result": None
        }
        self.current_item_id = item_id
        print(f"🆕 NEW ITEM - ID: {item_id}")

    def _commit_current_item(self):
        if not self.current_item:
            return
        self.session_data.append(self.current_item)
        print(f"📦 SAVED - ID: {self.current_item['item_id']}")
        self.current_item = None
        self.current_item_id = None

    def _save_session_data(self):
        if not self.session_data:
            print("⚠ No data")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.json"

        output = {
            "session_start": self.session_start_time.isoformat(),
            "session_end": self.session_end_time.isoformat(),
            "total_items": len(self.session_data),
            "data": self.session_data
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"💾 SAVED: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def exit_fullscreen(self, event=None):
        if self.attributes('-fullscreen'):
            self.attributes('-fullscreen', False)
            self.overrideredirect(False)
            self.geometry("1024x600")
        else:
            self.attributes('-fullscreen', True)
            self.overrideredirect(True)

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

        # Demo Mode indicator
        demo_container = ctk.CTkFrame(
            status_frame,
            fg_color="#f0f0f0",
            corner_radius=8,
            border_width=2,
            border_color="#cccccc",
        )
        demo_container.pack(pady=(0, 6))

        demo_inner = ctk.CTkFrame(demo_container, fg_color="transparent")
        demo_inner.pack(padx=10, pady=6)

        demo_indicator = ctk.CTkLabel(
            demo_inner,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color="#4caf50",
            width=25,
        )
        demo_indicator.pack(side="left", padx=(0, 6))

        demo_text_frame = ctk.CTkFrame(demo_inner, fg_color="transparent")
        demo_text_frame.pack(side="left")

        ctk.CTkLabel(
            demo_text_frame,
            text="Demo Mode",
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            demo_text_frame,
            text="Keyboard Input",
            font=ctk.CTkFont("Segoe UI", 8),
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(anchor="w")

        # System status
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

    def open_settings(self):
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
            print("⚙️ Settings saved")

    def _load_demo_sample(self, index):
        if index >= len(self.demo_samples):
            return

        sample = self.demo_samples[index]

        self.scanner1.clear()
        self.scanner2.clear()
        self.scanner3.clear()

        self._start_new_item()

        self.scanner1.set_value(sample["scanner1"])
        self.current_item["scanner_1"] = sample["scanner1"]
        print(f"✓ Scanner 1: {sample['scanner1']}")

        self.after(500, lambda: self._fill_scanner2(sample))

    def _fill_scanner2(self, sample):
        self.scanner2.set_value(sample["scanner2"])
        self.current_item["scanner_2"] = sample["scanner2"]
        print(f"✓ Scanner 2: {sample['scanner2']}")

        self.after(500, lambda: self._fill_scanner3(sample))

    def _fill_scanner3(self, sample):
        self.scanner3.set_value(sample["scanner3"])
        self.current_item["scanner_3"] = sample["scanner3"]
        print(f"✓ Scanner 3: {sample['scanner3']}")

        self.after(500, lambda: self._validate_and_show(sample))

    def _validate_and_show(self, sample):
        result = sample["result"]
        self.current_item["result"] = result

        is_pass = result.lower() == "pass"

        if is_pass:
            self.scanner1.configure(border_color="#4caf50")
            self.scanner2.configure(border_color="#4caf50")
            self.scanner3.configure(border_color="#4caf50")
            print("✅ PASS")
        else:
            self.scanner1.configure(border_color="#ff4444")
            self.scanner2.configure(border_color="#ff4444")
            self.scanner3.configure(border_color="#ff4444")
            print("❌ FAIL")

        self._commit_current_item()
        self.after(2000, self._reset_ui)

    def _reset_ui(self):
        self.scanner1.configure(border_color=ENTRY_BORDER)
        self.scanner2.configure(border_color=ENTRY_BORDER)
        self.scanner3.configure(border_color=ENTRY_BORDER)

        self.scanner1.clear()
        self.scanner2.clear()
        self.scanner3.clear()

        print("=" * 60)
        print("🔄 READY - Press 1 (FAIL) or 2 (PASS)")
        print("=" * 60)

    def start_system(self):
        self.system_running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.system_status_indicator.configure(text_color="#4caf50")
        self.system_status_label.configure(text="RUNNING")
        self.session_start_time = datetime.now()
        self.session_data = []

        print("=" * 60)
        print("🚀 STARTED")
        print("Press '1' = FAIL | '2' = PASS")
        print("=" * 60)

    def stop_system(self):
        self.session_end_time = datetime.now()

        if self.current_item:
            self._commit_current_item()

        self._save_session_data()

        self.system_running = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.system_status_indicator.configure(text_color="#ff4444")
        self.system_status_label.configure(text="STOPPED")

        print("=" * 60)
        print(f"🛑 STOPPED - {len(self.session_data)} items")
        print("=" * 60)

        self.scanner1.clear()
        self.scanner2.clear()
        self.scanner3.clear()

    def on_key(self, event):
        if not self.system_running:
            return

        key = event.char

        if key in ['1', '2']:
            index = int(key) - 1
            print(f"\n🔢 Selection: {key}")
            self._load_demo_sample(index)

    def on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
