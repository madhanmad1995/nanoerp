"""
database.py - Database connection and initialization
"""
import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='data/nano_erp.db'):
        """Initialize database connection"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            print(f"✓ Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
    def execute(self, query, params=()):
        """Execute a SQL query and return the last row ID"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            # Try to reconnect and retry
            try:
                print("Attempting to reconnect...")
                self.connect()
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.connection.commit()
                return cursor.lastrowid
            except Exception as retry_error:
                print(f"✗ Retry failed: {retry_error}")
                raise
    
    def fetch_one(self, query, params=()):
        """Fetch a single row"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            print(f"Query: {query}")
            return None
    
    def fetch_all(self, query, params=()):
        """Fetch all rows"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            print(f"Query: {query}")
            return []

# Create a global database instance
db = Database()

def init_db():
    """Initialize database tables"""
    try:
        print("Initializing database tables...")

        # Check if connection is established
        if not db.connection:
            if not db.connect():
                print("✗ Failed to connect to database")
                return False
        
        # Customers table
        db.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL DEFAULT 0,
                stock INTEGER NOT NULL DEFAULT 0,
                is_service INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Invoices table
        db.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                date DATE NOT NULL,
                due_date DATE,
                subtotal REAL NOT NULL DEFAULT 0,
                discount_amount REAL NOT NULL DEFAULT 0,
                discount_percentage REAL NOT NULL DEFAULT 0,
                discounted_subtotal REAL NOT NULL DEFAULT 0,
                tax_rate REAL NOT NULL DEFAULT 0,
                tax_amount REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Invoice items table
        db.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER,
                description TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 1,
                unit_price REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Expenses table
        db.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                description TEXT,
                payment_method TEXT DEFAULT 'Cash',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Payments table
        db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                payment_date DATE NOT NULL,
                method TEXT DEFAULT 'Cash',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id)
            )
        ''')
        
        # Settings table
        db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default settings if they don't exist
        default_settings = [
            ('next_invoice_number', '1001'),
            ('business_name', 'My Business'),
            ('business_address', ''),
            ('business_phone', ''),
            ('business_email', ''),
            ('default_tax_rate', '18'),
            ('currency_symbol', '₹'),
            ('invoice_prefix', 'INV'),
            ('payment_methods', 'Cash,Card,Credit,UPI'),
             ('default_payment_method', 'Cash'),
        ]
        
        for key, value in default_settings:
            db.execute('''
                INSERT OR IGNORE INTO settings (key, value) 
                VALUES (?, ?)
            ''', (key, value))
        
        print("✓ Database initialization completed successfully!")
        
        # Verify tables were created
        tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        print(f"Created tables: {[table['name'] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_setting(key, default=None):
    """Get a setting value from database"""
    try:
        row = db.fetch_one('SELECT value FROM settings WHERE key = ?', (key,))
        return row['value'] if row else default
    except Exception as e:
        print(f"Error getting setting {key}: {e}")
        return default

def set_setting(key, value):
    """Set a setting value in database"""
    try:
        db.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        return True
    except Exception as e:
        print(f"Error setting setting {key}: {e}")
        return False

# Test the database connection when this module is run directly
if __name__ == "__main__":
    print("Testing database connection...")
    try:
        if init_db():
            # Test query
            result = db.fetch_one("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table'")
            print(f"Number of tables in database: {result['count']}")
            
            # Test settings
            business_name = get_setting('business_name', 'Default Business')
            print(f"Business name from settings: {business_name}")
            
            # Test inserting a customer
            print("\nTesting customer insertion...")
            customer_id = db.execute(
                "INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)",
                ("Test Customer", "1234567890", "test@example.com")
            )
            print(f"Inserted customer with ID: {customer_id}")
            
            # Test retrieving the customer
            customer = db.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
            if customer:
                print(f"Retrieved customer: {customer['name']}")
            
            print("\n✓ Database test completed successfully!")
        else:
            print("✗ Database test failed!")
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()