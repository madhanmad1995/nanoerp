"""
test_reports.py - Test the reports module
"""
import tkinter as tk
from ui.reports import Reports

def test_reports():
    root = tk.Tk()
    root.title("Test Reports Module")
    root.geometry("1200x700")
    
    reports = Reports(root)
    reports.pack(fill=tk.BOTH, expand=True)
    
    # Test one report
    reports.after(1000, reports.generate_sales_report)
    
    root.mainloop()

if __name__ == "__main__":
    test_reports()