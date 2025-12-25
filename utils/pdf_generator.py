"""
pdf_generator.py - PDF generation utilities
"""
from datetime import datetime
import os
import tempfile

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class PDFGenerator:
    """Generate PDF invoices"""
    
    @staticmethod
    def generate_invoice(invoice, company_info=None):
        """Generate PDF invoice"""
        if not PDF_AVAILABLE:
            raise ImportError("fpdf2 is not installed. Install with: pip install fpdf2")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.set_font("Arial", "B", 16)
        
        # Company header
        if company_info:
            pdf.cell(0, 10, txt=company_info.get('name', 'My Business'), ln=1, align="C")
            pdf.set_font("Arial", "", 10)
            if company_info.get('address'):
                pdf.cell(0, 5, txt=company_info['address'], ln=1, align="C")
            if company_info.get('phone'):
                pdf.cell(0, 5, txt=f"Phone: {company_info['phone']}", ln=1, align="C")
            if company_info.get('email'):
                pdf.cell(0, 5, txt=f"Email: {company_info['email']}", ln=1, align="C")
        
        # Invoice header
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt=f"INVOICE #{invoice.invoice_number}", ln=1, align="C")
        
        # Invoice details
        pdf.ln(5)
        pdf.set_font("Arial", "", 10)
        
        # Two columns: Invoice info and Customer info
        col_width = 90
        pdf.cell(col_width, 6, txt=f"Date: {invoice.date}", ln=0)
        pdf.cell(col_width, 6, txt=f"Due Date: {invoice.due_date}", ln=1)
        pdf.cell(col_width, 6, txt=f"Status: {invoice.status.upper()}", ln=1)
        
        pdf.ln(5)
        
        # Customer info
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, txt="BILL TO:", ln=1)
        pdf.set_font("Arial", "", 10)
        
        from models import Customer
        customer = Customer.get_by_id(invoice.customer_id) if invoice.customer_id else None
        if customer:
            pdf.cell(0, 6, txt=customer.name, ln=1)
            if customer.address:
                pdf.cell(0, 6, txt=customer.address, ln=1)
            if customer.phone:
                pdf.cell(0, 6, txt=f"Phone: {customer.phone}", ln=1)
            if customer.email:
                pdf.cell(0, 6, txt=f"Email: {customer.email}", ln=1)
        else:
            pdf.cell(0, 6, txt="Walk-in Customer", ln=1)
        
        # Items table
        pdf.ln(10)
        pdf.set_font("Arial", "B", 10)
        
        # Table header
        col_widths = [100, 30, 30, 30]
        headers = ["Description", "Quantity", "Unit Price", "Total"]
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, txt=header, border=1, align="C")
        pdf.ln()
        
        # Table rows
        pdf.set_font("Arial", "", 10)
        for item in invoice.items:
            # Description
            pdf.cell(col_widths[0], 8, txt=item.description[:50], border=1)
            # Quantity
            pdf.cell(col_widths[1], 8, txt=str(item.quantity), border=1, align="C")
            # Unit Price
            pdf.cell(col_widths[2], 8, txt=f"₹{item.unit_price:.2f}", border=1, align="R")
            # Total
            pdf.cell(col_widths[3], 8, txt=f"₹{item.total:.2f}", border=1, align="R")
            pdf.ln()
        
        # Totals
        pdf.ln(5)
        pdf.set_font("Arial", "B", 10)
        
        # Subtotal
        pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 8, txt="Subtotal:", border=0, align="R")
        pdf.cell(col_widths[3], 8, txt=f"₹{invoice.subtotal:.2f}", border=1, align="R")
        pdf.ln()
        
        # Tax
        pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 8, txt=f"Tax ({invoice.tax_rate}%):", border=0, align="R")
        pdf.cell(col_widths[3], 8, txt=f"₹{invoice.tax_amount:.2f}", border=1, align="R")
        pdf.ln()
        
        # Total
        pdf.set_font("Arial", "B", 12)
        pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 10, txt="TOTAL:", border=0, align="R")
        pdf.cell(col_widths[3], 10, txt=f"₹{invoice.total:.2f}", border=1, align="R")
        
        # Notes
        if invoice.notes:
            pdf.ln(10)
            pdf.set_font("Arial", "I", 10)
            pdf.multi_cell(0, 5, txt=f"Notes: {invoice.notes}")
        
        # Footer
        pdf.ln(20)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 5, txt="Thank you for your business!", ln=1, align="C")
        pdf.cell(0, 5, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align="C")
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, f"invoice_{invoice.invoice_number}.pdf")
        pdf.output(filename)
        
        return filename
    
    @staticmethod
    def generate_report(title, data, report_type="summary"):
        """Generate PDF report"""
        if not PDF_AVAILABLE:
            raise ImportError("fpdf2 is not installed")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, txt=title, ln=1, align="C")
        pdf.ln(10)
        
        # Content based on report type
        pdf.set_font("Arial", "", 10)
        
        if report_type == "summary":
            for key, value in data.items():
                pdf.cell(0, 8, txt=f"{key}: {value}", ln=1)
        elif report_type == "list":
            for item in data:
                pdf.cell(0, 8, txt=str(item), ln=1)
        
        # Footer
        pdf.ln(20)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 5, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align="C")
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        pdf.output(filename)
        
        return filename