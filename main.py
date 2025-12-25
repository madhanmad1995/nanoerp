"""
main.py - Main entry point for Nano ERP System
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import UI modules
from ui.main_window import MainWindow
from database import init_db

def main():
    """Main entry point"""
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        
        # Create main application window
        print("Starting Nano ERP...")
        root = tk.Tk()
        app = MainWindow(root)
        
        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()