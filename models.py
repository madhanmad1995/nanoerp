"""
models.py - Data models for NanoERP
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional
from database import db

@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def save(self):
        """Save customer to database"""
        if self.id is None:
            self.id = db.execute('''
                INSERT INTO customers (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            ''', (self.name, self.phone, self.email, self.address))
        else:
            db.execute('''
                UPDATE customers 
                SET name=?, phone=?, email=?, address=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (self.name, self.phone, self.email, self.address, self.id))
        return self
    
    def delete(self):
        """Delete customer from database"""
        if self.id:
            db.execute('DELETE FROM customers WHERE id=?', (self.id,))
        return True
    
    @staticmethod
    def get_all():
        """Get all customers"""
        rows = db.fetch_all('SELECT * FROM customers ORDER BY name')
        customers = []
        for row in rows:
            customer = Customer(
                id=row['id'],
                name=row['name'],
                phone=row['phone'] or "",
                email=row['email'] or "",
                address=row['address'] or "",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            customers.append(customer)
        return customers
    
    @staticmethod
    def get_by_id(customer_id):
        """Get customer by ID"""
        row = db.fetch_one('SELECT * FROM customers WHERE id=?', (customer_id,))
        if row:
            return Customer(
                id=row['id'],
                name=row['name'],
                phone=row['phone'] or "",
                email=row['email'] or "",
                address=row['address'] or "",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
        return None
    
    @staticmethod
    def search(query):
        """Search customers by name, email, or phone"""
        rows = db.fetch_all('''
            SELECT * FROM customers             
            SELECT * FROM invoice.customer = customers 
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
            ORDER BY name
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        customers = []
        for row in rows:
            customer = Customer(
                id=row['id'],
                name=row['name'],
                phone=row['phone'] or "",
                email=row['email'] or "",
                address=row['address'] or "",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            customers.append(customer)
        return customers
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    price: float = 0.0
    stock: int = 0
    is_service: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def save(self):
        """Save product to database"""
        if self.id is None:
            self.id = db.execute('''
                INSERT INTO products (name, description, price, stock, is_service)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.name, self.description, self.price, self.stock, self.is_service))
        else:
            db.execute('''
                UPDATE products 
                SET name=?, description=?, price=?, stock=?, is_service=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (self.name, self.description, self.price, self.stock, self.is_service, self.id))
        return self
    
    def update_stock(self, quantity_change):
        """Update stock quantity"""
        if not self.is_service:
            new_stock = self.stock + quantity_change
            db.execute('UPDATE products SET stock=? WHERE id=?', (new_stock, self.id))
            self.stock = new_stock
        return self
    
    @staticmethod
    def get_all():
        """Get all products"""
        rows = db.fetch_all('SELECT * FROM products ORDER BY name')
        products = []
        for row in rows:
            product = Product(
                id=row['id'],
                name=row['name'],
                description=row['description'] or "",
                price=row['price'],
                stock=row['stock'],
                is_service=bool(row['is_service']),
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            products.append(product)
        return products
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        row = db.fetch_one('SELECT * FROM products WHERE id=?', (product_id,))
        if row:
            return Product(
                id=row['id'],
                name=row['name'],
                description=row['description'] or "",
                price=row['price'],
                stock=row['stock'],
                is_service=bool(row['is_service']),
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
        return None
    
    @staticmethod
    def get_low_stock(threshold=10):
        """Get products with low stock"""
        rows = db.fetch_all('''
            SELECT * FROM products 
            WHERE stock < ? AND stock > 0 AND is_service = 0
            ORDER BY stock
        ''', (threshold,))
        products = []
        for row in rows:
            product = Product(
                id=row['id'],
                name=row['name'],
                description=row['description'] or "",
                price=row['price'],
                stock=row['stock'],
                is_service=bool(row['is_service']),
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            products.append(product)
        return products
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'is_service': self.is_service,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class InvoiceItem:
    id: Optional[int] = None
    product_id: Optional[int] = None
    description: str = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    total: float = 0.0
    
    def calculate_total(self):
        self.total = self.quantity * self.unit_price
        return self.total

@dataclass
class Payment:
    id: Optional[int] = None
    invoice_id: Optional[int] = None
    amount: float = 0.0
    payment_date: date = date.today()
    method: str = "Cash"
    notes: str = ""
    created_at: Optional[datetime] = None
    
    def save(self):
        """Save payment to database"""
        if self.id is None:
            self.id = db.execute('''
                INSERT INTO payments (invoice_id, amount, payment_date, method, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.invoice_id, self.amount, self.payment_date, self.method, self.notes))
        else:
            db.execute('''
                UPDATE payments 
                SET invoice_id=?, amount=?, payment_date=?, method=?, notes=?
                WHERE id=?
            ''', (self.invoice_id, self.amount, self.payment_date, self.method, self.notes, self.id))
        return self
    
    @staticmethod
    def get_by_invoice(invoice_id):
        """Get payments for an invoice"""
        rows = db.fetch_all('SELECT * FROM payments WHERE invoice_id=? ORDER BY payment_date DESC', (invoice_id,))
        payments = []
        for row in rows:
            payment = Payment(
                id=row['id'],
                invoice_id=row['invoice_id'],
                amount=row['amount'],
                payment_date=datetime.strptime(row['payment_date'], '%Y-%m-%d').date(),
                method=row['method'] or "Cash",
                notes=row['notes'] or "",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            payments.append(payment)
        return payments
    
    @staticmethod
    def get_all_payment_methods():
        """Get all distinct payment methods used"""
        rows = db.fetch_all('SELECT DISTINCT method FROM payments WHERE method IS NOT NULL ORDER BY method')
        methods = [row['method'] for row in rows]
        # Add default methods if not present
        default_methods = ["Cash", "Card", "Credit", "UPI"]
        for method in default_methods:
            if method not in methods:
                methods.append(method)
        return methods

@dataclass
class Invoice:
    id: Optional[int] = None
    invoice_number: str = ""
    customer_id: Optional[int] = None
    date: date = date.today()
    due_date: Optional[date] = None
    subtotal: float = 0.0
    discount_amount: float = 0.0
    discount_percentage: float = 0.0
    discounted_subtotal: float = 0.0
    tax_rate: float = 18.0
    tax_amount: float = 0.0
    total: float = 0.0
    status: str = "pending"
    notes: str = ""
    items: List[InvoiceItem] = None
    payments: List[Payment] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.payments is None:
            self.payments = []
        if self.due_date is None:
            from datetime import timedelta
            self.due_date = self.date + timedelta(days=30)
    
    def calculate_totals(self):
        """Calculate invoice totals with discount"""
        # Calculate subtotal from items
        self.subtotal = sum(item.calculate_total() for item in self.items)
        
        # Calculate discount
        if self.discount_percentage > 0:
            self.discount_amount = self.subtotal * (self.discount_percentage / 100)
        else:
            # Ensure discount doesn't exceed subtotal
            self.discount_amount = min(self.discount_amount, self.subtotal)
            if self.subtotal > 0:
                self.discount_percentage = (self.discount_amount / self.subtotal) * 100
        
        # Calculate discounted subtotal
        self.discounted_subtotal = self.subtotal - self.discount_amount
        
        # Calculate tax and total
        self.tax_amount = self.discounted_subtotal * (self.tax_rate / 100)
        self.total = self.discounted_subtotal + self.tax_amount
        
        return self
    
    def save(self):
        """Save invoice to database"""
        self.calculate_totals()
        
        if self.id is None:
            # Generate invoice number if not provided
            if not self.invoice_number:
                self.invoice_number = self._generate_invoice_number()
            
            # Insert invoice
            self.id = db.execute('''
                INSERT INTO invoices (invoice_number, customer_id, date, due_date,
                                    subtotal, discount_amount, discount_percentage,
                                    discounted_subtotal, tax_rate, tax_amount, 
                                    total, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.invoice_number, self.customer_id, self.date, self.due_date,
                  self.subtotal, self.discount_amount, self.discount_percentage,
                  self.discounted_subtotal, self.tax_rate, self.tax_amount, 
                  self.total, self.status, self.notes))
            
            # Insert invoice items
            for item in self.items:
                db.execute('''
                    INSERT INTO invoice_items (invoice_id, product_id, description,
                                             quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.id, item.product_id, item.description, 
                      item.quantity, item.unit_price, item.total))
            
            # Update next invoice number
            try:
                next_num = int(self.invoice_number) + 1
                db.execute('UPDATE settings SET value=? WHERE key="next_invoice_number"', 
                          (str(next_num),))
            except ValueError:
                # If invoice number is not numeric, don't update
                pass
        else:
            # Update existing invoice
            db.execute('''
                UPDATE invoices 
                SET customer_id=?, date=?, due_date=?, subtotal=?,
                    discount_amount=?, discount_percentage=?, discounted_subtotal=?,
                    tax_rate=?, tax_amount=?, total=?, status=?, notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (self.customer_id, self.date, self.due_date, self.subtotal,
                  self.discount_amount, self.discount_percentage, self.discounted_subtotal,
                  self.tax_rate, self.tax_amount, self.total, self.status,
                  self.notes, self.id))
            
            # Delete existing items and insert new ones
            db.execute('DELETE FROM invoice_items WHERE invoice_id=?', (self.id,))
            
            for item in self.items:
                db.execute('''
                    INSERT INTO invoice_items (invoice_id, product_id, description,
                                             quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.id, item.product_id, item.description, 
                      item.quantity, item.unit_price, item.total))
        
        return self
    
    def _generate_invoice_number(self):
        """Generate next invoice number"""
        row = db.fetch_one('SELECT value FROM settings WHERE key="next_invoice_number"')
        return row['value'] if row else "1001"
    
    def mark_as_paid(self, payment_method="Cash", payment_date=None):
        """Mark invoice as paid with payment method"""
        self.status = "paid"
        db.execute('UPDATE invoices SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', 
                  ("paid", self.id))
        
        # Record payment
        if payment_date is None:
            payment_date = date.today()
        
        payment = Payment(
            invoice_id=self.id,
            amount=self.total,
            payment_date=payment_date,
            method=payment_method
        )
        payment.save()
        
        return self
    
    def add_payment(self, amount, method="Cash", payment_date=None, notes=""):
        """Add a payment to the invoice"""
        if payment_date is None:
            payment_date = date.today()
        
        payment = Payment(
            invoice_id=self.id,
            amount=amount,
            payment_date=payment_date,
            method=method,
            notes=notes
        )
        payment.save()
        
        # Check if invoice is fully paid
        total_paid = sum(p.amount for p in self.get_payments())
        if total_paid >= self.total:
            self.status = "paid"
            db.execute('UPDATE invoices SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', 
                      ("paid", self.id))
        else:
            self.status = "partial"
            db.execute('UPDATE invoices SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', 
                      ("partial", self.id))
        
        self.payments.append(payment)
        return payment
    
    def get_payments(self):
        """Get all payments for this invoice"""
        if not self.payments and self.id:
            self.payments = Payment.get_by_invoice(self.id)
        return self.payments
    
    def get_payment_summary(self):
        """Get payment summary for this invoice"""
        payments = self.get_payments()
        total_paid = sum(p.amount for p in payments)
        balance = self.total - total_paid
        return {
            'total': self.total,
            'paid': total_paid,
            'balance': balance,
            'is_fully_paid': balance <= 0,
            'payments': payments
        }
    
    @staticmethod
    def get_all():
        """Get all invoices"""
        rows = db.fetch_all('''
            SELECT i.*, c.name as customer_name
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.date DESC, i.id DESC
        ''')
        invoices = []
        for row in rows:
            invoice = Invoice(
                id=row['id'],
                invoice_number=row['invoice_number'],
                customer_id=row['customer_id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date() if row['due_date'] else None,
                subtotal=row['subtotal'],
                discount_amount=row['discount_amount'] or 0,
                discount_percentage=row['discount_percentage'] or 0,
                discounted_subtotal=row['discounted_subtotal'] or row['subtotal'],
                tax_rate=row['tax_rate'],
                tax_amount=row['tax_amount'],
                total=row['total'],
                status=row['status'],
                notes=row['notes'] or "",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None,
                updated_at=datetime.strptime(row['updated_at'], '%Y-%m-%d %H:%M:%S') if row['updated_at'] else None
            )
            # Load items
            items_rows = db.fetch_all('''
                SELECT * FROM invoice_items WHERE invoice_id=?
            ''', (invoice.id,))
            items = []
            for item_row in items_rows:
                item = InvoiceItem(
                    id=item_row['id'],
                    product_id=item_row['product_id'],
                    description=item_row['description'] or "",
                    quantity=item_row['quantity'],
                    unit_price=item_row['unit_price'],
                    total=item_row['total']
                )
                items.append(item)
            invoice.items = items
            invoices.append(invoice)
        return invoices
    
    @staticmethod
    def get_by_id(invoice_id):
        """Get invoice by ID"""
        row = db.fetch_one('SELECT * FROM invoices WHERE id=?', (invoice_id,))
        if row:
            invoice = Invoice(
                id=row['id'],
                invoice_number=row['invoice_number'],
                customer_id=row['customer_id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date() if row['due_date'] else None,
                subtotal=row['subtotal'],
                discount_amount=row['discount_amount'] or 0,
                discount_percentage=row['discount_percentage'] or 0,
                discounted_subtotal=row['discounted_subtotal'] or row['subtotal'],
                tax_rate=row['tax_rate'],
                tax_amount=row['tax_amount'],
                total=row['total'],
                status=row['status'],
                notes=row['notes'] or "",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None,
                updated_at=datetime.strptime(row['updated_at'], '%Y-%m-%d %H:%M:%S') if row['updated_at'] else None
            )
            # Load items
            items_rows = db.fetch_all('SELECT * FROM invoice_items WHERE invoice_id=?', (invoice.id,))
            items = []
            for item_row in items_rows:
                item = InvoiceItem(
                    id=item_row['id'],
                    product_id=item_row['product_id'],
                    description=item_row['description'] or "",
                    quantity=item_row['quantity'],
                    unit_price=item_row['unit_price'],
                    total=item_row['total']
                )
                items.append(item)
            invoice.items = items
            return invoice
        return None
    
    @staticmethod
    def get_by_status(status):
        """Get invoices by status"""
        rows = db.fetch_all('''
            SELECT i.*, c.name as customer_name
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.status = ?
            ORDER BY i.date DESC
        ''', (status,))
        invoices = []
        for row in rows:
            invoice = Invoice(
                id=row['id'],
                invoice_number=row['invoice_number'],
                customer_id=row['customer_id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date() if row['due_date'] else None,
                subtotal=row['subtotal'],
                discount_amount=row['discount_amount'] or 0,
                discount_percentage=row['discount_percentage'] or 0,
                discounted_subtotal=row['discounted_subtotal'] or row['subtotal'],
                tax_rate=row['tax_rate'],
                tax_amount=row['tax_amount'],
                total=row['total'],
                status=row['status'],
                notes=row['notes'] or "",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            invoices.append(invoice)
        return invoices
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'date': self.date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subtotal': self.subtotal,
            'discount_amount': self.discount_amount,
            'discount_percentage': self.discount_percentage,
            'discounted_subtotal': self.discounted_subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'total': self.total,
            'status': self.status,
            'notes': self.notes,
            'items': [{'description': item.description, 'quantity': item.quantity, 
                      'unit_price': item.unit_price, 'total': item.total} 
                     for item in self.items],
            'payments': [{'amount': p.amount, 'method': p.method, 
                         'payment_date': p.payment_date.isoformat()}
                        for p in self.payments] if self.payments else []
        }

@dataclass
class Expense:
    id: Optional[int] = None
    date: date = date.today()
    category: str = ""
    amount: float = 0.0
    description: str = ""
    payment_method: str = "Cash"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def save(self):
        """Save expense to database"""
        if self.id is None:
            self.id = db.execute('''
                INSERT INTO expenses (date, category, amount, description, payment_method)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.date, self.category, self.amount, self.description, self.payment_method))
        else:
            db.execute('''
                UPDATE expenses 
                SET date=?, category=?, amount=?, description=?, payment_method=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (self.date, self.category, self.amount, self.description, self.payment_method, self.id))
        return self
    
    @staticmethod
    def get_all():
        """Get all expenses"""
        rows = db.fetch_all('SELECT * FROM expenses ORDER BY date DESC')
        expenses = []
        for row in rows:
            expense = Expense(
                id=row['id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                category=row['category'],
                amount=row['amount'],
                description=row['description'] or "",
                payment_method=row['payment_method'] or "Cash",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            expenses.append(expense)
        return expenses
    
    @staticmethod
    def get_by_category(category):
        """Get expenses by category"""
        rows = db.fetch_all('SELECT * FROM expenses WHERE category=? ORDER BY date DESC', (category,))
        expenses = []
        for row in rows:
            expense = Expense(
                id=row['id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                category=row['category'],
                amount=row['amount'],
                description=row['description'] or "",
                payment_method=row['payment_method'] or "Cash",
                created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S') if row['created_at'] else None
            )
            expenses.append(expense)
        return expenses
    
    @staticmethod
    def get_payment_method_summary():
        """Get expense summary by payment method"""
        rows = db.fetch_all('''
            SELECT payment_method, COUNT(*) as count, SUM(amount) as total
            FROM expenses
            GROUP BY payment_method
            ORDER BY total DESC
        ''')
        return rows
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }