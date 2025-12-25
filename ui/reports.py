"""
reports.py - Comprehensive reporting module for Nano ERP
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
from database import db
import csv
import os

class Reports(ttk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.create_widgets()
    
    def create_widgets(self):
        """Create reports management widgets"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Reports & Analytics", 
                 font=('Segoe UI', 20, 'bold')).pack(side=tk.LEFT)
        
        # Export button
        export_btn = ttk.Button(header_frame, text="📤 Export All Data", 
                               command=self.export_all_data)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Report selection frame
        reports_frame = ttk.LabelFrame(main_frame, text="Available Reports", padding=20)
        reports_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create report buttons in a grid
        reports = [
            ("📊 Sales Report", "Generate detailed sales report", self.generate_sales_report),
            ("💰 Expense Report", "Track and analyze expenses", self.generate_expense_report),
            ("📈 Profit & Loss", "View P&L statement", self.generate_profit_loss_report),
            ("👥 Customer Report", "Customer analysis and statistics", self.generate_customer_report),
            ("📦 Inventory Report", "Stock levels and valuation", self.generate_inventory_report),
            ("📅 Monthly Summary", "Monthly performance overview", self.generate_monthly_summary),
            ("📋 Invoice Report", "Detailed invoice analysis", self.generate_invoice_report),
            ("🏷️ Product Sales", "Product-wise sales analysis", self.generate_product_sales_report),
        ]
        
        for i, (title, desc, command) in enumerate(reports):
            report_card = ttk.Frame(reports_frame)
            report_card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            ttk.Label(report_card, text=title, 
                     font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(report_card, text=desc, 
                     font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(0, 10))
            
            btn_frame = ttk.Frame(report_card)
            btn_frame.pack(fill=tk.X)
            
            ttk.Button(btn_frame, text="Generate", 
                      command=command, width=12).pack(side=tk.LEFT)
            ttk.Button(btn_frame, text="Export CSV", 
                      command=lambda cmd=command: self.export_report(cmd), width=12).pack(side=tk.LEFT, padx=5)
            
            reports_frame.columnconfigure(i%2, weight=1)
    
    def show_report_dialog(self, title, report_data, columns, summary_text=None):
        """Show report results in a dialog"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("900x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Main container
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Summary text (if provided)
        if summary_text:
            summary_frame = ttk.LabelFrame(main_frame, text="Summary", padding=10)
            summary_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(summary_frame, text=summary_text, 
                     font=('Segoe UI', 10)).pack(anchor=tk.W)
        
        # Treeview for report data
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add data to treeview
        for row in report_data:
            tree.insert('', tk.END, values=row)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Export to CSV", 
                  command=lambda: self.export_to_csv(report_data, columns, title)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Print", 
                  command=lambda: self.print_report(title, report_data, columns)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", 
                  command=dialog.destroy).pack(side=tk.RIGHT)
    
    def get_date_range_dialog(self, title="Select Date Range"):
        """Show date range selection dialog"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # From date
        ttk.Label(frame, text="From Date:", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=10)
        from_date_var = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime("%Y-%m-%d"))
        from_date_entry = ttk.Entry(frame, textvariable=from_date_var, width=15)
        from_date_entry.grid(row=0, column=1, sticky=tk.W, pady=10, padx=10)
        ttk.Button(frame, text="📅", width=3,
                  command=lambda: self.show_calendar(from_date_var)).grid(row=0, column=2, padx=5)
        
        # To date
        ttk.Label(frame, text="To Date:", font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=10)
        to_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        to_date_entry = ttk.Entry(frame, textvariable=to_date_var, width=15)
        to_date_entry.grid(row=1, column=1, sticky=tk.W, pady=10, padx=10)
        ttk.Button(frame, text="📅", width=3,
                  command=lambda: self.show_calendar(to_date_var)).grid(row=1, column=2, padx=5)
        
        # Status filter
        ttk.Label(frame, text="Invoice Status:", font=('Segoe UI', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=10)
        status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(frame, textvariable=status_var, 
                                   values=["All", "paid", "pending", "cancelled"], 
                                   state="readonly", width=15)
        status_combo.grid(row=2, column=1, sticky=tk.W, pady=10, padx=10)
        
        result = {"from_date": from_date_var, "to_date": to_date_var, "status": status_var}
        
        def on_generate():
            result["confirmed"] = True
            dialog.destroy()
        
        def on_cancel():
            result["confirmed"] = False
            dialog.destroy()
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Generate Report", 
                  command=on_generate, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return result
    
    def show_calendar(self, date_var):
        """Show a simple calendar for date selection"""
        import calendar
        
        dialog = tk.Toplevel(self)
        dialog.title("Select Date")
        dialog.geometry("300x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Current date
        current_date = datetime.now()
        
        # Month and year selection
        month_var = tk.IntVar(value=current_date.month)
        year_var = tk.IntVar(value=current_date.year)
        
        month_year_frame = ttk.Frame(frame)
        month_year_frame.pack(fill=tk.X, pady=(0, 10))
        
        months = list(calendar.month_name)[1:]
        ttk.Combobox(month_year_frame, textvariable=month_var, 
                    values=months, state="readonly", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(month_year_frame, from_=2000, to=2100, 
                   textvariable=year_var, width=8).pack(side=tk.LEFT, padx=5)
        
        # Calendar grid
        cal_frame = ttk.Frame(frame)
        cal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get calendar
        cal = calendar.monthcalendar(year_var.get(), month_var.get())
        
        # Day headers
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(days):
            ttk.Label(cal_frame, text=day, width=3, 
                     font=('Arial', 9, 'bold')).grid(row=0, column=i)
        
        # Day buttons
        selected_day = tk.IntVar()
        
        def select_day(day):
            selected_day.set(day)
            date_var.set(f"{year_var.get():04d}-{month_var.get():02d}-{day:02d}")
            dialog.destroy()
        
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = ttk.Button(cal_frame, text=str(day), width=3,
                                   command=lambda d=day: select_day(d))
                    btn.grid(row=week_num, column=day_num, padx=1, pady=1)
        
        dialog.wait_window()
    
    def generate_sales_report(self):
        """Generate detailed sales report"""
        # Get date range
        date_range = self.get_date_range_dialog("Sales Report - Select Date Range")
        if not date_range.get("confirmed", False):
            return
        
        from_date = date_range["from_date"].get()
        to_date = date_range["to_date"].get()
        status = date_range["status"].get()
        
        # Build query
        where_clauses = ["i.date BETWEEN ? AND ?"]
        params = [from_date, to_date]
        
        if status != "All":
            where_clauses.append("i.status = ?")
            params.append(status)
        
        where_clause = " AND ".join(where_clauses)
        
        query = f'''
            SELECT 
                i.id as invoice_id,
                i.invoice_number,
                i.date,
                c.name as customer_name,
                i.subtotal,
                i.tax_amount,
                i.total,
                i.status,
                COUNT(ii.id) as items_count
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
            WHERE {where_clause}
            GROUP BY i.id
            ORDER BY i.date DESC
        '''
        
        rows = db.fetch_all(query, params)
        
        # Calculate totals
        total_sales = sum(row['total'] for row in rows)
        total_tax = sum(row['tax_amount'] for row in rows)
        total_subtotal = sum(row['subtotal'] for row in rows)
        total_invoices = len(rows)
        
        # Prepare data for display
        report_data = []
        for row in rows:
            report_data.append((
                row['invoice_number'],
                row['date'],
                row['customer_name'] or 'Walk-in',
                f"₹{row['subtotal']:.2f}",
                f"₹{row['tax_amount']:.2f}",
                f"₹{row['total']:.2f}",
                row['status'],
                row['items_count']
            ))
        
        columns = ('Invoice #', 'Date', 'Customer', 'Subtotal', 'Tax', 'Total', 'Status', 'Items')
        
        summary = f"Date Range: {from_date} to {to_date}\n"
        summary += f"Total Invoices: {total_invoices}\n"
        summary += f"Total Sales: ₹{total_sales:.2f}\n"
        summary += f"Total Tax: ₹{total_tax:.2f}\n"
        summary += f"Net Sales: ₹{total_subtotal:.2f}"
        
        self.show_report_dialog(f"Sales Report ({from_date} to {to_date})", 
                               report_data, columns, summary)
    
    def generate_expense_report(self):
        """Generate expense analysis report"""
        # Get date range
        date_range = self.get_date_range_dialog("Expense Report - Select Date Range")
        if not date_range.get("confirmed", False):
            return
        
        from_date = date_range["from_date"].get()
        to_date = date_range["to_date"].get()
        
        # Query expenses by category
        query = '''
            SELECT 
                category,
                COUNT(*) as count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(date) as first_date,
                MAX(date) as last_date
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total_amount DESC
        '''
        
        rows = db.fetch_all(query, (from_date, to_date))
        
        # Prepare data for display
        report_data = []
        for row in rows:
            report_data.append((
                row['category'],
                row['count'],
                f"₹{row['total_amount']:.2f}",
                f"₹{row['avg_amount']:.2f}",
                row['first_date'],
                row['last_date']
            ))
        
        # Get total expenses
        total_query = '''
            SELECT SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE date BETWEEN ? AND ?
        '''
        total_row = db.fetch_one(total_query, (from_date, to_date))
        
        columns = ('Category', 'Count', 'Total Amount', 'Avg Amount', 'First Date', 'Last Date')
        
        summary = f"Date Range: {from_date} to {to_date}\n"
        summary += f"Total Expenses: {total_row['count']}\n"
        summary += f"Total Amount: ₹{total_row['total'] or 0:.2f}\n"
        summary += f"Categories: {len(rows)}"
        
        self.show_report_dialog(f"Expense Report ({from_date} to {to_date})", 
                               report_data, columns, summary)
    
    def generate_profit_loss_report(self):
        """Generate Profit & Loss statement"""
        # Get date range
        date_range = self.get_date_range_dialog("Profit & Loss - Select Date Range")
        if not date_range.get("confirmed", False):
            return
        
        from_date = date_range["from_date"].get()
        to_date = date_range["to_date"].get()
        
        # Get total sales
        sales_query = '''
            SELECT 
                SUM(total) as total_sales,
                SUM(tax_amount) as total_tax,
                SUM(subtotal) as net_sales,
                COUNT(*) as invoice_count
            FROM invoices
            WHERE date BETWEEN ? AND ? AND status != 'cancelled'
        '''
        sales_data = db.fetch_one(sales_query, (from_date, to_date))
        
        # Get total expenses
        expense_query = '''
            SELECT 
                SUM(amount) as total_expenses,
                COUNT(*) as expense_count
            FROM expenses
            WHERE date BETWEEN ? AND ?
        '''
        expense_data = db.fetch_one(expense_query, (from_date, to_date))
        
        # Calculate profit/loss
        net_sales = sales_data['net_sales'] or 0
        total_expenses = expense_data['total_expenses'] or 0
        profit_loss = net_sales - total_expenses
        
        # Prepare report data
        report_data = [
            ("Revenue", "", f"₹{net_sales:.2f}"),
            ("  Sales (Net)", f"{sales_data['invoice_count']} invoices", f"₹{net_sales:.2f}"),
            ("", "", ""),
            ("Expenses", "", f"₹{total_expenses:.2f}"),
            ("  Operating Expenses", f"{expense_data['expense_count']} expenses", f"₹{total_expenses:.2f}"),
            ("", "", ""),
            ("Profit/Loss", "", f"₹{profit_loss:.2f}")
        ]
        
        columns = ('Category', 'Details', 'Amount')
        
        summary = f"Profit & Loss Statement\n"
        summary += f"Date Range: {from_date} to {to_date}\n"
        summary += f"Net Sales: ₹{net_sales:.2f}\n"
        summary += f"Total Expenses: ₹{total_expenses:.2f}\n"
        summary += f"Net Profit/Loss: ₹{profit_loss:.2f}\n"
        summary += f"Profit Margin: {(profit_loss/net_sales*100 if net_sales > 0 else 0):.1f}%"
        
        self.show_report_dialog(f"Profit & Loss ({from_date} to {to_date})", 
                               report_data, columns, summary)
    
    def generate_customer_report(self):
        """Generate customer analysis report"""
        # Get customer statistics
        query = '''
            SELECT 
                c.id,
                c.name,
                c.email,
                c.phone,
                COUNT(i.id) as invoice_count,
                SUM(i.total) as total_spent,
                MIN(i.date) as first_purchase,
                MAX(i.date) as last_purchase
            FROM customers c
            LEFT JOIN invoices i ON c.id = i.customer_id
            GROUP BY c.id
            ORDER BY total_spent DESC
        '''
        
        rows = db.fetch_all(query)
        
        # Prepare data for display
        report_data = []
        for row in rows:
            report_data.append((
                row['id'],
                row['name'],
                row['email'] or '',
                row['phone'] or '',
                row['invoice_count'],
                f"₹{row['total_spent'] or 0:.2f}",
                row['first_purchase'] or 'No purchases',
                row['last_purchase'] or 'No purchases'
            ))
        
        # Calculate summary
        total_customers = len(rows)
        active_customers = sum(1 for row in rows if row['invoice_count'] > 0)
        total_revenue = sum(row['total_spent'] or 0 for row in rows)
        avg_spending = total_revenue / active_customers if active_customers > 0 else 0
        
        columns = ('ID', 'Name', 'Email', 'Phone', 'Invoices', 'Total Spent', 'First Purchase', 'Last Purchase')
        
        summary = f"Customer Analysis Report\n"
        summary += f"Total Customers: {total_customers}\n"
        summary += f"Active Customers: {active_customers}\n"
        summary += f"Total Revenue: ₹{total_revenue:.2f}\n"
        summary += f"Average Spending: ₹{avg_spending:.2f}"
        
        self.show_report_dialog("Customer Analysis Report", report_data, columns, summary)
    
    def generate_inventory_report(self):
        """Generate inventory stock report"""
        # Get product inventory
        query = '''
            SELECT 
                id,
                name,
                description,
                price,
                stock,
                CASE WHEN is_service = 1 THEN 'Service' ELSE 'Product' END as type,
                created_at
            FROM products
            ORDER BY stock, name
        '''
        
        rows = db.fetch_all(query)
        
        # Prepare data for display
        report_data = []
        low_stock_count = 0
        out_of_stock_count = 0
        total_value = 0
        
        for row in rows:
            if row['type'] == 'Product':
                item_value = row['price'] * row['stock']
                total_value += item_value
                
                if row['stock'] == 0:
                    stock_status = "Out of Stock"
                    out_of_stock_count += 1
                elif row['stock'] < 10:
                    stock_status = "Low Stock"
                    low_stock_count += 1
                else:
                    stock_status = "In Stock"
            else:
                item_value = 0
                stock_status = "N/A (Service)"
            
            report_data.append((
                row['id'],
                row['name'],
                row['type'],
                f"₹{row['price']:.2f}",
                row['stock'],
                f"₹{item_value:.2f}",
                stock_status
            ))
        
        columns = ('ID', 'Name', 'Type', 'Price', 'Stock', 'Total Value', 'Status')
        
        summary = f"Inventory Valuation Report\n"
        summary += f"Total Products: {len(rows)}\n"
        summary += f"Low Stock (<10): {low_stock_count}\n"
        summary += f"Out of Stock: {out_of_stock_count}\n"
        summary += f"Total Inventory Value: ₹{total_value:.2f}"
        
        self.show_report_dialog("Inventory Report", report_data, columns, summary)
    
    def generate_monthly_summary(self):
        """Generate monthly performance summary"""
        # Get current month and previous month
        today = date.today()
        current_month_start = today.replace(day=1)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)
        
        # Get current month data
        current_sales = db.fetch_one('''
            SELECT 
                SUM(total) as sales,
                COUNT(*) as invoices,
                AVG(total) as avg_invoice
            FROM invoices
            WHERE date >= ? AND status != 'cancelled'
        ''', (current_month_start,))
        
        current_expenses = db.fetch_one('''
            SELECT 
                SUM(amount) as expenses,
                COUNT(*) as expense_count
            FROM expenses
            WHERE date >= ?
        ''', (current_month_start,))
        
        # Get previous month data
        previous_sales = db.fetch_one('''
            SELECT 
                SUM(total) as sales,
                COUNT(*) as invoices,
                AVG(total) as avg_invoice
            FROM invoices
            WHERE date BETWEEN ? AND ? AND status != 'cancelled'
        ''', (previous_month_start, previous_month_end))
        
        previous_expenses = db.fetch_one('''
            SELECT 
                SUM(amount) as expenses,
                COUNT(*) as expense_count
            FROM expenses
            WHERE date BETWEEN ? AND ?
        ''', (previous_month_start, previous_month_end))
        
        # Get new customers this month
        new_customers = db.fetch_one('''
            SELECT COUNT(*) as count
            FROM customers
            WHERE created_at >= ?
        ''', (current_month_start,))
        
        # Calculate changes
        sales_change = self.calculate_change(current_sales['sales'] or 0, previous_sales['sales'] or 0)
        expense_change = self.calculate_change(current_expenses['expenses'] or 0, previous_expenses['expenses'] or 0)
        profit = (current_sales['sales'] or 0) - (current_expenses['expenses'] or 0)
        previous_profit = (previous_sales['sales'] or 0) - (previous_expenses['expenses'] or 0)
        profit_change = self.calculate_change(profit, previous_profit)
        
        # Prepare report data
        report_data = [
            ("Sales", f"₹{current_sales['sales'] or 0:.2f}", 
             f"{sales_change:+.1f}%", f"₹{previous_sales['sales'] or 0:.2f}"),
            ("Expenses", f"₹{current_expenses['expenses'] or 0:.2f}", 
             f"{expense_change:+.1f}%", f"₹{previous_expenses['expenses'] or 0:.2f}"),
            ("Profit/Loss", f"₹{profit:.2f}", 
             f"{profit_change:+.1f}%", f"₹{previous_profit:.2f}"),
            ("Invoices", str(current_sales['invoices'] or 0), 
             "", str(previous_sales['invoices'] or 0)),
            ("Avg Invoice", f"₹{current_sales['avg_invoice'] or 0:.2f}", 
             "", f"₹{previous_sales['avg_invoice'] or 0:.2f}"),
            ("New Customers", str(new_customers['count'] or 0), 
             "", "N/A"),
        ]
        
        columns = ('Metric', 'Current Month', 'Change', 'Previous Month')
        
        summary = f"Monthly Performance Summary\n"
        summary += f"Current Month: {current_month_start.strftime('%B %Y')}\n"
        summary += f"Previous Month: {previous_month_start.strftime('%B %Y')}\n"
        summary += f"Profit Margin: {(profit/(current_sales['sales'] or 1)*100 if current_sales['sales'] else 0):.1f}%"
        
        self.show_report_dialog("Monthly Summary Report", report_data, columns, summary)
    
    def generate_invoice_report(self):
        """Generate detailed invoice analysis"""
        # Get all invoices with details
        query = '''
            SELECT 
                i.invoice_number,
                i.date,
                c.name as customer,
                i.status,
                i.subtotal,
                i.tax_amount,
                i.total,
                GROUP_CONCAT(p.name, ', ') as products,
                COUNT(ii.id) as items_count
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
            LEFT JOIN products p ON ii.product_id = p.id
            GROUP BY i.id
            ORDER BY i.date DESC
            LIMIT 50
        '''
        
        rows = db.fetch_all(query)
        
        # Prepare data for display
        report_data = []
        for row in rows:
            products = row['products'] or 'Various items'
            if len(products) > 30:
                products = products[:27] + "..."
            
            report_data.append((
                row['invoice_number'],
                row['date'],
                row['customer'] or 'Walk-in',
                row['status'],
                f"₹{row['subtotal']:.2f}",
                f"₹{row['tax_amount']:.2f}",
                f"₹{row['total']:.2f}",
                row['items_count'],
                products
            ))
        
        # Calculate summary
        total_invoices = len(rows)
        pending_invoices = sum(1 for row in rows if row['status'] == 'pending')
        paid_invoices = sum(1 for row in rows if row['status'] == 'paid')
        total_amount = sum(row['total'] for row in rows)
        
        columns = ('Invoice #', 'Date', 'Customer', 'Status', 'Subtotal', 'Tax', 'Total', 'Items', 'Products')
        
        summary = f"Invoice Analysis Report\n"
        summary += f"Total Invoices: {total_invoices}\n"
        summary += f"Pending: {pending_invoices} | Paid: {paid_invoices}\n"
        summary += f"Total Amount: ₹{total_amount:.2f}"
        
        self.show_report_dialog("Invoice Analysis Report", report_data, columns, summary)
    
    def generate_product_sales_report(self):
        """Generate product-wise sales analysis"""
        query = '''
            SELECT 
                p.id,
                p.name,
                p.price,
                p.stock,
                COUNT(ii.id) as times_sold,
                SUM(ii.quantity) as total_quantity,
                SUM(ii.total) as total_revenue,
                AVG(ii.unit_price) as avg_selling_price
            FROM products p
            LEFT JOIN invoice_items ii ON p.id = ii.product_id
            LEFT JOIN invoices i ON ii.invoice_id = i.id AND i.status != 'cancelled'
            GROUP BY p.id
            ORDER BY total_revenue DESC NULLS LAST
        '''
        
        rows = db.fetch_all(query)
        
        # Prepare data for display
        report_data = []
        total_revenue = 0
        total_quantity = 0
        
        for row in rows:
            total_revenue += row['total_revenue'] or 0
            total_quantity += row['total_quantity'] or 0
            
            report_data.append((
                row['id'],
                row['name'],
                f"₹{row['price']:.2f}",
                row['stock'],
                row['times_sold'] or 0,
                row['total_quantity'] or 0,
                f"₹{row['total_revenue'] or 0:.2f}",
                f"₹{row['avg_selling_price'] or row['price']:.2f}"
            ))
        
        columns = ('ID', 'Product', 'Price', 'Stock', 'Times Sold', 'Total Qty', 'Total Revenue', 'Avg Price')
        
        summary = f"Product Sales Analysis\n"
        summary += f"Total Products: {len(rows)}\n"
        summary += f"Total Revenue: ₹{total_revenue:.2f}\n"
        summary += f"Total Quantity Sold: {total_quantity}\n"
        summary += f"Average Revenue per Product: ₹{total_revenue/len(rows) if rows else 0:.2f}"
        
        self.show_report_dialog("Product Sales Report", report_data, columns, summary)
    
    def calculate_change(self, current, previous):
        """Calculate percentage change"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100
    
    def export_to_csv(self, data, columns, title):
        """Export report data to CSV file"""
        try:
            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"{title.replace(' ', '_')}.csv"
            )
            
            if not filename:
                return
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(columns)
                
                # Write data
                for row in data:
                    writer.writerow(row)
            
            messagebox.showinfo("Export Successful", 
                              f"Report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
    def print_report(self, title, data, columns):
        """Print report to text file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"{title.replace(' ', '_')}.txt"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")
                f.write("=" * 50 + "\n\n")
                
                # Write columns
                header = " | ".join(columns)
                f.write(header + "\n")
                f.write("-" * len(header) + "\n")
                
                # Write data
                for row in data:
                    line = " | ".join(str(item) for item in row)
                    f.write(line + "\n")
            
            messagebox.showinfo("Print Successful", 
                              f"Report saved to:\n{filename}\n\nYou can print this file.")
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to save report: {str(e)}")
    
    def export_report(self, report_function):
        """Export report directly without showing dialog"""
        # This is a simplified export function
        messagebox.showinfo("Export", 
                          "Please generate the report first, then use the Export CSV button in the report window.")
    
    def export_all_data(self):
        """Export all database data to CSV files"""
        try:
            # Ask for directory
            directory = filedialog.askdirectory(title="Select directory to save exported data")
            if not directory:
                return
            
            # Export tables
            tables = ['customers', 'products', 'invoices', 'invoice_items', 'expenses', 'payments']
            
            for table in tables:
                try:
                    # Get data
                    rows = db.fetch_all(f'SELECT * FROM {table}')
                    if rows:
                        filename = os.path.join(directory, f'{table}.csv')
                        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                            # Get column names
                            if rows:
                                columns = list(rows[0].keys())
                                writer = csv.DictWriter(csvfile, fieldnames=columns)
                                writer.writeheader()
                                writer.writerows([dict(row) for row in rows])
                except Exception as e:
                    print(f"Error exporting {table}: {e}")
            
            messagebox.showinfo("Export Successful", 
                              f"All data exported to:\n{directory}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")