import os
import customtkinter as ctk

from PIL import Image, ImageTk
from components.scanner_input import ScannerInput
from components.error_dialog import ErrorDialog as errorDialog

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="white")

        # ROOT CONFIG
        self.title("Envelope Sorting System")
        self.geometry("1024x600")

        # APP LOGO
        self.logo = ImageTk.PhotoImage(file="assets/img/logo.ico")
        self.iconbitmap("assets/img/logo.ico")

        # FONT
        self.montserrat = ctk.CTkFont(family="Montserrat", size=14)
        self.montserrat_bold = ctk.CTkFont(family="Montserrat", size=14, weight="bold")
        self.montserrat_medium = ctk.CTkFont(family="Montserrat", size=16)
        self.montserrat_medium_bold = ctk.CTkFont(family="Montserrat", size=16, weight="bold")
        self.montserrat_big = ctk.CTkFont(family="Montserrat", size=20)
        self.montserrat_big_bold = ctk.CTkFont(family="Montserrat", size=20, weight="bold")
        self.montserrat_xl = ctk.CTkFont(family="Montserrat", size=24)
        self.montserrat_xl_bold = ctk.CTkFont(family="Montserrat", size=24, weight="bold")

        # SCANNER BUFFER
        self.buffer = ""
        self.bind_all("<Key>", self.on_key)

        # APP TITLE
        logoPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "img", "logo.png")
        logoImage = ctk.CTkImage(Image.open(logoPath), size=(164, 54))
        self.label = ctk.CTkLabel(self, text="", image=logoImage, font=self.montserrat_big_bold)
        self.label.pack(pady=20)

        # SCANNER INPUTS
        self.scanner1 = ScannerInput(self, "SCANNER 1", self.montserrat_xl_bold, self.montserrat_medium, self.montserrat_medium_bold)
        self.scanner1.pack(fill="x", padx=50, pady=(5, 20))

        self.scanner2 = ScannerInput(self, "SCANNER 2", self.montserrat_xl_bold, self.montserrat_medium, self.montserrat_medium_bold)
        self.scanner2.pack(fill="x", padx=50, pady=(0, 20))

        self.scanner3 = ScannerInput(self, "SCANNER 3", self.montserrat_xl_bold, self.montserrat_medium, self.montserrat_medium_bold)
        self.scanner3.pack(fill="x", padx=50, pady=(0, 5))

    def on_key(self, event):
        char = event.char
        if event.keysym == "Return":
            self.buffer_proc()
            self.buffer = ""
            return
        
        if char.isprintable():
            self.buffer += char

    def identify(self, code: str) -> str:
        code = code.strip()

        if code.isdigit() and len(code) == 10:
            print("[SCANNER 1] ", code)
            return "scanner_1"
        
        if code.startswith("BCA0") and len(code) == 16:
            print("[SCANNER 2] ", code)
            return "scanner_2"
        
        if code.startswith("BCA1") and len(code) == 24:
            print("[SCANNER 3] ", code)
            return "scanner_3"
        
        return "unknown_scanner"
    
    def buffer_proc(self):
        code = self.buffer.strip()
        if not code:
            return
        
        scanner = self.identify(code)

        if scanner == "scanner_1":
            if self.scanner1.entry.get().strip() != "":
                return
            self.scanner1.insert(0, code)
        elif scanner == "scanner_2":
            if self.scanner2.entry.get().strip() != "":
                return
            self.scanner2.insert(0, code)
        elif scanner == "scanner_3":
            if self.scanner3.entry.get().strip() != "":
                return
            self.scanner3.insert(0, code)
        else:
            print("Unknown scanner code:", code)
            errorDialog(f"Unknown scanner code:\n{code}")

if __name__ == "__main__":
    app = App()
    app.mainloop()