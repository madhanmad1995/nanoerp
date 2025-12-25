"""
expenses.py - Expense tracking module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime, date, timedelta
from database import db

class Expenses(ttk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.current_expense = None
        self.create_widgets()
        self.load_expenses()
    
    def create_widgets(self):
        """Create expense management widgets"""
        # Main container
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane - Expense list
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right pane - Expense details
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # Left pane content
        left_top = ttk.Frame(left_frame)
        left_top.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(left_top, text="Expenses", font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)
        
        # Filter frame
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT)
        self.category_filter_var = tk.StringVar(value="All")
        
        # Get unique categories
        categories = ["All"]
        rows = db.fetch_all('SELECT DISTINCT category FROM expenses WHERE category IS NOT NULL')
        categories.extend([row['category'] for row in rows])
        
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_filter_var, 
                                     values=categories, state="readonly", width=15)
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_expenses())
        
        # Month filter
        ttk.Label(filter_frame, text="Month:").pack(side=tk.LEFT, padx=(20, 0))
        self.month_filter_var = tk.StringVar(value="All")
        months = ["All", "This Month", "Last Month", "Last 3 Months"]
        month_combo = ttk.Combobox(filter_frame, textvariable=self.month_filter_var, 
                                  values=months, state="readonly", width=15)
        month_combo.pack(side=tk.LEFT, padx=5)
        month_combo.bind('<<ComboboxSelected>>', lambda e: self.load_expenses())
        
        # Buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="➕ New Expense", 
                  command=self.new_expense, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Refresh", 
                  command=self.load_expenses).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📊 Quick Stats", 
                  command=self.show_quick_stats).pack(side=tk.LEFT, padx=2)
        
        # Expense list (Treeview)
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview with scrollbar
        columns = ('ID', 'Date', 'Category', 'Amount', 'Description')
        self.expense_tree = ttk.Treeview(list_frame, columns=columns, 
                                        show='headings', height=20)
        
        # Define headings
        self.expense_tree.heading('ID', text='ID')
        self.expense_tree.heading('Date', text='Date')
        self.expense_tree.heading('Category', text='Category')
        self.expense_tree.heading('Amount', text='Amount (₹)')
        self.expense_tree.heading('Description', text='Description')
        
        # Define columns
        self.expense_tree.column('ID', width=50, anchor=tk.CENTER)
        self.expense_tree.column('Date', width=80)
        self.expense_tree.column('Category', width=100)
        self.expense_tree.column('Amount', width=90, anchor=tk.E)
        self.expense_tree.column('Description', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.expense_tree.yview)
        self.expense_tree.configure(yscrollcommand=scrollbar.set)
        
        self.expense_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.expense_tree.bind('<<TreeviewSelect>>', self.on_expense_select)
        
        # Right pane content - Expense details form
        detail_frame = ttk.LabelFrame(right_frame, text="Expense Details", padding=15)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form fields
        row = 0
        
        # Date
        ttk.Label(detail_frame, text="Date *", font=('Segoe UI', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(detail_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=row, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        row += 1
        
        # Category
        ttk.Label(detail_frame, text="Category *", font=('Segoe UI', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        
        category_frame = ttk.Frame(detail_frame)
        category_frame.grid(row=row, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                          values=self.get_category_suggestions(), width=20)
        self.category_combo.pack(side=tk.LEFT)
        
        ttk.Button(category_frame, text="➕", 
                  command=self.add_new_category, width=3).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Amount
        ttk.Label(detail_frame, text="Amount (₹) *", font=('Segoe UI', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        self.amount_var = tk.DoubleVar(value=0.0)
        self.amount_spin = ttk.Spinbox(detail_frame, from_=0, to=1000000, 
                                      textvariable=self.amount_var, width=15)
        self.amount_spin.grid(row=row, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        row += 1
        
        # Payment Method
        ttk.Label(detail_frame, text="Payment Method", font=('Segoe UI', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        self.payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(detail_frame, textvariable=self.payment_var, 
                                    values=["Cash", "Bank Transfer", "Card", "Digital", "Other"], 
                                    width=15, state="readonly")
        payment_combo.grid(row=row, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        row += 1
        
        # Description
        ttk.Label(detail_frame, text="Description", font=('Segoe UI', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        self.description_text = tk.Text(detail_frame, height=4, width=40)
        self.description_text.grid(row=row, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        row += 1
        
        # Action buttons
        btn_frame = ttk.Frame(detail_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Save Expense", 
                                  command=self.save_expense, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🗑️ Clear Form", 
                                   command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(btn_frame, text="❌ Delete Expense", 
                                    command=self.delete_expense, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Expense statistics
        stats_frame = ttk.LabelFrame(right_frame, text="Expense Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="This Month: ₹0.00\nAll Time: ₹0.00")
        self.stats_label.pack()
        
        # Update statistics
        self.update_statistics()
    
    def get_category_suggestions(self):
        """Get category suggestions from existing expenses"""
        categories = []
        rows = db.fetch_all('''
            SELECT category, COUNT(*) as count 
            FROM expenses 
            WHERE category IS NOT NULL 
            GROUP BY category 
            ORDER BY count DESC
            LIMIT 10
        ''')
        
        for row in rows:
            categories.append(row['category'])
        
        # Add common categories if not present
        common_categories = [
            "Rent", "Utilities", "Supplies", "Marketing", 
            "Transportation", "Meals", "Equipment", "Software",
            "Taxes", "Insurance", "Salaries", "Repairs"
        ]
        
        for cat in common_categories:
            if cat not in categories:
                categories.append(cat)
        
        return categories
    
    def load_expenses(self):
        """Load expenses into the treeview"""
        # Clear existing items
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # Build WHERE clause based on filters
        where_clauses = []
        params = []
        
        # Category filter
        category_filter = self.category_filter_var.get()
        if category_filter != "All":
            where_clauses.append("category = ?")
            params.append(category_filter)
        
        # Date filter
        month_filter = self.month_filter_var.get()
        today = date.today()
        
        if month_filter == "This Month":
            first_day = today.replace(day=1)
            where_clauses.append("date >= ?")
            params.append(first_day)
        elif month_filter == "Last Month":
            first_day_last = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last = today.replace(day=1) - timedelta(days=1)
            where_clauses.append("date >= ? AND date <= ?")
            params.extend([first_day_last, last_day_last])
        elif month_filter == "Last 3 Months":
            three_months_ago = today - timedelta(days=90)
            where_clauses.append("date >= ?")
            params.append(three_months_ago)
        
        # Build query
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f'''
            SELECT id, date, category, amount, description
            FROM expenses
            WHERE {where_clause}
            ORDER BY date DESC, id DESC
        '''
        
        rows = db.fetch_all(query, params)
        
        # Add to treeview
        for row in rows:
            description = row['description'] or ""
            if len(description) > 30:
                description = description[:27] + "..."
            
            self.expense_tree.insert('', tk.END, values=(
                row['id'],
                row['date'],
                row['category'],
                f"₹{row['amount']:.2f}",
                description
            ))
    
    def on_expense_select(self, event):
        """Handle expense selection from treeview"""
        selection = self.expense_tree.selection()
        if not selection:
            return
        
        # Get selected expense ID
        item = self.expense_tree.item(selection[0])
        expense_id = item['values'][0]
        
        # Load expense data
        self.load_expense_data(expense_id)
    
    def load_expense_data(self, expense_id):
        """Load expense data into form"""
        # Get expense from database
        row = db.fetch_one('SELECT * FROM expenses WHERE id=?', (expense_id,))
        
        if not row:
            return
        
        self.current_expense = row
        
        # Update form fields
        self.date_var.set(row['date'])
        self.category_var.set(row['category'] or "")
        self.amount_var.set(row['amount'])
        self.payment_var.set(row['payment_method'] or "Cash")
        
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, row['description'] or "")
        
        # Enable buttons
        self.save_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)
    
    def update_statistics(self):
        """Update expense statistics"""
        today = date.today()
        first_day = today.replace(day=1)
        
        # This month's total
        row = db.fetch_one('SELECT SUM(amount) as total FROM expenses WHERE date >= ?', 
                          (first_day,))
        month_total = row['total'] or 0
        
        # All time total
        row = db.fetch_one('SELECT SUM(amount) as total FROM expenses')
        all_total = row['total'] or 0
        
        self.stats_label.config(
            text=f"This Month: ₹{month_total:.2f}\nAll Time: ₹{all_total:.2f}"
        )
    
    def add_new_category(self):
        """Add new category to suggestions"""
        from tkinter import simpledialog
        new_category = simpledialog.askstring("New Category", "Enter new category name:")
        if new_category:
            # Update combobox values
            current_values = list(self.category_combo['values'])
            if new_category not in current_values:
                current_values.append(new_category)
                self.category_combo['values'] = current_values
            
            # Set as current value
            self.category_var.set(new_category)
    
    def new_expense(self):
        """Create new expense form"""
        self.current_expense = None
        self.clear_form()
        self.save_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.DISABLED)
        self.category_combo.focus()
    
    def clear_form(self):
        """Clear the form"""
        self.current_expense = None
        self.date_var.set(date.today().strftime("%Y-%m-%d"))
        self.category_var.set("")
        self.amount_var.set(0.0)
        self.payment_var.set("Cash")
        self.description_text.delete(1.0, tk.END)
        self.save_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.expense_tree.selection_remove(self.expense_tree.selection())
        
        # Update category suggestions
        self.category_combo['values'] = self.get_category_suggestions()
    
    def save_expense(self):
        """Save expense data"""
        # Validate required fields
        if not self.date_var.get():
            messagebox.showwarning("Validation Error", "Date is required!")
            return
        
        if not self.category_var.get():
            messagebox.showwarning("Validation Error", "Category is required!")
            return
        
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
        except ValueError as e:
            messagebox.showwarning("Validation Error", "Please enter a valid amount!")
            return
        
        # Parse date
        try:
            expense_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter a valid date (YYYY-MM-DD)!")
            return
        
        # Prepare data
        category = self.category_var.get().strip()
        amount = float(self.amount_var.get())
        payment_method = self.payment_var.get()
        description = self.description_text.get(1.0, tk.END).strip()
        
        try:
            if self.current_expense:
                # Update existing expense
                db.execute('''
                    UPDATE expenses 
                    SET date=?, category=?, amount=?, payment_method=?, description=?
                    WHERE id=?
                ''', (expense_date, category, amount, payment_method, 
                      description, self.current_expense['id']))
            else:
                # Insert new expense
                db.execute('''
                    INSERT INTO expenses (date, category, amount, payment_method, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (expense_date, category, amount, payment_method, description))
            
            # Show success message
            action = "updated" if self.current_expense else "created"
            messagebox.showinfo("Success", f"Expense {action} successfully!")
            
            # Refresh list and clear form
            self.load_expenses()
            self.clear_form()
            self.update_statistics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense: {str(e)}")
    
    def delete_expense(self):
        """Delete selected expense"""
        if not self.current_expense:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Delete expense from {self.current_expense['date']}?\n\n"
                                  "This action cannot be undone."):
            return
        
        try:
            # Delete expense
            db.execute('DELETE FROM expenses WHERE id=?', (self.current_expense['id'],))
            
            # Show success message
            messagebox.showinfo("Success", "Expense deleted successfully!")
            
            # Refresh list and clear form
            self.load_expenses()
            self.clear_form()
            self.update_statistics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete expense: {str(e)}")
    
    def show_quick_stats(self):
        """Show quick expense statistics"""
        from datetime import date, timedelta
        
        today = date.today()
        first_day = today.replace(day=1)
        
        # Get monthly stats by category
        rows = db.fetch_all('''
            SELECT category, SUM(amount) as total
            FROM expenses 
            WHERE date >= ?
            GROUP BY category
            ORDER BY total DESC
        ''', (first_day,))
        
        # Get today's total
        row_today = db.fetch_one('''
            SELECT SUM(amount) as total
            FROM expenses 
            WHERE date = ?
        ''', (today,))
        
        # Get top categories all time
        rows_all = db.fetch_all('''
            SELECT category, SUM(amount) as total
            FROM expenses 
            GROUP BY category
            ORDER BY total DESC
            LIMIT 5
        ''')
        
        stats_text = "💰 Expense Statistics\n"
        stats_text += "=" * 30 + "\n"
        stats_text += f"This Month: ₹{sum(row['total'] for row in rows):.2f}\n"
        stats_text += f"Today: ₹{row_today['total'] or 0:.2f}\n\n"
        
        stats_text += "Top Categories This Month:\n"
        for row in rows[:5]:  # Top 5
            stats_text += f"  {row['category']}: ₹{row['total']:.2f}\n"
        
        stats_text += "\nAll Time Top Categories:\n"
        for row in rows_all:
            stats_text += f"  {row['category']}: ₹{row['total']:.2f}\n"
        
        messagebox.showinfo("Expense Statistics", stats_text)