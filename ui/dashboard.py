"""
dashboard.py - Dashboard showing business overview
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from database import db

class Dashboard(ttk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Dashboard", style='PageTitle.TLabel').pack(side=tk.LEFT)
        
        refresh_btn = ttk.Button(header_frame, text="🔄 Refresh", command=self.refresh_data)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Stats cards
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.stats_vars = {
            'monthly_sales': tk.StringVar(value="₹0.00"),
            'pending_invoices': tk.StringVar(value="0"),
            'total_customers': tk.StringVar(value="0"),
            'total_products': tk.StringVar(value="0")
        }
        
        stats_cards = [
            ("💰 Monthly Sales", self.stats_vars['monthly_sales'], "#4CAF50"),
            ("📄 Pending Invoices", self.stats_vars['pending_invoices'], "#FF9800"),
            ("👥 Total Customers", self.stats_vars['total_customers'], "#2196F3"),
            ("📦 Total Products", self.stats_vars['total_products'], "#9C27B0")
        ]
        
        for i, (title, var, color) in enumerate(stats_cards):
            card = ttk.LabelFrame(stats_frame, text=title, padding=10)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            ttk.Label(card, textvariable=var, font=('Segoe UI', 20, 'bold'), 
                     foreground=color).pack()
            stats_frame.columnconfigure(i, weight=1)
        
        # Quick Actions
        actions_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        
        actions = [
            ("📝 Create Invoice", self.create_invoice),
            ("➕ Add Customer", self.add_customer),
            ("🛒 Add Product", self.add_product),
            ("💰 Record Expense", self.record_expense),
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = ttk.Button(actions_frame, text=text, command=command, width=20)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            actions_frame.columnconfigure(i%2, weight=1)
        
        # Recent Activity
        activity_frame = ttk.LabelFrame(main_frame, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True)
        
        # Recent Invoices
        invoices_frame = ttk.Frame(activity_frame)
        invoices_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(invoices_frame, text="Recent Invoices", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        columns = ('ID', 'Date', 'Customer', 'Amount', 'Status')
        self.invoice_tree = ttk.Treeview(invoices_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(invoices_frame, orient=tk.VERTICAL, command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        self.invoice_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Recent Expenses
        expenses_frame = ttk.Frame(activity_frame)
        expenses_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(expenses_frame, text="Recent Expenses", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        columns = ('ID', 'Date', 'Category', 'Amount')
        self.expense_tree = ttk.Treeview(expenses_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.expense_tree.heading(col, text=col)
            self.expense_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(expenses_frame, orient=tk.VERTICAL, command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=scrollbar.set)
        
        self.expense_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            # Calculate monthly sales
            first_day = date.today().replace(day=1)
            row = db.fetch_one('''
                SELECT SUM(total) as total FROM invoices 
                WHERE date >= ? AND status != 'cancelled'
            ''', (first_day.strftime("%Y-%m-%d"),))
            self.stats_vars['monthly_sales'].set(f"₹{row['total'] or 0:.2f}")
            
            # Pending invoices
            row = db.fetch_one('SELECT COUNT(*) as count FROM invoices WHERE status="pending"')
            self.stats_vars['pending_invoices'].set(row['count'])
            
            # Total customers
            row = db.fetch_one('SELECT COUNT(*) as count FROM customers')
            self.stats_vars['total_customers'].set(row['count'])
            
            # Total products
            row = db.fetch_one('SELECT COUNT(*) as count FROM products')
            self.stats_vars['total_products'].set(row['count'])
            
            # Load recent invoices
            for item in self.invoice_tree.get_children():
                self.invoice_tree.delete(item)
            
            rows = db.fetch_all('''
                SELECT i.id, i.date, c.name as customer, i.total, i.status
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                ORDER BY i.date DESC LIMIT 10
            ''')
            
            for row in rows:
                self.invoice_tree.insert('', tk.END, values=(
                    row['id'], row['date'], row['customer'] or 'Walk-in',
                    f"₹{row['total']:.2f}", row['status']
                ))
            
            # Load recent expenses
            for item in self.expense_tree.get_children():
                self.expense_tree.delete(item)
            
            rows = db.fetch_all('''
                SELECT id, date, category, amount
                FROM expenses
                ORDER BY date DESC LIMIT 10
            ''')
            
            for row in rows:
                self.expense_tree.insert('', tk.END, values=(
                    row['id'], row['date'], row['category'],
                    f"₹{row['amount']:.2f}"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")
    
    def create_invoice(self):
        """Navigate to create invoice"""
        if self.app:
            self.app.show_invoices()
    
    def add_customer(self):
        """Navigate to add customer"""
        if self.app:
            self.app.show_customers()
    
    def add_product(self):
        """Navigate to add product"""
        if self.app:
            self.app.show_products()
    
    def record_expense(self):
        """Navigate to record expense"""
        if self.app:
            self.app.show_expenses()