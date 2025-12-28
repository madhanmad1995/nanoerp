# Create a test script check_schema.py
import re

with open('database.py', 'r') as f:
    content = f.read()
    
# Find the invoices CREATE TABLE statement
pattern = r"CREATE TABLE IF NOT EXISTS invoices\s*\(([^;]+)\)"
match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

if match:
    print("Found invoices table creation SQL:")
    print("CREATE TABLE IF NOT EXISTS invoices (")
    print(match.group(1))
    print(")")
    
    # Check for discount columns
    sql_lower = match.group(1).lower()
    
    checks = [
        ('discount_amount', 'discount_amount' in sql_lower),
        ('discount_percentage', 'discount_percentage' in sql_lower),
        ('discounted_subtotal', 'discounted_subtotal' in sql_lower)
    ]
    
    print("\nMissing columns:")
    for col_name, present in checks:
        if not present:
            print(f"  ✗ {col_name}")
else:
    print("Could not find invoices table creation SQL in database.py")