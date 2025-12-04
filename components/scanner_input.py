# components/scanner_input.py
import os
import customtkinter as ctk
from PIL import Image

class ScannerInput(ctk.CTkFrame):
    def __init__(self, master, title, titleFont, inputFont, buttonFont=None, **kwargs):
        super().__init__(master, fg_color="white", **kwargs)

        # TITLE
        self.titleFrame = ctk.CTkFrame(self, fg_color="white")
        self.titleFrame.pack(fill="x")

        trash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img", "trash.png")
        trash_icon = ctk.CTkImage(Image.open(trash_path), size=(20, 20))

        self.label = ctk.CTkLabel(self.titleFrame, text=title, text_color="#003399", font=titleFont)
        self.label.pack(pady=5, padx=(35, 5), side="left")

        self.clear_input = ctk.CTkButton(self.titleFrame, text="", width=10, height=10,
                                         fg_color="white", hover=False, cursor="hand2",
                                         image=trash_icon, command=self.clear)
        self.clear_input.pack(padx=20, pady=5, side="left")

        # INPUT
        self.inputFrame = ctk.CTkFrame(self, fg_color="white")
        self.inputFrame.pack(fill="x", pady=5)

        self.entry = ctk.CTkEntry(self.inputFrame, font=inputFont, fg_color="white",
                                  text_color="#003399", corner_radius=25, height=74,
                                  border_width=3, border_color="#003399")
        self.entry.pack(fill="x", pady=5, padx=5, side="left", expand=True)

    def clear(self):
        self.entry.delete(0, ctk.END)

    def insert(self, index, code):
        self.entry.insert(index, code)