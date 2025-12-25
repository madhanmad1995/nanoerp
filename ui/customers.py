"""
customers.py - Customer management module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models import Customer
from database import db

class Customers(ttk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.current_customer = None
        self.create_widgets()
        self.load_customers()
    
    def create_widgets(self):
        """Create customer management widgets"""
        # Main container with left and right panes
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane - List of customers
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right pane - Customer details
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # Left pane content
        left_top = ttk.Frame(left_frame)
        left_top.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(left_top, text="Customers", font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)
        
        # Search box
        search_frame = ttk.Frame(left_top)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_customers())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="➕ New Customer", 
                  command=self.new_customer, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Refresh", 
                  command=self.load_customers).pack(side=tk.LEFT, padx=2)
        
        # Customer list (Treeview)
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview with scrollbar
        columns = ('ID', 'Name', 'Phone', 'Email')
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, 
                                         show='headings', height=20)
        
        # Define headings
        self.customer_tree.heading('ID', text='ID')
        self.customer_tree.heading('Name', text='Name')
        self.customer_tree.heading('Phone', text='Phone')
        self.customer_tree.heading('Email', text='Email')
        
        # Define columns
        self.customer_tree.column('ID', width=50, anchor=tk.CENTER)
        self.customer_tree.column('Name', width=150)
        self.customer_tree.column('Phone', width=100)
        self.customer_tree.column('Email', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        
        # Right pane content - Customer details form
        detail_frame = ttk.LabelFrame(right_frame, text="Customer Details", padding=15)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form fields
        ttk.Label(detail_frame, text="Name *", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(detail_frame, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        
        ttk.Label(detail_frame, text="Email", font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(detail_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        ttk.Label(detail_frame, text="Phone", font=('Segoe UI', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(detail_frame, textvariable=self.phone_var, width=40)
        self.phone_entry.grid(row=2, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        ttk.Label(detail_frame, text="Address", font=('Segoe UI', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        self.address_text = tk.Text(detail_frame, height=4, width=40)
        self.address_text.grid(row=3, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Action buttons
        btn_frame = ttk.Frame(detail_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Save Customer", 
                                  command=self.save_customer, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🗑️ Clear Form", 
                                   command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(btn_frame, text="❌ Delete Customer", 
                                    command=self.delete_customer, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Customer statistics
        stats_frame = ttk.LabelFrame(right_frame, text="Customer Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="Select a customer to view statistics")
        self.stats_label.pack()
    
    def load_customers(self):
        """Load customers into the treeview"""
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get search term
        search_term = self.search_var.get().lower()
        
        # Get all customers
        customers = Customer.get_all()
        
        # Filter by search term if provided
        if search_term:
            customers = [c for c in customers if 
                        search_term in c.name.lower() or 
                        search_term in (c.email or "").lower() or
                        search_term in (c.phone or "").lower()]
        
        # Add to treeview
        for customer in customers:
            self.customer_tree.insert('', tk.END, values=(
                customer.id,
                customer.name,
                customer.phone or "",
                customer.email or ""
            ))
    
    def on_customer_select(self, event):
        """Handle customer selection from treeview"""
        selection = self.customer_tree.selection()
        if not selection:
            return
        
        # Get selected customer ID
        item = self.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        
        # Load customer data
        self.load_customer_data(customer_id)
    
    def load_customer_data(self, customer_id):
        """Load customer data into form"""
        customer = Customer.get_by_id(customer_id)
        if not customer:
            return
        
        self.current_customer = customer
        
        # Update form fields
        self.name_var.set(customer.name)
        self.email_var.set(customer.email or "")
        self.phone_var.set(customer.phone or "")
        
        self.address_text.delete(1.0, tk.END)
        self.address_text.insert(1.0, customer.address or "")
        
        # Enable buttons
        self.save_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)
        
        # Update statistics
        self.update_customer_stats(customer_id)
    
    def update_customer_stats(self, customer_id):
        """Update customer statistics"""
        from database import db
        
        # Get total invoices and amount
        row = db.fetch_one('''
            SELECT COUNT(*) as count, SUM(total) as total
            FROM invoices 
            WHERE customer_id = ?
        ''', (customer_id,))
        
        if row:
            count = row['count'] or 0
            total = row['total'] or 0
            
            self.stats_label.config(
                text=f"Total Invoices: {count}\nTotal Amount: ₹{total:.2f}"
            )
    
    def new_customer(self):
        """Create new customer form"""
        self.current_customer = None
        self.clear_form()
        self.save_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.DISABLED)
        self.name_entry.focus()
    
    def clear_form(self):
        """Clear the form"""
        self.current_customer = None
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_text.delete(1.0, tk.END)
        self.stats_label.config(text="Select a customer to view statistics")
        self.save_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.customer_tree.selection_remove(self.customer_tree.selection())
    
    def save_customer(self):
        """Save customer data"""
        # Validate required fields
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Customer name is required!")
            return
        
        # Create or update customer
        customer = self.current_customer or Customer()
        customer.name = name
        customer.email = self.email_var.get().strip()
        customer.phone = self.phone_var.get().strip()
        customer.address = self.address_text.get(1.0, tk.END).strip()
        
        try:
            customer.save()
            
            # Show success message
            action = "updated" if self.current_customer else "created"
            messagebox.showinfo("Success", f"Customer {action} successfully!")
            
            # Refresh list and clear form
            self.load_customers()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save customer: {str(e)}")
    
    def delete_customer(self):
        """Delete selected customer"""
        if not self.current_customer:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Delete customer '{self.current_customer.name}'?\n\n"
                                  "This action cannot be undone."):
            return
        
        try:
            # Check if customer has invoices
            row = db.fetch_one('SELECT COUNT(*) as count FROM invoices WHERE customer_id=?', 
                              (self.current_customer.id,))
            
            if row and row['count'] > 0:
                if not messagebox.askyesno("Warning", 
                                          "This customer has invoices.\n"
                                          "Deleting will remove customer information from invoices.\n"
                                          "Continue anyway?"):
                    return
            
            # Delete customer
            self.current_customer.delete()
            
            # Show success message
            messagebox.showinfo("Success", "Customer deleted successfully!")
            
            # Refresh list and clear form
            self.load_customers()
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")
    
    def get_selected_customer_id(self):
        """Get ID of selected customer"""
        selection = self.customer_tree.selection()
        if selection:
            item = self.customer_tree.item(selection[0])
            return item['values'][0]
        return None