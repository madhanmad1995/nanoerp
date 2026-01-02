"""
invoices.py - Invoice management module with searchable customer dropdown
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import re
from models import Invoice, InvoiceItem, Customer, Product
from database import db

class AutoCompleteCombobox(ttk.Combobox):
    """Custom combobox with improved autocomplete functionality"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Use tk.StringVar for the textvariable
        self.var = tk.StringVar()
        self.configure(textvariable=self.var)
        
        self.original_values = []
        
        # Bind events for autocomplete
        self.bind('<KeyRelease>', self._on_keyrelease)
        self.bind('<FocusIn>', self._on_focusin)
        self.bind('<FocusOut>', self._on_focusout)
        self.bind('<Tab>', self._on_tab)
        self.bind('<Down>', self._on_down)
        self.bind('<Return>', self._on_return)
        
        # Track the last key to avoid infinite loops
        self.last_key = None
    
    def set_values(self, values):
        """Set the list of values for autocomplete"""
        self.original_values = list(values)
        self['values'] = self.original_values
    
    def _on_keyrelease(self, event):
        """Handle key release for autocomplete"""
        # Store the key
        self.last_key = event.keysym
        
        # Skip if it's a navigation key or control key
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R'):
            return
        
        value = self.var.get()
        
        if value == '':
            self['values'] = self.original_values
            # Don't post dropdown on empty, let user click down arrow
        else:
            # Filter values based on input (case insensitive)
            filtered = []
            value_lower = value.lower()
            for item in self.original_values:
                if value_lower in item.lower():
                    filtered.append(item)
            
            self['values'] = filtered
            
            # Show dropdown if there are matches
            if filtered:
                # Post the dropdown only if not deleting
                if event.keysym not in ('BackSpace', 'Delete'):
                    # Use after to avoid recursion issues
                    self.after(10, self._show_dropdown)
    
    def _show_dropdown(self):
        """Show dropdown programmatically"""
        if self['values']:
            # This triggers the dropdown to appear
            self.event_generate('<Button-1>')
            # Focus on the combobox to keep typing
            self.focus_set()
    
    def _on_focusin(self, event):
        """Show dropdown when focused"""
        if self.var.get() == '':
            self['values'] = self.original_values
            # Don't auto-show dropdown on focus, let user click
    
    def _on_focusout(self, event):
        """Handle focus out"""
        # Clear any temporary values
        pass
    
    def _on_tab(self, event):
        """Handle tab key - move to next widget"""
        # Let the default tab handling work
        return 'break'  # Prevent default behavior
    
    def _on_return(self, event):
        """Handle return key"""
        # Select the current value and close dropdown
        self.selection_clear()
        return 'break'
    
    def _on_down(self, event):
        """Handle down arrow - show dropdown"""
        # Post dropdown
        if self['values']:
            self.event_generate('<Button-1>')
        return 'break'

class ProfessionalSearchCombobox(ttk.Frame):
    """Professional search combobox with dropdown and clear button"""
    
    def __init__(self, parent, values=None, placeholder="Search...", **kwargs):
        super().__init__(parent, **kwargs)
        self.values = values or []
        self.filtered_values = []
        self.placeholder = placeholder
        
        # Create the combobox
        self.var = tk.StringVar()
        self.combo = ttk.Combobox(self, textvariable=self.var, state='normal')
        self.combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Clear button
        self.clear_btn = ttk.Button(self, text="✕", width=3, 
                                   command=self.clear_search, state=tk.DISABLED)
        self.clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Search button
        self.search_btn = ttk.Button(self, text="🔍", width=3,
                                    command=self.show_search_dialog)
        self.search_btn.pack(side=tk.RIGHT)
        
        # Setup values
        if self.values:
            self.combo['values'] = self.values
        
        # Bind events
        self.var.trace('w', self.on_text_change)
        self.combo.bind('<KeyRelease>', self.on_key_release)
        self.combo.bind('<FocusIn>', self.on_focus_in)
        self.combo.bind('<FocusOut>', self.on_focus_out)
        self.combo.bind('<Down>', self.on_down_arrow)
        
        # Track if we're showing placeholder
        self.showing_placeholder = False
        self.set_placeholder()
    
    def set_placeholder(self):
        """Set placeholder text"""
        if not self.var.get():
            self.combo.configure(foreground='gray')
            self.var.set(self.placeholder)
            self.showing_placeholder = True
    
    def clear_placeholder(self):
        """Clear placeholder text"""
        if self.showing_placeholder:
            self.combo.configure(foreground='black')
            self.var.set('')
            self.showing_placeholder = False
    
    def on_focus_in(self, event):
        """Handle focus in"""
        if self.showing_placeholder:
            self.clear_placeholder()
    
    def on_focus_out(self, event):
        """Handle focus out"""
        if not self.var.get():
            self.set_placeholder()
    
    def on_text_change(self, *args):
        """Handle text change"""
        value = self.var.get()
        
        if self.showing_placeholder:
            return
        
        # Enable/disable clear button
        if value:
            self.clear_btn.config(state=tk.NORMAL)
        else:
            self.clear_btn.config(state=tk.DISABLED)
    
    def on_key_release(self, event):
        """Handle key release for search"""
        if self.showing_placeholder:
            return
        
        value = self.var.get().lower()
        
        if not value:
            self.combo['values'] = self.values
            return
        
        # Filter values
        self.filtered_values = [
            item for item in self.values 
            if value in item.lower()
        ]
        
        # Update dropdown
        self.combo['values'] = self.filtered_values
        
        # Show dropdown if there are results
        if self.filtered_values and event.keysym not in ('Up', 'Down', 'Left', 'Right', 'Return', 'Tab'):
            self.combo.event_generate('<Down>')
    
    def on_down_arrow(self, event):
        """Handle down arrow to show dropdown"""
        if not self.combo['values']:
            self.combo['values'] = self.values
        return None  # Let default behavior happen
    
    def clear_search(self):
        """Clear search text"""
        self.var.set('')
        self.combo['values'] = self.values
        self.clear_btn.config(state=tk.DISABLED)
        self.combo.focus_set()
    
    def show_search_dialog(self):
        """Show advanced search dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Advanced Customer Search")
        dialog.geometry("600x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Search frame
        search_frame = ttk.Frame(dialog, padding=10)
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Search:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Results frame
        results_frame = ttk.Frame(dialog)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview with scrollbars
        columns = ('ID', 'Name', 'Phone', 'Email', 'Address')
        tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column('Name', width=150)
        tree.column('Email', width=150)
        tree.column('Address', width=200)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Load customers
        customers = Customer.get_all()
        
        def load_customers(customer_list=None):
            """Load customers into treeview"""
            for item in tree.get_children():
                tree.delete(item)
            
            customer_list = customer_list or customers
            
            for customer in customer_list:
                tree.insert('', tk.END, values=(
                    customer.id,
                    customer.name,
                    customer.phone or '',
                    customer.email or '',
                    customer.address or ''
                ))
        
        load_customers()
        
        def perform_search(*args):
            """Perform search based on criteria"""
            term = search_var.get().lower()
            
            if not term:
                load_customers(customers)
                return
            
            filtered = [
                c for c in customers
                if (term in c.name.lower() or
                    term in (c.phone or '').lower() or
                    term in (c.email or '').lower() or
                    term in (c.address or '').lower())
            ]
            
            load_customers(filtered)
        
        search_var.trace('w', perform_search)
        
        # Button frame
        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill=tk.X)
        
        def select_customer():
            """Select customer from search results"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Selection Required", "Please select a customer first!")
                return
            
            item = tree.item(selection[0])
            customer_id = item['values'][0]
            
            # Find and select the customer
            for customer in customers:
                if customer.id == customer_id:
                    # Create display string
                    display_string = f"{customer.name}"
                    if customer.phone:
                        display_string += f" 📞 {customer.phone}"
                    if customer.email:
                        display_string += f" ✉ {customer.email}"
                    display_string += f" (ID: {customer.id})"
                    
                    # Update the combobox
                    self.var.set(display_string)
                    self.showing_placeholder = False
                    self.combo.configure(foreground='black')
                    
                    # Call the parent's customer selection handler if it exists
                    parent = self.winfo_toplevel()
                    if hasattr(parent, 'on_customer_select'):
                        parent.on_customer_select(None)
                    elif hasattr(self.master, 'on_customer_select'):
                        self.master.on_customer_select(None)
                    
                    dialog.destroy()
                    return
        
        ttk.Button(btn_frame, text="Select", 
                  command=select_customer, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind double-click
        tree.bind('<Double-1>', lambda e: select_customer())
        
        # Focus search entry
        search_entry.focus_set()
    
    def get(self):
        """Get current value"""
        if self.showing_placeholder:
            return ''
        return self.var.get()
    
    def set(self, value):
        """Set current value"""
        if value:
            self.combo.configure(foreground='black')
            self.var.set(value)
            self.showing_placeholder = False
            self.clear_btn.config(state=tk.NORMAL)
        else:
            self.set_placeholder()

class Invoices(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_invoice = None
        self.invoice_items = []
        self.customer_map = {}  # Maps display string to customer object
        self.create_widgets()
        self.load_customers()
        self.load_invoices()
    
    def create_widgets(self):
        """Create invoice management widgets"""
        # Main container - Make sure it fills the parent
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane - Invoice list
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right pane - Invoice details
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # Left pane content
        left_top = ttk.Frame(left_frame)
        left_top.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(left_top, text="Invoices", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Filter frame
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, 
                                   values=["All", "pending", "paid", "cancelled"], 
                                   state="readonly", width=12)
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.load_invoices())
        # Payment method filter (only for paid invoices)
        ttk.Label(filter_frame, text="Payment Method:").pack(side=tk.LEFT, padx=(20, 0))
        self.payment_method_var = tk.StringVar(value="All")
        payment_methods = ["All", "Cash", "Card", "Credit", "UPI"]
        payment_combo = ttk.Combobox(filter_frame, textvariable=self.payment_method_var, 
                            values=payment_methods, state="readonly", width=12)
        payment_combo.pack(side=tk.LEFT, padx=5)
        payment_combo.bind('<<ComboboxSelected>>', lambda e: self.load_invoices())
        
        # Month filter
        ttk.Label(filter_frame, text="Month:").pack(side=tk.LEFT, padx=(20, 0))
        self.month_var = tk.StringVar(value="All")
        months = ["All", "This Month", "Last Month", "Last 3 Months"]
        month_combo = ttk.Combobox(filter_frame, textvariable=self.month_var, 
                                  values=months, state="readonly", width=15)
        month_combo.pack(side=tk.LEFT, padx=5)
        month_combo.bind('<<ComboboxSelected>>', lambda e: self.load_invoices())
        
        # Buttons frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="➕ New Invoice", 
                  command=self.new_invoice, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Refresh", 
                  command=self.load_invoices).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📊 Quick Stats", 
                  command=self.show_quick_stats).pack(side=tk.LEFT, padx=2)
        
        # Invoice list (Treeview)
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview with scrollbar
        columns = ('ID', 'Date', 'Customer', 'Amount', 'Status')
        self.invoice_tree = ttk.Treeview(list_frame, columns=columns, 
                                        show='headings', height=20)
        
        # Define headings
        self.invoice_tree.heading('ID', text='Invoice #')
        self.invoice_tree.heading('Date', text='Date')
        self.invoice_tree.heading('Customer', text='Customer')
        self.invoice_tree.heading('Amount', text='Amount (₹)')
        self.invoice_tree.heading('Status', text='Status')
        
        # Define columns
        self.invoice_tree.column('ID', width=80, anchor=tk.CENTER)
        self.invoice_tree.column('Date', width=80)
        self.invoice_tree.column('Customer', width=100)
        self.invoice_tree.column('Amount', width=90, anchor=tk.E)
        self.invoice_tree.column('Status', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        self.invoice_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.invoice_tree.bind('<<TreeviewSelect>>', self.on_invoice_select)
        
        # Right pane content - Invoice details
        detail_frame = ttk.LabelFrame(right_frame, text="Invoice Details", padding=15)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Invoice header
        header_frame = ttk.Frame(detail_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Invoice number and date
        ttk.Label(header_frame, text="Invoice #:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.invoice_num_var = tk.StringVar()
        self.invoice_num_entry = ttk.Entry(header_frame, textvariable=self.invoice_num_var, 
                                          width=15, state='readonly')
        self.invoice_num_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, text="Date:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(20, 0))
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(header_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, text="Due Date:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(20, 0))
        self.due_date_var = tk.StringVar(value=(date.today() + timedelta(days=30)).strftime("%Y-%m-%d"))
        self.due_date_entry = ttk.Entry(header_frame, textvariable=self.due_date_var, width=12)
        self.due_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Customer selection frame
        customer_frame = ttk.Frame(detail_frame)
        customer_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(customer_frame, text="Customer:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Professional search combobox
        self.customer_search = ProfessionalSearchCombobox(customer_frame, 
                                                         placeholder="Search customer by name, phone, or email...")
        self.customer_search.pack(fill=tk.X, pady=(5, 0))
        
        # Bind the professional combobox selection
        self.customer_search.combo.bind('<<ComboboxSelected>>', self.on_customer_select)
        
        # Add new customer button
        customer_btn_frame = ttk.Frame(customer_frame)
        customer_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(customer_btn_frame, text="➕ Add New Customer", 
                  command=self.add_new_customer_dialog, width=22).pack(side=tk.LEFT)
        ttk.Button(customer_btn_frame, text="👁️ View Selected", 
                  command=self.view_selected_customer, width=18).pack(side=tk.LEFT, padx=5)
        
        
        # Items list (Treeview)
        items_frame = ttk.LabelFrame(detail_frame, text="Items")
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8), padx=5)

        # Items toolbar
        items_toolbar = ttk.Frame(items_frame)
        items_toolbar.pack(fill=tk.X, padx=8, pady=6)
        
        ttk.Button(items_toolbar, text="➕ Add Item", 
                  command=self.add_item_dialog,width=12).pack(side=tk.LEFT)
        ttk.Button(items_toolbar, text="➖ Remove Selected", 
                  command=self.remove_selected_item,width=20).pack(side=tk.LEFT, padx=5)
        
        # Items treeview
        columns = ('Product', 'Description', 'Qty', 'Price', 'Total')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, 
                                      show='headings', height=5)
        self.items_tree.bind("<Double-1>", self.on_item_cell_double_click)
        
        # Define headings
        self.items_tree.heading('Product', text='Product')
        self.items_tree.heading('Description', text='Description')
        self.items_tree.heading('Qty', text='Qty')
        self.items_tree.heading('Price', text='Price (₹)')
        self.items_tree.heading('Total', text='Total (₹)')
        
        # Define columns
        self.items_tree.column('Product', width=100)
        self.items_tree.column('Description', width=180)
        self.items_tree.column('Qty', width=60, anchor=tk.E)
        self.items_tree.column('Price', width=80, anchor=tk.E)
        self.items_tree.column('Total', width=90, anchor=tk.E)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, 
                                 command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Totals frame (VERTICAL, RIGHT-ALIGNED)
        totals_frame = ttk.Frame(detail_frame)
        totals_frame.pack(fill=tk.X, pady=(0, 10))

        # Align totals to the right
        totals_inner = ttk.Frame(totals_frame)
        totals_inner.pack(anchor=tk.W, padx=10)

        # Row 0 — Subtotal
        ttk.Label(totals_inner, text="Subtotal :", font=('Arial', 10)).grid(
        row=0, column=0, sticky=tk.W, pady=3, padx=(0, 10)
        )
        self.subtotal_var = tk.StringVar(value="₹0.00")
        ttk.Label(totals_inner, textvariable=self.subtotal_var, font=('Arial', 10)).grid(
        row=0, column=1, sticky=tk.W, pady=3
        )
        # Row 1 — Discount
        discount_row = ttk.Frame(totals_inner)
        discount_row.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=3)

        ttk.Label(discount_row, text="Discount :", font=('Arial', 10)).pack(side=tk.LEFT)

        self.discount_type = tk.StringVar(value="percentage")
        discount_type_combo = ttk.Combobox(
            discount_row,
            textvariable=self.discount_type,
            values=["percentage", "amount"],
            state="readonly",
            width=10
        )
        discount_type_combo.pack(side=tk.LEFT, padx=5)

        self.discount_value = tk.DoubleVar(value=0.0)
        discount_spin = ttk.Spinbox(
            discount_row,
            from_=0,
            to=10000,
            textvariable=self.discount_value,
            width=8
        )
        discount_spin.pack(side=tk.LEFT, padx=5)

        self.discount_amount_var = tk.StringVar(value="₹0.00")
        ttk.Label(discount_row, textvariable=self.discount_amount_var).pack(side=tk.LEFT, padx=5)

        discount_type_combo.bind('<<ComboboxSelected>>', lambda e: self.calculate_totals())
        discount_spin.bind('<KeyRelease>', lambda e: self.calculate_totals())
        discount_spin.bind('<<Increment>>', lambda e: self.calculate_totals())
        discount_spin.bind('<<Decrement>>', lambda e: self.calculate_totals())

        # Row 2 — Tax
        tax_row = ttk.Frame(totals_inner)
        tax_row.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=3)

        ttk.Label(tax_row, text="Tax (%) :", font=('Arial', 10)).pack(side=tk.LEFT)
        self.tax_rate_var = tk.DoubleVar(value=18.0)
        tax_spin = ttk.Spinbox(
            tax_row,
            from_=0,
            to=100,
            textvariable=self.tax_rate_var,
            width=8
        )
        tax_spin.pack(side=tk.LEFT, padx=5)

        self.tax_amount_var = tk.StringVar(value="₹0.00")
        ttk.Label(tax_row, textvariable=self.tax_amount_var).pack(side=tk.LEFT, padx=5)

        tax_spin.bind('<KeyRelease>', lambda e: self.calculate_totals())
        tax_spin.bind('<<Increment>>', lambda e: self.calculate_totals())
        tax_spin.bind('<<Decrement>>', lambda e: self.calculate_totals())


        # Separator
        ttk.Separator(totals_inner, orient=tk.HORIZONTAL).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=6
        )

        # Row 4 — Total
        ttk.Label(totals_inner, text="Total :", font=('Arial', 11, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=4, padx=(0, 10)
        )
        self.total_var = tk.StringVar(value="₹0.00")
        ttk.Label(
            totals_inner,
            textvariable=self.total_var,
            font=('Arial', 11, 'bold'),
            foreground='green'
        ).grid(row=4, column=1, sticky=tk.W, pady=4)

        # Action buttons
        btn_frame = ttk.Frame(detail_frame)
        btn_frame.pack(fill=tk.X)
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Save Invoice", 
                                  command=self.save_invoice, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🗑️ Clear Form", 
                                   command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(btn_frame, text="❌ Delete Invoice", 
                                    command=self.delete_invoice, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.print_btn = ttk.Button(btn_frame, text="🖨️ Print Invoice", 
                                   command=self.print_invoice, state=tk.DISABLED)
        self.print_btn.pack(side=tk.LEFT, padx=5)
        
        self.mark_paid_btn = ttk.Button(btn_frame, text="💰 Mark as Paid", 
                                       command=self.mark_as_paid, state=tk.DISABLED)
        self.mark_paid_btn.pack(side=tk.LEFT, padx=5)
        
        # Pack the main frame to ensure it's visible
        self.pack(fill=tk.BOTH, expand=True)
    
    def load_customers(self):
        """Load customers into the dropdown with autocomplete"""
        customers = Customer.get_all()
        customer_list = ["Walk-in Customer"]  # Default option
        self.customer_map = {"Walk-in Customer": None}
        
        for customer in customers:
            # Create display string with name and phone
            if customer.phone:
                display_string = f"{customer.name} 📞 {customer.phone}"
            else:
                display_string = f"{customer.name}"
            
            # Add email if available
            if customer.email:
                display_string += f" ✉ {customer.email}"
            
            # Store ID for reference
            display_string_with_id = f"{display_string} (ID: {customer.id})"
            
            customer_list.append(display_string_with_id)
            self.customer_map[display_string_with_id] = customer
        
        # Set values for professional search combobox
        if hasattr(self, 'customer_search'):
            self.customer_search.values = customer_list
            self.customer_search.combo['values'] = customer_list
        
        # Also set plain display values (without ID) for dropdown
        plain_display = ["Walk-in Customer"]
        for customer in customers:
            if customer.phone:
                plain_display.append(f"{customer.name} 📞 {customer.phone}")
            else:
                plain_display.append(customer.name)
        
        # Store for quick reference
        self.customer_plain_list = plain_display
    
    def on_customer_select(self, event):
        """Handle customer selection from dropdown"""
        selected = self.customer_search.get()
        
        if selected == "Walk-in Customer":
               # No customer info to show
            return
        
        # Find customer in map
        customer = None
        if selected in self.customer_map:
            customer = self.customer_map[selected]
        else:
            # Try to find by display string (without ID)
            for display_str, cust in self.customer_map.items():
                if cust and selected in display_str:
                    customer = cust
                    # Update combobox to show full string with ID
                    self.customer_search.set(display_str)
                    break
    
    # def show_customer_info(self, customer):
    #     """Show customer information panel"""
    #     # Update labels
    #     self.customer_name_value.config(text=customer.name)
    #     self.customer_phone_value.config(text=customer.phone or "Not provided")
    #     self.customer_email_value.config(text=customer.email or "Not provided")
        
    #     # Show the frame
    #     self.customer_info_frame.pack(fill=tk.X, pady=(0, 10))
    
    # def hide_customer_info(self):
    #     """Hide customer information panel"""
    #     self.customer_info_frame.pack_forget()
    
    def add_new_customer_dialog(self):
        """Open dialog to add new customer"""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Customer")
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
        
        # Form frame
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Name *", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        
        # Phone
        ttk.Label(form_frame, text="Phone", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(10, 5))
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(form_frame, textvariable=phone_var, width=30)
        phone_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Email
        ttk.Label(form_frame, text="Email", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5))
        email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=email_var, width=30)
        email_entry.grid(row=2, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Address
        ttk.Label(form_frame, text="Address", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        address_text = tk.Text(form_frame, height=4, width=30)
        address_text.grid(row=3, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Button frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save_customer():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Validation", "Customer name is required!")
                return
            
            # Create customer
            customer = Customer(
                name=name,
                phone=phone_var.get().strip(),
                email=email_var.get().strip(),
                address=address_text.get(1.0, tk.END).strip()
            )
            
            try:
                customer.save()
                
                # Refresh customer list
                self.load_customers()
                
                # Select the new customer
                display_string = f"{customer.name}"
                if customer.phone:
                    display_string += f" 📞 {customer.phone}"
                if customer.email:
                    display_string += f" ✉ {customer.email}"
                display_string += f" (ID: {customer.id})"
                
                self.customer_search.set(display_string)
                # self.show_customer_info(customer)
                
                messagebox.showinfo("Success", "Customer added successfully!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save customer: {str(e)}")
        
        ttk.Button(btn_frame, text="💾 Save Customer", 
                  command=save_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus name entry
        name_entry.focus_set()
    
    def view_selected_customer(self):
        """View details of currently selected customer"""
        selected = self.customer_search.get()
        
        if not selected or selected == "Walk-in Customer":
            messagebox.showinfo("Info", "No customer selected or Walk-in customer selected")
            return
        
        # Find customer
        customer = None
        if selected in self.customer_map:
            customer = self.customer_map[selected]
        else:
            for display_str, cust in self.customer_map.items():
                if cust and selected in display_str:
                    customer = cust
                    break
        
        if customer:
            # Show customer details in messagebox
            details = f"Customer Details\n"
            details += "=" * 30 + "\n"
            details += f"ID: {customer.id}\n"
            details += f"Name: {customer.name}\n"
            details += f"Phone: {customer.phone or 'Not provided'}\n"
            details += f"Email: {customer.email or 'Not provided'}\n"
            details += f"Address: {customer.address or 'Not provided'}\n"
            
            # Get invoice statistics
            row = db.fetch_one('''
                SELECT COUNT(*) as count, SUM(total) as total
                FROM invoices 
                WHERE customer_id = ?
            ''', (customer.id,))
            
            if row:
                details += f"\nInvoice Statistics:\n"
                details += f"  Total Invoices: {row['count'] or 0}\n"
                details += f"  Total Amount: ₹{row['total'] or 0:.2f}\n"
            
            messagebox.showinfo("Customer Details", details)
        else:
            messagebox.showwarning("Not Found", "Customer not found!")
    
    def load_invoices(self):
        """Load invoices into the treeview"""
        # Clear existing items
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Build WHERE clause based on filters
        where_clauses = []
        params = []

         # Payment method filter
        payment_method = self.payment_method_var.get()
        if payment_method != "All":
            where_clauses.append("EXISTS (SELECT 1 FROM payments p WHERE p.invoice_id = i.id AND p.method = ?)")
            params.append(payment_method)
        
        # Status filter
        status = self.status_var.get()
        if status != "All":
            where_clauses.append("i.status = ?")
            params.append(status)
        
        # Date filter
        month_filter = self.month_var.get()
        today = date.today()
        
        if month_filter == "This Month":
            first_day = today.replace(day=1)
            where_clauses.append("i.date >= ?")
            params.append(first_day)
        elif month_filter == "Last Month":
            first_day_last = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last = today.replace(day=1) - timedelta(days=1)
            where_clauses.append("i.date >= ? AND i.date <= ?")
            params.extend([first_day_last, last_day_last])
        elif month_filter == "Last 3 Months":
            three_months_ago = today - timedelta(days=90)
            where_clauses.append("i.date >= ?")
            params.append(three_months_ago)
        
        # Build query
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f'''
            SELECT i.id, i.invoice_number, i.date, c.name as customer, 
                   i.total, i.status
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE {where_clause}
            ORDER BY i.date DESC, i.id DESC
        '''
        
        rows = db.fetch_all(query, params)
        
        # Add to treeview
        for row in rows:
            self.invoice_tree.insert('', tk.END, values=(
                row['invoice_number'],
                row['date'],
                row['customer'] or "Walk-in",
                f"₹{row['total']:.2f}",
                row['status']
            ))
    
    def on_invoice_select(self, event):
        """Handle invoice selection from treeview"""
        selection = self.invoice_tree.selection()
        if not selection:
            return
        
        # Get selected invoice ID
        item = self.invoice_tree.item(selection[0])
        invoice_number = item['values'][0]
        
        # Load invoice data
        self.load_invoice_data(invoice_number)
    
    def load_invoice_data(self, invoice_number):
        """Load invoice data into form"""
        # Get invoice from database
        row = db.fetch_one('''
            SELECT i.*, c.name as customer_name, c.id as customer_id,
                   c.phone as customer_phone, c.email as customer_email
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.invoice_number = ?
        ''', (invoice_number,))
        
        if not row:
            return
        
        # Load invoice items
        items_rows = db.fetch_all('''
            SELECT ii.*, p.name as product_name
            FROM invoice_items ii
            LEFT JOIN products p ON ii.product_id = p.id
            WHERE ii.invoice_id = ?
        ''', (row['id'],))
        
        # Create invoice object
        self.current_invoice = Invoice(
            id=row['id'],
            invoice_number=row['invoice_number'],
            customer_id=row['customer_id'],
            date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
            due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date() if row['due_date'] else None,
            subtotal=row['subtotal'],
            tax_rate=row['tax_rate'],
            tax_amount=row['tax_amount'],
            total=row['total'],
            status=row['status'] or ""
            # notes=row['notes'] 
        )
        
        # Load items
        self.invoice_items = []
        for item_row in items_rows:
            item = InvoiceItem(
                product_id=item_row['product_id'],
                description=item_row['description'] or "",
                quantity=item_row['quantity'],
                unit_price=item_row['unit_price'],
                total=item_row['total']
            )
            self.invoice_items.append(item)
        
        self.current_invoice.items = self.invoice_items
        
        # Update form fields
        self.invoice_num_var.set(self.current_invoice.invoice_number)
        self.date_var.set(self.current_invoice.date.strftime("%Y-%m-%d"))
        self.due_date_var.set(self.current_invoice.due_date.strftime("%Y-%m-%d") if self.current_invoice.due_date else "")
        
        # Set customer
        if row['customer_name']:
            # Build display string
            display_string = f"{row['customer_name']}"
            if row['customer_phone']:
                display_string += f" 📞 {row['customer_phone']}"
            if row['customer_email']:
                display_string += f" ✉ {row['customer_email']}"
            display_string += f" (ID: {row['customer_id']})"
            
            self.customer_search.set(display_string)
        else:
            self.customer_search.set("Walk-in Customer")
        # Set tax rate
        self.tax_rate_var.set(self.current_invoice.tax_rate)
         # Set discount values if they exist in the invoice
        if hasattr(self.current_invoice, 'discount_amount') and self.current_invoice.discount_amount > 0:
            self.discount_value.set(self.current_invoice.discount_amount)
            self.discount_type.set("amount")
        elif hasattr(self.current_invoice, 'discount_percentage') and self.current_invoice.discount_percentage > 0:
            self.discount_value.set(self.current_invoice.discount_percentage)
            self.discount_type.set("percentage")
        else:
            self.discount_value.set(0.0)
        
        # # Set notes
        # self.notes_text.delete(1.0, tk.END)
        # self.notes_text.insert(1.0, self.current_invoice.notes)
        
        # Update items tree
        self.update_items_tree()
        
        # Calculate totals
        self.calculate_totals()
        
        # Enable buttons based on status
        self.save_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)
        self.print_btn.config(state=tk.NORMAL)
        
        if self.current_invoice.status == 'pending':
            self.mark_paid_btn.config(state=tk.NORMAL)
        else:
            self.mark_paid_btn.config(state=tk.DISABLED)
    
    def update_items_tree(self):
        """Update items treeview with current items"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add items to treeview
        for idx, item in enumerate(self.invoice_items):
            # Get product name
            product_name = "Unknown Product"
            if item.product_id:
                product = Product.get_by_id(item.product_id)
                if product:
                    product_name = product.name
            
            self.items_tree.insert('', tk.END, values=(
                product_name,
                item.description,
                f"{item.quantity}",
                f"₹{item.unit_price:.2f}",
                f"₹{item.total:.2f}"
            ), tags=(str(idx),))
    def on_item_cell_double_click(self, event):
        region = self.items_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.items_tree.identify_column(event.x)
        row_id = self.items_tree.identify_row(event.y)

        # Qty column is column #3 (Product=1, Desc=2, Qty=3)
        if column != "#3" or not row_id:
            return

        # Get item index from tags
        item = self.items_tree.item(row_id)
        tags = item.get("tags", [])
        if not tags:
            return

        idx = int(tags[0])
        invoice_item = self.invoice_items[idx]

        # Cell bounding box
        x, y, width, height = self.items_tree.bbox(row_id, column)

        # Create entry widget
        entry = ttk.Entry(self.items_tree, width=6)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, str(invoice_item.quantity))
        entry.focus()

        def save_qty(event=None):
            try:
                new_qty = float(entry.get())
                if new_qty <= 0:
                    raise ValueError

                invoice_item.quantity = new_qty
                invoice_item.calculate_total()

                self.update_items_tree()
                self.calculate_totals()
            except ValueError:
                messagebox.showwarning("Invalid Quantity", "Please enter a valid quantity.")
            finally:
                entry.destroy()

        def cancel_edit(event=None):
            entry.destroy()

        entry.bind("<Return>", save_qty)
        entry.bind("<FocusOut>", save_qty)
        entry.bind("<Escape>", cancel_edit)

    def calculate_totals(self):
        """Calculate invoice totals with discount"""
        subtotal = sum(item.total for item in self.invoice_items)
        # Get tax rate safely
        tax_rate = 0.0
        try:
            if hasattr(self, 'tax_rate_var') and self.tax_rate_var:
                tax_rate_str = self.tax_rate_var.get()
                if tax_rate_str:
                    tax_rate = float(tax_rate_str)
        except (AttributeError, tk.TclError, ValueError):
            tax_rate = 0.0
    
        # Calculate discount
        discount_value= 0.0
        discount_type = "percentage"
        discount_amount = 0.0
        
        try:
            if hasattr(self, 'discount_value') and self.discount_value:
                discount_value = self.discount_value.get()
            if hasattr(self, 'discount_type') and self.discount_type:
                discount_type = self.discount_type.get()
        except (AttributeError, tk.TclError):
            # Handle case where variables aren't initialized yet
            discount_value = 0.0
            discount_type = "percentage"
    
        if discount_type == "percentage":
            discount_amount = subtotal * (discount_value / 100)
        else:
            discount_amount = min(discount_value, subtotal)  # Can't discount more than subtotal
    
        # Calculate taxable amount (after discount)
        taxable_amount = subtotal - discount_amount
    
        # Calculate tax and total
        tax_amount = taxable_amount * (tax_rate / 100)
        total = taxable_amount + tax_amount
    
        # Update display
        self.subtotal_var.set(f"₹{subtotal:.2f}")
        # Only update discount_amount_var if it exists
        if hasattr(self, 'discount_amount_var'):
            self.discount_amount_var.set(f"₹{discount_amount:.2f}")
        self.tax_amount_var.set(f"₹{tax_amount:.2f}")
        self.total_var.set(f"₹{total:.2f}")
    
    def new_invoice(self):
        """Create new invoice form"""
        self.current_invoice = None
        self.invoice_items = []
        self.clear_form()
        
        # Generate new invoice number
        row = db.fetch_one('SELECT value FROM settings WHERE key="next_invoice_number"')
        if row:
            self.invoice_num_var.set(row['value'])
        
        # Set today's date
        today = date.today()
        self.date_var.set(today.strftime("%Y-%m-%d"))
        self.due_date_var.set((today + timedelta(days=30)).strftime("%Y-%m-%d"))
        
        # Set default customer to Walk-in
        self.customer_search.set("Walk-in Customer")
        
        # Enable save button
        self.save_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.DISABLED)
        self.print_btn.config(state=tk.DISABLED)
        self.mark_paid_btn.config(state=tk.DISABLED)
        
        # Clear items tree
        self.update_items_tree()
        self.calculate_totals()
        
        # Focus on customer search
        self.customer_search.combo.focus()
    
    def clear_form(self):
        """Clear the form"""
        self.current_invoice = None
        self.invoice_items = []
        self.invoice_num_var.set("")
        self.date_var.set("")
        self.due_date_var.set("")
        self.customer_search.set("")
        self.tax_rate_var.set(18.0)
        # self.notes_text.delete(1.0, tk.END)
        self.subtotal_var.set("₹0.00")
        self.tax_amount_var.set("₹0.00")
        self.total_var.set("₹0.00")
        self.save_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        self.print_btn.config(state=tk.DISABLED)
        self.mark_paid_btn.config(state=tk.DISABLED)
        self.invoice_tree.selection_remove(self.invoice_tree.selection())
        self.update_items_tree()
        
        # Reload customers
        self.load_customers()
    
    def add_item_dialog(self):
        """Open dialog to add item to invoice"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Item")
        dialog.geometry("500x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Product selection
        ttk.Label(dialog, text="Product/Service:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=20, pady=(20, 5))
        
        product_frame = ttk.Frame(dialog)
        product_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.dialog_product_var = tk.StringVar()
        product_combo = ttk.Combobox(product_frame, textvariable=self.dialog_product_var, 
                                    state="normal", width=40)
        product_combo.pack(side=tk.LEFT)
        
        # Load products
        products = Product.get_all()
        product_list = []
        self.dialog_products_map = {}
        
        for product in products:
            item_text = f"{product.name} - ₹{product.price:.2f}"
            if not product.is_service:
                item_text += f" (Stock: {product.stock})"
            product_list.append(item_text)
            self.dialog_products_map[item_text] = product
            self._all_product_values = product_list[:]   # store master list
        
        product_combo['values'] = product_list
        if product_list:
            product_combo.current(0)
        
        # Description
        ttk.Label(dialog, text="Description:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=20, pady=(10, 5))
        self.dialog_desc_var = tk.StringVar()
        desc_entry = ttk.Entry(dialog, textvariable=self.dialog_desc_var, width=50)
        desc_entry.pack(padx=20, pady=(0, 10))
        
        # Quantity and price
        qty_price_frame = ttk.Frame(dialog)
        qty_price_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        ttk.Label(qty_price_frame, text="Quantity:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.dialog_qty_var = tk.DoubleVar(value=1.0)
        qty_spin = ttk.Spinbox(qty_price_frame, from_=0.01, to=1000, 
                              textvariable=self.dialog_qty_var, width=10)
        qty_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(qty_price_frame, text="Price (₹):", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(20, 0))
        self.dialog_price_var = tk.DoubleVar(value=0.0)
        price_spin = ttk.Spinbox(qty_price_frame, from_=0, to=1000000, 
                                textvariable=self.dialog_price_var, width=12)
        price_spin.pack(side=tk.LEFT, padx=5)
        
        # Update price when product changes
        def update_price(*args):
            selected = self.dialog_product_var.get()
            if selected in self.dialog_products_map:
                product = self.dialog_products_map[selected]
                self.dialog_price_var.set(product.price)
                # Auto-fill description if empty
                self.dialog_desc_var.set(product.description or product.name)
        
        self.dialog_product_var.trace('w', update_price)
        update_price()  # Initial update
        
        # Total
        total_frame = ttk.Frame(dialog)
        total_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        ttk.Label(total_frame, text="Total:", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        self.dialog_total_var = tk.StringVar(value="₹0.00")
        ttk.Label(total_frame, textvariable=self.dialog_total_var, 
                 font=('Arial', 12, 'bold'), foreground='green').pack(side=tk.LEFT, padx=5)
        
        # Calculate total when qty or price changes
        def calculate_dialog_total(*args):
            try:
                qty = self.dialog_qty_var.get()
                price = self.dialog_price_var.get()
                total = qty * price
                self.dialog_total_var.set(f"₹{total:.2f}")
            except:
                self.dialog_total_var.set("₹0.00")
        
        self.dialog_qty_var.trace('w', calculate_dialog_total)
        self.dialog_price_var.trace('w', calculate_dialog_total)
        calculate_dialog_total()
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Add to Invoice", 
                  command=lambda: self.add_item_from_dialog(dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_item_from_dialog(self, dialog):
        """Add item from dialog to invoice"""
        # Get selected product
        selected = self.dialog_product_var.get()
        if not selected:
            messagebox.showwarning("Error", "Please select a product!")
            return
        
        product = self.dialog_products_map.get(selected)
        if not product:
            messagebox.showwarning("Error", "Invalid product selection!")
            return
        
        # Validate quantity
        try:
            quantity = self.dialog_qty_var.get()
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            # Check stock for products
            if not product.is_service and product.stock < quantity:
                if not messagebox.askyesno("Low Stock", 
                                          f"Only {product.stock} units available.\n"
                                          "Add anyway?"):
                    return
        except ValueError as e:
            messagebox.showwarning("Error", str(e))
            return
        
        # Get description
        description = self.dialog_desc_var.get().strip()
        if not description:
            description = product.name
        
        # Get price
        price = self.dialog_price_var.get()
        
        # Create invoice item
        item = InvoiceItem(
            product_id=product.id,
            description=description,
            quantity=quantity,
            unit_price=price
        )
        item.calculate_total()
        
        # Add to invoice items
        self.invoice_items.append(item)
        
        # Update UI
        self.update_items_tree()
        self.calculate_totals()
        
        # Close dialog
        dialog.destroy()
        
        # Enable save button if not already enabled
        self.save_btn.config(state=tk.NORMAL)
    
    def remove_selected_item(self):
        """Remove selected item from invoice"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Error", "Please select an item to remove!")
            return
        
        # Get selected item index
        item = self.items_tree.item(selection[0])
        tags = item['tags']
        if tags:
            idx = int(tags[0])
            
            # Remove from list
            if 0 <= idx < len(self.invoice_items):
                self.invoice_items.pop(idx)
                
                # Update UI
                self.update_items_tree()
                self.calculate_totals()
    
    def save_invoice(self):
        """Save invoice data"""
        # Validate required fields
        if not self.invoice_num_var.get():
            messagebox.showwarning("Validation Error", "Invoice number is required!")
            return
        
        if not self.invoice_items:
            messagebox.showwarning("Validation Error", "Please add at least one item!")
            return
        
        # Parse customer ID from selection
        customer_id = None
        customer_text = self.customer_search.get()
        
        if customer_text and customer_text != "Walk-in Customer":
            # Try to find customer in map
            customer = None
            if customer_text in self.customer_map:
                customer = self.customer_map[customer_text]
            else:
                # Try to extract ID from string
                match = re.search(r'\(ID:\s*(\d+)\)', customer_text)
                if match:
                    customer_id = int(match.group(1))
                    customer = Customer.get_by_id(customer_id)
                else:
                    # Search for customer by name
                    for display_str, cust in self.customer_map.items():
                        if cust and customer_text in display_str:
                            customer = cust
                            break
            
            if customer:
                customer_id = customer.id
            else:
                messagebox.showwarning("Customer Error", 
                                     "Customer not found. Please select a valid customer or use 'Walk-in Customer'.")
                return
        
        # Parse dates
        try:
            invoice_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
            due_date = datetime.strptime(self.due_date_var.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter valid dates (YYYY-MM-DD)!")
            return
        
        # Create or update invoice
        invoice = self.current_invoice or Invoice()
        invoice.invoice_number = self.invoice_num_var.get()
        invoice.customer_id = customer_id
        invoice.date = invoice_date
        invoice.due_date = due_date
        invoice.tax_rate = self.tax_rate_var.get()
        # invoice.notes = self.notes_text.get(1.0, tk.END).strip()
        invoice.items = self.invoice_items

        # Calculate and store discount
        subtotal = sum(item.total for item in self.invoice_items)
        discount_value =  0.0
        discount_type = "percentage"

        try:
            if hasattr(self, 'discount_value') and self.discount_value:
                discount_value = self.discount_value.get()
            if hasattr(self, 'discount_type') and self.discount_type:    
                discount_type = self.discount_type.get()
        except (AttributeError, tk.TclError):
            discount_value = 0.0
            discount_type = "percentage"
        # Create or update invoice with discount
        if self.current_invoice:
            invoice = self.current_invoice
        else:
            invoice = Invoice()    
        invoice.invoice_number = self.invoice_num_var.get()
        invoice.customer_id = customer_id
        invoice.date = invoice_date
        invoice.due_date = due_date
        invoice.tax_rate = self.tax_rate_var.get()
        # invoice.notes = self.notes_text.get(1.0, tk.END).strip()
        invoice.items = self.invoice_items 
         # Set discount values
        if discount_type == "percentage":
            invoice.discount_percentage = discount_value
            invoice.discount_amount = subtotal * (discount_value / 100)
        else:
            invoice.discount_amount = min(discount_value, subtotal)
            invoice.discount_percentage = (invoice.discount_amount / subtotal * 100) if subtotal > 0 else 0
        # Calculate discounted subtotal
        invoice.discounted_subtotal = subtotal - invoice.discount_amount
        
        try:
            # Start transaction
            if db.connection:
                db.connection.isolation_level = None  # Enable autocommit mode
                db.connection.execute("BEGIN TRANSACTION")
            invoice.save()
            
            # Update stock for products
            for item in self.invoice_items:
                if item.product_id:
                    # Get current stock
                    row = db.fetch_one('SELECT stock, is_service FROM products WHERE id=?', 
                                      (item.product_id,))
                    if row and not row['is_service']:
                        # Reduce stock
                        new_stock = row['stock'] - item.quantity
                        db.execute('UPDATE products SET stock=? WHERE id=?', 
                                  (new_stock, item.product_id))
            
            # Commit transaction
            if db.connection:
                db.connection.commit()
            
            # Show success message
            action = "updated" if self.current_invoice else "created"
            messagebox.showinfo("Success", f"Invoice {action} successfully!")
            
            # Refresh list and clear form
            self.load_invoices()
            self.clear_form()
            
        except Exception as e:
            db.connection.rollback()
            messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")
    
    def delete_invoice(self):
        """Delete selected invoice"""
        if not self.current_invoice:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Delete invoice #{self.current_invoice.invoice_number}?\n\n"
                                  "This action cannot be undone."):
            return
        
        try:
            # Restore stock first
            for item in self.current_invoice.items:
                if item.product_id:
                    # Get current stock
                    row = db.fetch_one('SELECT stock, is_service FROM products WHERE id=?', 
                                      (item.product_id,))
                    if row and not row['is_service']:
                        # Restore stock
                        new_stock = row['stock'] + item.quantity
                        db.execute('UPDATE products SET stock=? WHERE id=?', 
                                  (new_stock, item.product_id))
            
            # Delete invoice items
            db.execute('DELETE FROM invoice_items WHERE invoice_id=?', 
                      (self.current_invoice.id,))
            
            # Delete invoice
            db.execute('DELETE FROM invoices WHERE id=?', 
                      (self.current_invoice.id,))
            
             # Commit transaction
            if db.connection:
                db.connection.commit()
            
            # Show success message
            messagebox.showinfo("Success", "Invoice deleted successfully!")
            
            # Refresh list and clear form
            self.load_invoices()
            self.clear_form()
            
        except Exception as e:
            if db.connection:
                db.connection.rollback()
            messagebox.showerror("Error", f"Failed to delete invoice: {str(e)}")
    
    def print_invoice(self):
        """Print or generate PDF for invoice"""
        if not self.current_invoice:
            return
        
        # Simple text display
        invoice_text = f"Invoice #{self.current_invoice.invoice_number}\n"
        invoice_text += f"Date: {self.current_invoice.date}\n"
        invoice_text += f"Status: {self.current_invoice.status}\n"
        invoice_text += f"Total: ₹{self.current_invoice.total:.2f}\n"
        
        # Show in messagebox
        from tkinter import scrolledtext
        
        text_window = tk.Toplevel(self)
        text_window.title(f"Invoice #{self.current_invoice.invoice_number}")
        text_window.geometry("400x300")
        
        text_area = scrolledtext.ScrolledText(text_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Build detailed text
        detailed_text = invoice_text + "\n" + "="*40 + "\n"
        for idx, item in enumerate(self.current_invoice.items, 1):
            detailed_text += f"{idx}. {item.description}: {item.quantity} x ₹{item.unit_price:.2f} = ₹{item.total:.2f}\n"
        
        detailed_text += "="*40 + "\n"
        detailed_text += f"Subtotal: ₹{self.current_invoice.subtotal:.2f}\n"
        detailed_text += f"Tax: ₹{self.current_invoice.tax_amount:.2f}\n"
        detailed_text += f"Total: ₹{self.current_invoice.total:.2f}\n"
        
        text_area.insert(1.0, detailed_text)
        text_area.config(state=tk.DISABLED)
    
    def mark_as_paid(self):
        """Mark invoice as paid"""
        if not self.current_invoice or self.current_invoice.status != 'pending':
            return
        # Create payment method dialog
        dialog = tk.Toplevel(self)
        dialog.title("Record Payment")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        # Payment details
        ttk.Label(frame, text="Record Payment", font=('Arial', 14, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 10))
    
        ttk.Label(frame, text="Invoice Total:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=f"₹{self.current_invoice.total:.2f}", 
             font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky=tk.W, pady=5)
    
        ttk.Label(frame, text="Payment Method:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)
    
        payment_methods = ["Cash", "Card", "Credit", "UPI"]
        payment_method_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(frame, textvariable=payment_method_var, 
                                values=payment_methods, state="readonly", width=15)
        payment_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
    
        ttk.Label(frame, text="Payment Date:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        payment_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        payment_date_entry = ttk.Entry(frame, textvariable=payment_date_var, width=15)
        payment_date_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        def record_payment():
            method = payment_method_var.get()
            payment_date = payment_date_var.get()
        
            try:
                # Update status
                db.execute('UPDATE invoices SET status="paid" WHERE id=?', 
                            (self.current_invoice.id,))
            
                # Record payment
                db.execute('''
                    INSERT INTO payments (invoice_id, amount, payment_date, method)
                    VALUES (?, ?, ?, ?)
                    ''', (self.current_invoice.id, self.current_invoice.total, 
                            payment_date, method))
            
                # Commit transaction
                if db.connection:
                    db.connection.commit()
            
                # Update current invoice
                self.current_invoice.status = 'paid'
            
                # Disable mark paid button
                self.mark_paid_btn.config(state=tk.DISABLED)
            
                # Refresh list
                self.load_invoices()
            
                messagebox.showinfo("Success", f"Invoice marked as paid via {method}!")
                dialog.destroy()
            except Exception as e:
                if db.connection:
                    db.connection.rollback()
                messagebox.showerror("Error", f"Failed to update invoice: {str(e)}")
                    
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
    
        ttk.Button(btn_frame, text="Record Payment", 
                  command=record_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_quick_stats(self):
        """Show quick invoice statistics"""
        today = date.today()
        first_day = today.replace(day=1)
        
        # Get monthly stats
        row = db.fetch_one('''
            SELECT 
                COUNT(*) as count,
                SUM(total) as total,
                SUM(CASE WHEN status = 'pending' THEN total ELSE 0 END) as pending_total
            FROM invoices 
            WHERE date >= ?
        ''', (first_day,))
        
        # Get today's stats
        row_today = db.fetch_one('''
            SELECT 
                COUNT(*) as count,
                SUM(total) as total
            FROM invoices 
            WHERE date = ?
        ''', (today,))
        
        stats_text = "📊 Invoice Statistics\n"
        stats_text += "=" * 30 + "\n"
        stats_text += f"This Month:\n"
        stats_text += f"  Invoices: {row['count'] or 0}\n"
        stats_text += f"  Total: ₹{row['total'] or 0:.2f}\n"
        stats_text += f"  Pending: ₹{row['pending_total'] or 0:.2f}\n\n"
        stats_text += f"Today:\n"
        stats_text += f"  Invoices: {row_today['count'] or 0}\n"
        stats_text += f"  Total: ₹{row_today['total'] or 0:.2f}"
        
        messagebox.showinfo("Invoice Statistics", stats_text)

# Main function to test the invoice page
def main():
    """Test function to display the invoice page"""
    root = tk.Tk()
    root.title("Invoice Management")
    root.geometry("1200x700")
    
    # Create and display invoices page
    invoices_page = Invoices(root)
    invoices_page.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()