import customtkinter as ctk
from tkinter import ttk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("House Rental Listings")
        self.geometry("600x800")

        self.canvas = ctk.CTkCanvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.load_postings()

        self.canvas.bind("<Configure>", self.on_scroll)

    def load_postings(self):
        # Load your postings here
        for i in range(20):  # Example: Load 20 postings at a time
            label = ctk.CTkLabel(self.scrollable_frame, text=f"Posting {i+1}")
            label.pack()

    def on_scroll(self, event):
        if self.canvas.yview()[1] >= 0.9:  # If scrolled near the bottom
            self.load_postings()

if __name__ == "__main__":
    app = App()
    app.mainloop()
