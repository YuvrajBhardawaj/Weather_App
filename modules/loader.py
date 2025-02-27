import tkinter as tk
from tkinter import ttk

class Loader:
    def __init__(self, root):
        self.root = root
        self.overlay = tk.Frame(root, bg="white")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Lift the overlay to ensure it appears on top of other widgets
        self.overlay.lift()

        # Center container for the loader
        self.loader_frame = tk.Frame(self.overlay, bg="white", padx=20, pady=20,border=2)
        self.loader_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.loading_label = tk.Label(self.loader_frame, text="Fetching Data...", font=("Arial", 14), bg="white")
        self.loading_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.loader_frame, mode="indeterminate", length=200)
        self.progress.pack(pady=5)

        self.overlay.place_forget()  # Initially hidden

    def show(self):
        """Show the loading overlay and bring it to the front."""
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()  # Ensure the overlay is above all other widgets
        self.progress.start()

    def hide(self):
        """Hide the loading overlay."""
        self.progress.stop()
        self.overlay.place_forget()