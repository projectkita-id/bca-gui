import customtkinter as ctk

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, message: str):
        super().__init__()
        self.title("Error")
        self.geometry("300x150")
        
        label = ctk.CTkLabel(self, text=message, text_color="red")
        label.pack(pady=20)
        
        button = ctk.CTkButton(self, text="Close", command=self.destroy)
        button.pack(pady=10)

        self.grab_set()