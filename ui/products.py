"""
ui/products.py - Product management module
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import db
from models import Product

class Products(ttk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.app = app
        self.current_product = None
        self.create_widgets()
        self.load_products()
    
    def create_widgets(self):
        """Create product management widgets"""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header with buttons
        header = ttk.Frame(main_container)
        header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header, text="Product Management", 
                 font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="➕ Add Product", 
                  command=self.add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh", 
                  command=self.load_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Low Stock", 
                  command=self.show_low_stock).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(main_container)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.filter_products())
        
        # Filter by type
        ttk.Label(search_frame, text="Type:", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(20, 0))
        self.type_filter = tk.StringVar(value="All")
        type_combo = ttk.Combobox(search_frame, textvariable=self.type_filter,
                                 values=["All", "Product", "Service"], 
                                 state="readonly", width=10)
        type_combo.pack(side=tk.LEFT, padx=5)
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_products())
        
        # Product list (Treeview)
        list_frame = ttk.LabelFrame(main_container, text="Product List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview with scrollbar
        columns = ('ID', 'Name', 'Type', 'Price', 'Stock', 'Description')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, 
                                        show='headings', height=20)
        
        # Define headings
        self.product_tree.heading('ID', text='ID')
        self.product_tree.heading('Name', text='Name')
        self.product_tree.heading('Type', text='Type')
        self.product_tree.heading('Price', text='Price (₹)')
        self.product_tree.heading('Stock', text='Stock')
        self.product_tree.heading('Description', text='Description')
        
        # Define columns
        self.product_tree.column('ID', width=50, anchor=tk.CENTER)
        self.product_tree.column('Name', width=150)
        self.product_tree.column('Type', width=80, anchor=tk.CENTER)
        self.product_tree.column('Price', width=80, anchor=tk.E)
        self.product_tree.column('Stock', width=60, anchor=tk.E)
        self.product_tree.column('Description', width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.product_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        self.product_tree.bind('<Double-1>', self.edit_selected_product)
        
        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Product", 
                                     command=self.edit_selected_product)
        self.context_menu.add_command(label="Delete Product", 
                                     command=self.delete_selected_product)
        self.context_menu.add_command(label="View Details", 
                                     command=self.view_product_details)
        self.product_tree.bind('<Button-3>', self.show_context_menu)
    
    def load_products(self):
        """Load products into the treeview"""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Load all products
        products = Product.get_all()
        
        for product in products:
            product_type = "Service" if product.is_service else "Product"
            stock_display = "N/A" if product.is_service else str(product.stock)
            
            # Color code low stock (for products only)
            tags = ()
            if not product.is_service and product.stock < 10:
                tags = ('low_stock',)
            
            self.product_tree.insert('', tk.END, values=(
                product.id,
                product.name,
                product_type,
                f"₹{product.price:.2f}",
                stock_display,
                product.description or ""
            ), tags=tags)
        
        # Configure tag for low stock
        self.product_tree.tag_configure('low_stock', foreground='red')
        
        # Update count label if exists
        if hasattr(self, 'count_label'):
            self.count_label.config(text=f"Total Products: {len(products)}")
    
    def filter_products(self):
        """Filter products based on search criteria"""
        search_term = self.search_var.get().lower()
        type_filter = self.type_filter.get()
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Load all products and filter
        products = Product.get_all()
        filtered_products = []
        
        for product in products:
            product_type = "Service" if product.is_service else "Product"
            
            # Apply type filter
            if type_filter != "All":
                if type_filter == "Service" and not product.is_service:
                    continue
                elif type_filter == "Product" and product.is_service:
                    continue
            
            # Apply search filter
            if search_term:
                if (search_term in product.name.lower() or 
                    search_term in (product.description or "").lower()):
                    filtered_products.append(product)
            else:
                filtered_products.append(product)
        
        # Display filtered products
        for product in filtered_products:
            product_type = "Service" if product.is_service else "Product"
            stock_display = "N/A" if product.is_service else str(product.stock)
            
            tags = ()
            if not product.is_service and product.stock < 10:
                tags = ('low_stock',)
            
            self.product_tree.insert('', tk.END, values=(
                product.id,
                product.name,
                product_type,
                f"₹{product.price:.2f}",
                stock_display,
                product.description or ""
            ), tags=tags)
    
    def on_product_select(self, event):
        """Handle product selection from treeview"""
        selection = self.product_tree.selection()
        if not selection:
            self.current_product = None
            return
        
        item = self.product_tree.item(selection[0])
        product_id = item['values'][0]
        self.current_product = Product.get_by_id(product_id)
    
    def add_product_dialog(self):
        """Open dialog to add new product"""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Product")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Form frame
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product Name
        ttk.Label(form_frame, text="Product Name *", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        
        # Product Type
        ttk.Label(form_frame, text="Product Type *", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(10, 5))
        type_var = tk.StringVar(value="Product")
        type_combo = ttk.Combobox(form_frame, textvariable=type_var,
                                 values=["Product", "Service"], 
                                 state="readonly", width=15)
        type_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Price
        ttk.Label(form_frame, text="Price (₹) *", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5))
        price_var = tk.DoubleVar(value=0.0)
        price_spin = ttk.Spinbox(form_frame, from_=0, to=1000000, 
                                textvariable=price_var, width=15)
        price_spin.grid(row=2, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Stock (only for products, not services)
        ttk.Label(form_frame, text="Initial Stock", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        stock_var = tk.IntVar(value=0)
        stock_spin = ttk.Spinbox(form_frame, from_=0, to=10000, 
                                textvariable=stock_var, width=15, state='normal')
        stock_spin.grid(row=3, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Description
        ttk.Label(form_frame, text="Description", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=(10, 5))
        desc_text = tk.Text(form_frame, height=5, width=30)
        desc_text.grid(row=4, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Update stock field based on type
        def update_stock_field(*args):
            if type_var.get() == "Service":
                stock_spin.config(state='disabled')
                stock_var.set(0)
            else:
                stock_spin.config(state='normal')
        
        type_var.trace('w', update_stock_field)
        update_stock_field()  # Initial update
        
        # Button frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_product():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Product name is required!")
                return
            
            try:
                price = price_var.get()
                if price < 0:
                    messagebox.showwarning("Validation", "Price cannot be negative!")
                    return
                
                # Create product
                product = Product(
                    name=name,
                    description=desc_text.get(1.0, tk.END).strip(),
                    price=price,
                    stock=stock_var.get(),
                    is_service=(type_var.get() == "Service")
                )
                
                product.save()
                
                # Refresh product list
                self.load_products()
                
                messagebox.showinfo("Success", "Product added successfully!")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid price and stock values!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save product: {str(e)}")
        
        ttk.Button(btn_frame, text="💾 Save Product", 
                  command=save_product, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Focus name entry
        name_entry.focus()
    
    def edit_selected_product(self, event=None):
        """Edit the selected product"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a product first!")
            return
        
        item = self.product_tree.item(selection[0])
        product_id = item['values'][0]
        
        # Get product from database
        product = Product.get_by_id(product_id)
        if not product:
            messagebox.showerror("Error", "Product not found!")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Product: {product.name}")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Form frame
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product Name
        ttk.Label(form_frame, text="Product Name *", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        name_var = tk.StringVar(value=product.name)
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        
        # Product Type (disabled for editing existing product)
        ttk.Label(form_frame, text="Product Type", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(10, 5))
        type_display = "Service" if product.is_service else "Product"
        ttk.Label(form_frame, text=type_display, 
                 font=('Segoe UI', 10)).grid(
            row=1, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Price
        ttk.Label(form_frame, text="Price (₹) *", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5))
        price_var = tk.DoubleVar(value=product.price)
        price_spin = ttk.Spinbox(form_frame, from_=0, to=1000000, 
                                textvariable=price_var, width=15)
        price_spin.grid(row=2, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Stock (only for products, not services)
        ttk.Label(form_frame, text="Current Stock", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        if product.is_service:
            ttk.Label(form_frame, text="N/A (Service)", 
                     font=('Segoe UI', 10)).grid(
                row=3, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        else:
            stock_var = tk.IntVar(value=product.stock)
            stock_spin = ttk.Spinbox(form_frame, from_=0, to=10000, 
                                    textvariable=stock_var, width=15)
            stock_spin.grid(row=3, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Description
        ttk.Label(form_frame, text="Description", 
                 font=('Segoe UI', 10, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=(10, 5))
        desc_text = tk.Text(form_frame, height=5, width=30)
        desc_text.grid(row=4, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        desc_text.insert(1.0, product.description or "")
        
        # Button frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_changes():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Product name is required!")
                return
            
            try:
                price = price_var.get()
                if price < 0:
                    messagebox.showwarning("Validation", "Price cannot be negative!")
                    return
                
                # Update product
                product.name = name
                product.description = desc_text.get(1.0, tk.END).strip()
                product.price = price
                
                if not product.is_service:
                    product.stock = stock_var.get()
                
                product.save()
                
                # Refresh product list
                self.load_products()
                
                messagebox.showinfo("Success", "Product updated successfully!")
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {str(e)}")
        
        ttk.Button(btn_frame, text="💾 Save Changes", 
                  command=save_changes, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        # Focus name entry
        name_entry.focus()
        name_entry.select_range(0, tk.END)
    
    def delete_selected_product(self):
        """Delete the selected product"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a product first!")
            return
        
        item = self.product_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        # Check if product is used in any invoices
        row = db.fetch_one('''
            SELECT COUNT(*) as count FROM invoice_items 
            WHERE product_id = ?
        ''', (product_id,))
        
        if row and row['count'] > 0:
            messagebox.showwarning("Cannot Delete", 
                                 f"Cannot delete '{product_name}' because it's used in {row['count']} invoice(s).\n\n"
                                 "You can mark it as inactive instead.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Are you sure you want to delete '{product_name}'?\n\n"
                                  "This action cannot be undone."):
            return
        
        try:
            # Delete product
            product = Product.get_by_id(product_id)
            if product:
                product.delete()
            
            # Refresh product list
            self.load_products()
            
            messagebox.showinfo("Success", "Product deleted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
    
    def view_product_details(self):
        """View details of selected product"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a product first!")
            return
        
        item = self.product_tree.item(selection[0])
        product_id = item['values'][0]
        
        # Get product from database
        product = Product.get_by_id(product_id)
        if not product:
            messagebox.showerror("Error", "Product not found!")
            return
        
        # Create details dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Product Details: {product.name}")
        dialog.geometry("400x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Details frame
        details_frame = ttk.Frame(dialog, padding=20)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Display product details
        details = [
            ("ID:", product.id),
            ("Name:", product.name),
            ("Type:", "Service" if product.is_service else "Product"),
            ("Price:", f"₹{product.price:.2f}"),
            ("Stock:", "N/A" if product.is_service else product.stock),
            ("Description:", product.description or "No description"),
            ("Created:", product.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(product, 'created_at') else "N/A"),
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(details_frame, text=label, 
                     font=('Segoe UI', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=5)
            ttk.Label(details_frame, text=str(value), 
                     font=('Segoe UI', 10)).grid(
                row=i, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Get usage statistics (if any)
        if not product.is_service:
            row = db.fetch_one('''
                SELECT SUM(quantity) as total_sold, 
                       COUNT(DISTINCT invoice_id) as invoice_count
                FROM invoice_items 
                WHERE product_id = ?
            ''', (product_id,))
            
            if row and (row['total_sold'] or row['invoice_count']):
                ttk.Label(details_frame, text="Usage Stats:", 
                         font=('Segoe UI', 10, 'bold')).grid(
                    row=len(details), column=0, sticky=tk.W, pady=(15, 5))
                
                stats_text = f"Total Sold: {row['total_sold'] or 0} units\n"
                stats_text += f"In Invoices: {row['invoice_count'] or 0}"
                
                ttk.Label(details_frame, text=stats_text, 
                         font=('Segoe UI', 10)).grid(
                    row=len(details), column=1, sticky=tk.W, pady=(15, 5), padx=(10, 0))
        
        # Close button
        ttk.Button(details_frame, text="Close", 
                  command=dialog.destroy).grid(
            row=len(details)+1, column=0, columnspan=2, pady=20)
    
    def show_low_stock(self):
        """Show products with low stock"""
        # Filter to show only products with low stock
        self.type_filter.set("Product")
        self.search_var.set("")
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Load products with low stock
        products = Product.get_all()
        low_stock_count = 0
        
        for product in products:
            if product.is_service or product.stock >= 10:
                continue
            
            product_type = "Product"
            stock_display = str(product.stock)
            
            self.product_tree.insert('', tk.END, values=(
                product.id,
                product.name,
                product_type,
                f"₹{product.price:.2f}",
                stock_display,
                product.description or ""
            ), tags=('low_stock',))
            
            low_stock_count += 1
        
        if low_stock_count == 0:
            messagebox.showinfo("Low Stock", "No products with low stock (less than 10 units).")
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.product_tree.identify_row(event.y)
        if item:
            self.product_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)