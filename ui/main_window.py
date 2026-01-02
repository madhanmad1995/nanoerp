"""
ui/main_window.py - Main application window
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Nano ERP - Business Management System")
        # Start with maximized window
        self.root.state('zoomed')  # Use 'zoomed' for Windows/Linux
        self.root.geometry("1200x700")
        
        # Set minimum size
        self.root.minsize(1000, 600)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)

        # Configure column weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create styles
        self.create_styles()
        
        # Create widgets
        self.create_widgets()
        
        # Initialize frames dictionary
        self.frames = {}
        self.current_frame = None
        
        # Show dashboard by default
        self.show_dashboard()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bind F11 for fullscreen toggle
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.fullscreen_state = False
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.fullscreen_state = False
        self.root.attributes("-fullscreen", False)
        return "break"
    

    
    def create_styles(self):
        """Create custom styles for the application"""
        style = ttk.Style()
        
        # Configure colors
        style.configure('Primary.TButton', font=('Segoe UI', 10))
        style.configure('Secondary.TButton', font=('Segoe UI', 9))
        # Consistent title styles
        style.configure('PageTitle.TLabel', font=('Segoe UI', 16, 'bold'))  # For page titles
        style.configure('SectionTitle.TLabel', font=('Segoe UI', 14, 'bold'))  # For section titles
        
        # Configure treeview
        style.configure('Treeview', font=('Segoe UI', 9))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        
        # Configure notebook
        style.configure('TNotebook.Tab', font=('Segoe UI', 10))
    
    def create_widgets(self):
        """Create main application widgets"""
        # Create header
        self.create_header()
        
        # Create main container with sidebar and content
        main_container = ttk.Frame(self.root)
        main_container.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Configure grid
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar(main_container)
        
        # Create content area
        self.content_frame = ttk.Frame(main_container, relief=tk.RAISED, borderwidth=1)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create application header"""
        header = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Logo and title
        logo_frame = ttk.Frame(header)
        logo_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Logo icon
        logo_label = ttk.Label(logo_frame, text="🏢", font=('Segoe UI', 24))
        logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title
        title_frame = ttk.Frame(logo_frame)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="Nano ERP", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(title_frame, text="Business Management System", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        # User info on the right
        user_frame = ttk.Frame(header)
        user_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        ttk.Label(user_frame, text="👤 Admin", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_frame, text="Logout", width=8, command=self.on_logout).pack(side=tk.LEFT, padx=5)
    
    def on_logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
    
    def create_sidebar(self, parent):
        """Create sidebar with navigation"""
        sidebar = ttk.Frame(parent, width=220, relief=tk.RAISED, borderwidth=1)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Navigation title
        ttk.Label(sidebar, text="Navigation", font=('Segoe UI', 12, 'bold'), 
                 padding=(10, 10, 10, 5)).pack(fill=tk.X)
        
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(sidebar)
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Navigation buttons with icons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📝 Invoices", self.show_invoices),
            ("👥 Customers", self.show_customers),
            ("🛒 Products", self.show_products),
            ("💰 Expenses", self.show_expenses),
            ("📈 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings),
            ("🆘 Help", self.show_help),
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(nav_frame, text=text, command=command, 
                           style='Secondary.TButton', width=20)
            btn.pack(pady=3, anchor=tk.W)
        
        # Quick stats section
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        
        stats_frame = ttk.LabelFrame(sidebar, text="Quick Stats", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.sidebar_stats = {
            "Today's Sales": tk.StringVar(value="₹0.00"),
            "Pending Invoices": tk.StringVar(value="0"),
            "New Customers": tk.StringVar(value="0"),
            "Low Stock": tk.StringVar(value="0"),
        }
        
        for label, var in self.sidebar_stats.items():
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.pack(fill=tk.X, pady=2)
            ttk.Label(stat_frame, text=label, font=('Segoe UI', 9)).pack(side=tk.LEFT)
            ttk.Label(stat_frame, textvariable=var, font=('Segoe UI', 9, 'bold')).pack(side=tk.RIGHT)
        
        # Refresh button
        ttk.Button(sidebar, text="🔄 Refresh Stats", 
                  command=self.update_sidebar_stats).pack(pady=10, padx=10, fill=tk.X)
    
    def create_status_bar(self):
        """Create status bar at the bottom"""
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        
        # Status messages
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_bar, textvariable=self.status_var, font=('Segoe UI', 9)).pack(
            side=tk.LEFT, padx=10)
        
        # Database status
        try:
            from database import db
            db_status = "Connected" if db.connection else "Disconnected"
        except ImportError:
            db_status = "Disconnected"
            
        ttk.Label(status_bar, text=f"Database: {db_status}", font=('Segoe UI', 9)).pack(
            side=tk.RIGHT, padx=10)
        
        # Version info
        ttk.Label(status_bar, text="v1.0.0", font=('Segoe UI', 9)).pack(side=tk.RIGHT, padx=10)
    
    def update_sidebar_stats(self):
        """Update sidebar statistics"""
        try:
            from database import db
            from datetime import date
            
            # Today's sales
            row = db.fetch_one('''
                SELECT SUM(total) as total FROM invoices 
                WHERE date = ? AND status != 'cancelled'
            ''', (date.today().strftime("%Y-%m-%d"),))
            self.sidebar_stats["Today's Sales"].set(f"₹{row['total'] or 0:.2f}")
            
            # Pending invoices
            row = db.fetch_one('SELECT COUNT(*) as count FROM invoices WHERE status="pending"')
            self.sidebar_stats["Pending Invoices"].set(row['count'])
            
            # New customers (last 7 days)
            row = db.fetch_one('''
                SELECT COUNT(*) as count FROM customers 
                WHERE DATE(created_at) >= DATE('now', '-7 days')
            ''')
            self.sidebar_stats["New Customers"].set(row['count'])
            
            # Low stock (less than 10)
            row = db.fetch_one('''
                SELECT COUNT(*) as count FROM products 
                WHERE stock < 10 AND stock > 0 AND is_service = 0
            ''')
            self.sidebar_stats["Low Stock"].set(row['count'])
            
            self.set_status("Stats updated")
            
        except Exception as e:
            self.set_status(f"Error updating stats: {e}", error=True)
    
    def set_status(self, message, error=False):
        """Set status bar message"""
        self.status_var.set(message)
        if error:
            self.root.after(5000, lambda: self.status_var.set("Ready"))
    
    def show_frame(self, frame_class, frame_name, *args, **kwargs):
        """Show a specific frame in the content area"""
        # Hide current frame
        if self.current_frame:
            self.current_frame.grid_forget()
        
        # Create or show the requested frame
        if frame_name not in self.frames:
            try:
                # Try to create the frame
                if frame_class == "Dashboard":
                    from ui.dashboard import Dashboard
                    self.frames[frame_name] = Dashboard(self.content_frame, app=self)
                elif frame_class == "Invoices":
                    from ui.invoices import Invoices
                    self.frames[frame_name] = Invoices(self.content_frame)
                elif frame_class == "Customers":
                    from ui.customers import Customers
                    self.frames[frame_name] = Customers(self.content_frame, app=self)
                elif frame_class == "Products":
                    from ui.products import Products
                    self.frames[frame_name] = Products(self.content_frame, app=self)
                elif frame_class == "Expenses":
                    from ui.expenses import Expenses
                    self.frames[frame_name] = Expenses(self.content_frame, app=self)
                elif frame_class == "Reports":
                    # Create Reports instance
                    self.frames[frame_name] = ReportsFrame(self.content_frame, app=self)
                else:
                    # For other frames, use the provided class
                    self.frames[frame_name] = frame_class(self.content_frame, *args, **kwargs)
            except Exception as e:
                self.set_status(f"Error loading {frame_name}: {e}", error=True)
                # Fallback to simple frame
                self.frames[frame_name] = self.create_simple_frame(frame_name)
        
        # Show the frame
        self.frames[frame_name].grid(row=0, column=0, sticky="nsew")
        self.current_frame = self.frames[frame_name]
        
        # Update window title
        self.root.title(f"Nano ERP - {frame_name}")
        
        # Update status
        self.set_status(f"{frame_name} loaded")
        
        # Update sidebar stats if showing dashboard
        if frame_name == "Dashboard":
            self.update_sidebar_stats()
    
    def create_simple_frame(self, frame_name):
        """Create a simple placeholder frame"""
        frame = ttk.Frame(self.content_frame)
        
        ttk.Label(frame, text=frame_name, font=('Segoe UI', 20, 'bold')).pack(pady=50)
        ttk.Label(frame, text="Module under development", font=('Segoe UI', 12)).pack()
        
        return frame
    
    def show_dashboard(self):
        """Show dashboard frame"""
        self.show_frame("Dashboard", "Dashboard")
    
    def show_invoices(self):
        """Show invoices frame"""
        self.show_frame("Invoices", "Invoices")
    
    def show_customers(self):
        """Show customers frame"""
        self.show_frame("Customers", "Customers")
    
    def show_products(self):
        """Show products frame"""
        self.show_frame("Products", "Products")
    
    def show_expenses(self):
        """Show expenses frame"""
        self.show_frame("Expenses", "Expenses")
    
    def show_reports(self):
        """Show reports frame"""
        self.show_frame("Reports", "Reports")
    
    def show_settings(self):
        """Show settings frame"""
        # Create settings frame
        frame = ttk.Frame(self.content_frame)
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header, text="Settings", font=('Segoe UI', 20, 'bold')).pack(side=tk.LEFT)
        
        # Settings notebook
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # General settings tab
        general_frame = ttk.Frame(notebook, padding=20)
        notebook.add(general_frame, text="General")
        
        ttk.Label(general_frame, text="Business Information", 
                 font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Business name
        try:
            from database import get_setting, set_setting
            
            business_name = get_setting('business_name', 'My Business')
            
            ttk.Label(general_frame, text="Business Name:", font=('Segoe UI', 10)).grid(
                row=0, column=0, sticky=tk.W, pady=5)
            business_name_var = tk.StringVar(value=business_name)
            business_name_entry = ttk.Entry(general_frame, textvariable=business_name_var, width=30)
            business_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            
            # Address
            business_address = get_setting('business_address', '')
            ttk.Label(general_frame, text="Address:", font=('Segoe UI', 10)).grid(
                row=1, column=0, sticky=tk.W, pady=5)
            address_text = tk.Text(general_frame, height=3, width=30)
            address_text.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            address_text.insert(1.0, business_address)
            
            # Contact
            business_phone = get_setting('business_phone', '')
            ttk.Label(general_frame, text="Contact:", font=('Segoe UI', 10)).grid(
                row=2, column=0, sticky=tk.W, pady=5)
            phone_var = tk.StringVar(value=business_phone)
            phone_entry = ttk.Entry(general_frame, textvariable=phone_var, width=30)
            phone_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            
            # Invoice settings tab
            invoice_frame = ttk.Frame(notebook, padding=20)
            notebook.add(invoice_frame, text="Invoicing")
            
            ttk.Label(invoice_frame, text="Invoice Settings", 
                     font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            # Default tax rate
            tax_rate = get_setting('default_tax_rate', '18')
            ttk.Label(invoice_frame, text="Default Tax Rate (%):", font=('Segoe UI', 10)).grid(
                row=0, column=0, sticky=tk.W, pady=5)
            tax_rate_var = tk.StringVar(value=tax_rate)
            tax_rate_spin = ttk.Spinbox(invoice_frame, from_=0, to=100, textvariable=tax_rate_var, width=10)
            tax_rate_spin.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            
            # Invoice prefix
            invoice_prefix = get_setting('invoice_prefix', 'INV')
            ttk.Label(invoice_frame, text="Invoice Prefix:", font=('Segoe UI', 10)).grid(
                row=1, column=0, sticky=tk.W, pady=5)
            prefix_var = tk.StringVar(value=invoice_prefix)
            prefix_entry = ttk.Entry(invoice_frame, textvariable=prefix_var, width=10)
            prefix_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            
            # Save button
            def save_settings():
                set_setting('business_name', business_name_var.get())
                set_setting('business_address', address_text.get(1.0, tk.END).strip())
                set_setting('business_phone', phone_var.get())
                set_setting('default_tax_rate', tax_rate_var.get())
                set_setting('invoice_prefix', prefix_var.get())
                messagebox.showinfo("Success", "Settings saved successfully!")
            
            ttk.Button(frame, text="💾 Save Settings", width=20, command=save_settings).pack(pady=20)
            
        except ImportError:
            ttk.Label(general_frame, text="Settings module not available", 
                     font=('Segoe UI', 12), foreground='red').pack(pady=50)
        
        self.show_frame(lambda parent: frame, "Settings")
    
    def show_help(self):
        """Show help frame"""
        # Create help frame
        frame = ttk.Frame(self.content_frame)
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header, text="Help & Documentation", 
                 font=('Segoe UI', 20, 'bold')).pack(side=tk.LEFT)
        
        # Help content
        help_text = tk.Text(frame, wrap=tk.WORD, font=('Segoe UI', 10), height=20)
        help_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        help_content = """
        Nano ERP - Help & Documentation
        ================================
        
        Getting Started
        ---------------
        1. Dashboard: View business overview and quick stats
        2. Invoices: Create and manage customer invoices
        3. Customers: Manage customer database
        4. Products: Manage product catalog and inventory
        5. Expenses: Track business expenses
        6. Reports: Generate business reports
        7. Settings: Configure application settings
        
        Quick Tips
        ----------
        • Use the sidebar navigation to switch between modules
        • Right-click on lists for additional options
        • Press F1 for context-sensitive help
        • Export data using the Export buttons
        
        Support
        -------
        For technical support or feature requests:
        • Email: support@nanoerp.com
        • Website: https://www.nanoerp.com
        • Documentation: https://docs.nanoerp.com
        
        Version: 1.0.0
        """
        
        help_text.insert("1.0", help_content)
        help_text.config(state=tk.DISABLED)
        
        self.show_frame(lambda parent: frame, "Help")
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit Nano ERP?"):
            # Save any unsaved data
            try:
                from database import db
                if db.connection:
                    db.close()
            except:
                pass
            
            self.root.destroy()


class ReportsFrame(ttk.Frame):
    """Reports frame with proper export functionality"""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.report_data = None  # Store generated report data
        self.create_widgets()
    
    def create_widgets(self):
        """Create report widgets"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Use the PageTitle style instead of hardcoded font
        ttk.Label(header_frame, text="Reports", style='PageTitle.TLabel').pack(side=tk.LEFT)
        
        # Control frame for filters and buttons
        control_frame = ttk.LabelFrame(main_frame, text="Report Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Date range
        ttk.Label(control_frame, text="Date Range:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.start_date = tk.StringVar(value="2024-01-01")
        self.end_date = tk.StringVar(value="2024-12-31")
        
        ttk.Entry(control_frame, textvariable=self.start_date, width=12).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(control_frame, text="to").grid(row=0, column=2, padx=5)
        ttk.Entry(control_frame, textvariable=self.end_date, width=12).grid(row=0, column=3, padx=5, pady=5)
        
        # Report type selection
        ttk.Label(control_frame, text="Report Type:").grid(row=0, column=4, sticky=tk.W, padx=(20, 5), pady=5)
        
        self.report_type = tk.StringVar(value="sales")
        report_types = ["sales", "expenses", "customers", "products", "inventory", "profit_loss"]
        report_combo = ttk.Combobox(control_frame, textvariable=self.report_type, 
                                   values=report_types, width=15, state="readonly")
        report_combo.grid(row=0, column=5, padx=5, pady=5)
        
        # Generate button
        ttk.Button(control_frame, text="📊 Generate Report", 
                  command=self.generate_report).grid(row=0, column=6, padx=20, pady=5)
        
        # Export buttons frame
        export_frame = ttk.Frame(control_frame)
        export_frame.grid(row=0, column=7, padx=20, pady=5)
        
        self.csv_btn = ttk.Button(export_frame, text="📥 Export CSV", 
                                  command=self.export_csv, state=tk.DISABLED)
        self.csv_btn.pack(side=tk.LEFT, padx=2)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Report Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for results
        columns = ("ID", "Date", "Description", "Amount", "Status")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Status", text="Status")
        
        # Define column widths
        self.tree.column("ID", width=50)
        self.tree.column("Date", width=100)
        self.tree.column("Description", width=300)
        self.tree.column("Amount", width=100)
        self.tree.column("Status", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Summary frame
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.summary_label = ttk.Label(summary_frame, text="No report generated yet", 
                                       font=('Segoe UI', 10, 'bold'))
        self.summary_label.pack(anchor=tk.W)
    
    def generate_report(self):
        """Generate report based on selected criteria"""
        try:
            from database import db
            report_type = self.report_type.get()
            start_date = self.start_date.get()
            end_date = self.end_date.get()
            
            # Clear previous data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.report_data = []
            
            if report_type == "sales":
                # Sales Report - Join with customers table
                query = """
                    SELECT 
                        i.id, 
                        i.date, 
                        c.name as customer_name, 
                        i.total, 
                        i.status 
                    FROM invoices i
                    LEFT JOIN customers c ON i.customer_id = c.id
                    WHERE i.date BETWEEN ? AND ?
                    ORDER BY i.date DESC
                """
                rows = db.fetch_all(query, (start_date, end_date))
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['id'],
                            row['date'],
                            f"Sale to {row['customer_name'] or 'Unknown Customer'}",
                            f"₹{row['total']:.2f}",
                            row['status']
                        ))
                        self.report_data.append(row)
                    
                    # Calculate summary (excluding cancelled)
                    total_query = """
                        SELECT 
                            COUNT(*) as count, 
                            SUM(i.total) as total 
                        FROM invoices i
                        LEFT JOIN customers c ON i.customer_id = c.id
                        WHERE i.date BETWEEN ? AND ? AND i.status != 'cancelled'
                    """
                    total_row = db.fetch_one(total_query, (start_date, end_date))
                    
                    cancelled_query = """
                        SELECT COUNT(*) as cancelled_count 
                        FROM invoices i
                        LEFT JOIN customers c ON i.customer_id = c.id
                        WHERE i.date BETWEEN ? AND ? AND i.status = 'cancelled'
                    """
                    cancelled_row = db.fetch_one(cancelled_query, (start_date, end_date))
                    
                    summary = f"Sales Report: {len(rows)} total invoices ({cancelled_row['cancelled_count'] or 0} cancelled). Active total: ₹{total_row['total'] or 0:.2f}"
                else:
                    summary = f"Sales Report: No invoices found for the selected date range"
                
            elif report_type == "expenses":
                # Expenses Report
                query = """
                    SELECT id, date, category, description, amount 
                    FROM expenses 
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                """
                rows = db.fetch_all(query, (start_date, end_date))
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['id'],
                            row['date'],
                            f"{row['category']}: {row['description']}",
                            f"₹{row['amount']:.2f}",
                            "Paid"
                        ))
                        self.report_data.append(row)
                    
                    # Calculate summary
                    total_query = """
                        SELECT COUNT(*) as count, SUM(amount) as total 
                        FROM expenses 
                        WHERE date BETWEEN ? AND ?
                    """
                    total_row = db.fetch_one(total_query, (start_date, end_date))
                    
                    summary = f"Expenses Report: {total_row['count']} expenses, Total: ₹{total_row['total'] or 0:.2f}"
                else:
                    summary = f"Expenses Report: No expenses found for the selected date range"
                
            elif report_type == "customers":
                # Customers Report
                query = """
                    SELECT 
                        c.id, 
                        c.name, 
                        c.email, 
                        c.phone,
                        c.created_at,
                        COUNT(i.id) as total_invoices,
                        SUM(i.total) as total_spent
                    FROM customers c
                    LEFT JOIN invoices i ON c.id = i.customer_id
                    WHERE c.created_at BETWEEN ? AND ?
                    GROUP BY c.id
                    ORDER BY c.created_at DESC
                """
                rows = db.fetch_all(query, (start_date, end_date))
                
                if rows:
                    for row in rows:
                        self.tree.insert("", tk.END, values=(
                            row['id'],
                            row['created_at'].split()[0] if row['created_at'] else "",
                            f"{row['name']} ({row['email']})",
                            f"₹{row['total_spent'] or 0:.2f}",
                            f"{row['total_invoices']} invoices"
                        ))
                        self.report_data.append(row)
                    
                    # Calculate summary
                    total_customers = len(rows)
                    active_customers = sum(1 for row in rows if row['total_invoices'] > 0)
                    total_revenue = sum(row['total_spent'] or 0 for row in rows)
                    
                    summary = f"Customers Report: {total_customers} total customers, {active_customers} active, Total Revenue: ₹{total_revenue:.2f}"
                else:
                    summary = f"Customers Report: No customers found for the selected date range"
                
            elif report_type == "products":
                # Products Report
                query = """
                    SELECT 
                        id, 
                        name, 
                        category, 
                        price, 
                        stock,
                        created_at,
                        is_service
                    FROM products
                    WHERE created_at BETWEEN ? AND ?
                    ORDER BY created_at DESC
                """
                rows = db.fetch_all(query, (start_date, end_date))
                
                if rows:
                    for row in rows:
                        product_type = "Service" if row['is_service'] == 1 else "Product"
                        stock_status = f"{row['stock']} units" if row['is_service'] == 0 else "N/A"
                        self.tree.insert("", tk.END, values=(
                            row['id'],
                            row['created_at'].split()[0] if row['created_at'] else "",
                            f"{row['name']} ({row['category']})",
                            f"₹{row['price']:.2f}",
                            f"{stock_status} - {product_type}"
                        ))
                        self.report_data.append(row)
                    
                    # Calculate summary
                    total_products = len(rows)
                    services = sum(1 for row in rows if row['is_service'] == 1)
                    products = total_products - services
                    total_stock_value = sum((row['price'] * row['stock']) for row in rows if row['is_service'] == 0)
                    
                    summary = f"Products Report: {total_products} total items ({products} products, {services} services), Total Stock Value: ₹{total_stock_value:.2f}"
                else:
                    summary = f"Products Report: No products found for the selected date range"
                
            elif report_type == "inventory":
                # Inventory Report (Low Stock)
                query = """
                    SELECT 
                        id, 
                        name, 
                        category, 
                        price, 
                        stock,
                        created_at
                    FROM products
                    WHERE stock < 20 AND is_service = 0
                    ORDER BY stock ASC
                """
                rows = db.fetch_all(query)
                
                if rows:
                    for row in rows:
                        status = "Critical" if row['stock'] < 5 else "Low" if row['stock'] < 10 else "Moderate"
                        self.tree.insert("", tk.END, values=(
                            row['id'],
                            row['created_at'].split()[0] if row['created_at'] else "",
                            f"{row['name']} ({row['category']})",
                            f"₹{row['price']:.2f}",
                            f"{row['stock']} units - {status}"
                        ))
                        self.report_data.append(row)
                    
                    # Calculate summary
                    critical = sum(1 for row in rows if row['stock'] < 5)
                    low = sum(1 for row in rows if 5 <= row['stock'] < 10)
                    moderate = sum(1 for row in rows if 10 <= row['stock'] < 20)
                    total_value = sum((row['price'] * row['stock']) for row in rows)
                    
                    summary = f"Inventory Report: {len(rows)} low stock items (Critical: {critical}, Low: {low}, Moderate: {moderate}), Total Value: ₹{total_value:.2f}"
                else:
                    summary = f"Inventory Report: No low stock items found"
                
            elif report_type == "profit_loss":
                # Profit & Loss Report
                # Get sales revenue
                sales_query = """
                    SELECT SUM(i.total) as total_sales
                    FROM invoices i
                    LEFT JOIN customers c ON i.customer_id = c.id
                    WHERE i.date BETWEEN ? AND ? AND i.status != 'cancelled'
                """
                sales_row = db.fetch_one(sales_query, (start_date, end_date))
                total_sales = sales_row['total_sales'] or 0
                
                # Get expenses
                expenses_query = """
                    SELECT SUM(amount) as total_expenses
                    FROM expenses 
                    WHERE date BETWEEN ? AND ?
                """
                expenses_row = db.fetch_one(expenses_query, (start_date, end_date))
                total_expenses = expenses_row['total_expenses'] or 0
                
                # Calculate profit/loss
                profit_loss = total_sales - total_expenses
                
                # Insert summary rows
                self.tree.insert("", tk.END, values=(
                    "REV",
                    f"{start_date} to {end_date}",
                    "Total Sales Revenue",
                    f"₹{total_sales:.2f}",
                    "Revenue"
                ))
                self.tree.insert("", tk.END, values=(
                    "EXP",
                    f"{start_date} to {end_date}",
                    "Total Expenses",
                    f"₹{total_expenses:.2f}",
                    "Expenses"
                ))
                self.tree.insert("", tk.END, values=(
                    "PL",
                    f"{start_date} to {end_date}",
                    "Net Profit/Loss",
                    f"₹{profit_loss:.2f}",
                    "Profit" if profit_loss >= 0 else "Loss"
                ))
                
                self.report_data = [
                    {"type": "revenue", "amount": total_sales},
                    {"type": "expenses", "amount": total_expenses},
                    {"type": "profit_loss", "amount": profit_loss}
                ]
                
                summary = f"Profit & Loss Report: Revenue: ₹{total_sales:.2f}, Expenses: ₹{total_expenses:.2f}, Net: ₹{profit_loss:.2f} ({'Profit' if profit_loss >= 0 else 'Loss'})"            
            self.summary_label.config(text=summary)
            
            # Enable export buttons if we have data
            if self.report_data:
                self.csv_btn.config(state=tk.NORMAL)
                self.app.set_status(f"Report generated: {len(self.report_data)} records")
            else:
                self.csv_btn.config(state=tk.DISABLED)
                self.app.set_status(f"Report generated: No data found")
            
        except Exception as e:
            self.app.set_status(f"Error generating report: {e}", error=True)
            messagebox.showerror("Error", f"Failed to generate report: {e}")
            self.csv_btn.config(state=tk.DISABLED)
    
    def export_csv(self):
        """Export report to CSV file"""
        if not self.report_data:
            messagebox.showwarning("Export", "Please generate a report first before exporting.")
            return
        
        try:
            import csv
            from tkinter import filedialog
            from datetime import datetime
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"{self.report_type.get()}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return  # User cancelled
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                report_type = self.report_type.get()
                
                if report_type == "sales":
                    headers = ["ID", "Date", "Customer Name", "Total", "Status"]
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    
                    for row in self.report_data:
                        if isinstance(row, dict):
                            writer.writerow([
                                row.get('id', ''),
                                row.get('date', ''),
                                row.get('customer_name', ''),
                                row.get('total', 0),
                                row.get('status', '')
                            ])
                        else:
                            # Handle list/tuple
                            writer.writerow(row)
                
                elif report_type == "expenses":
                    headers = ["ID", "Date", "Category", "Description", "Amount"]
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    
                    for row in self.report_data:
                        if isinstance(row, dict):
                            writer.writerow([
                                row.get('id', ''),
                                row.get('date', ''),
                                row.get('category', ''),
                                row.get('description', ''),
                                row.get('amount', 0)
                            ])
                        else:
                            writer.writerow(row)
                
                elif report_type == "customers":
                    headers = ["ID", "Name", "Email", "Phone", "Created At", "Total Invoices", "Total Spent"]
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    
                    for row in self.report_data:
                        if isinstance(row, dict):
                            writer.writerow([
                                row.get('id', ''),
                                row.get('name', ''),
                                row.get('email', ''),
                                row.get('phone', ''),
                                row.get('created_at', ''),
                                row.get('total_invoices', 0),
                                row.get('total_spent', 0)
                            ])
                        else:
                            writer.writerow(row)
                
                elif report_type == "products":
                    headers = ["ID", "Name", "Category", "Price", "Stock", "Created At", "Is Service"]
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    
                    for row in self.report_data:
                        if isinstance(row, dict):
                            writer.writerow([
                                row.get('id', ''),
                                row.get('name', ''),
                                row.get('category', ''),
                                row.get('price', 0),
                                row.get('stock', 0),
                                row.get('created_at', ''),
                                row.get('is_service', 0)
                            ])
                        else:
                            writer.writerow(row)
                
                elif report_type == "inventory":
                    headers = ["ID", "Name", "Category", "Price", "Stock", "Created At"]
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    
                    for row in self.report_data:
                        if isinstance(row, dict):
                            writer.writerow([
                                row.get('id', ''),
                                row.get('name', ''),
                                row.get('category', ''),
                                row.get('price', 0),
                                row.get('stock', 0),
                                row.get('created_at', '')
                            ])
                        else:
                            writer.writerow(row)
                
                elif report_type == "profit_loss":
                    headers = ["Type", "Amount"]
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    
                    for row in self.report_data:
                        if isinstance(row, dict):
                            writer.writerow([
                                row.get('type', ''),
                                row.get('amount', 0)
                            ])
                        else:
                            writer.writerow(row)
                
                else:
                    # Fallback for unknown report types
                    writer = csv.writer(csvfile)
                    if self.report_data and isinstance(self.report_data[0], dict):
                        headers = list(self.report_data[0].keys())
                        writer.writerow(headers)
                        for row in self.report_data:
                            writer.writerow([row.get(key, '') for key in headers])
                    else:
                        # Just write the data as-is
                        for row in self.report_data:
                            writer.writerow(row)
            
            self.app.set_status(f"Report exported to {filename}")
            messagebox.showinfo("Success", f"Report exported successfully to:\n{filename}")
            
        except Exception as e:
            self.app.set_status(f"Error exporting CSV: {e}", error=True)
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
