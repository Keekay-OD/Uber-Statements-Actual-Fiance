import os
import re
from datetime import datetime
import csv
import pdfplumber
import sys


def extract_transactions_from_pdf(pdf_path):
    """Extract transactions from PDF using table extraction."""
    transactions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table data
            table = page.extract_table()
            
            if table:
                for row in table:
                    # Skip header rows or rows without proper data
                    if len(row) >= 5 and row[0] and '/' in row[0]:
                        try:
                            # Parse date
                            date_str = row[0]
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                            
                            description = row[1]
                            
                            # Handle credits and debits - check for empty strings
                            credit_str = row[2] if len(row) > 2 else ''
                            debit_str = row[3] if len(row) > 3 else ''
                            
                            # Clean up strings
                            credit_str = str(credit_str).strip() if credit_str else ''
                            debit_str = str(debit_str).strip() if debit_str else ''
                            
                            # Skip if both are empty
                            if not credit_str and not debit_str:
                                continue
                            
                            # Parse amounts
                            credit = float(credit_str) if credit_str and credit_str.replace('.', '', 1).isdigit() else 0
                            debit = float(debit_str) if debit_str and debit_str.replace('.', '', 1).isdigit() else 0
                            
                            # Determine amount: positive for credits, negative for debits
                            if credit > 0:
                                amount = credit  # Positive for deposits/credits
                            elif debit > 0:
                                amount = -debit  # Negative for withdrawals/debits
                            else:
                                amount = 0
                            
                            # Skip zero amount transactions and unwanted ones
                            if amount != 0 and not any(skip in description for skip in [
                                "OPENING BALANCE",
                                "CLOSING BALANCE",
                                "FUNDS TRANSFER TO CARD",
                                "FUNDS TRANSFER FROM CARD",
                                "BACKUP BALANCE"
                            ]):
                                # Clean up description
                                description = description.replace('\n', ' ').replace('\r', ' ').strip()
                                
                                transactions.append({
                                    'date': formatted_date,
                                    'payee': description,
                                    'amount': round(amount, 2)
                                })
                                
                        except (ValueError, IndexError) as e:
                            # Try alternative parsing for this row
                            try:
                                if row and len(row) > 1:
                                    # Try to extract data from text
                                    row_text = ' '.join([str(cell) for cell in row if cell])
                                    alt_txn = parse_transaction_from_text(row_text)
                                    if alt_txn:
                                        transactions.append(alt_txn)
                            except:
                                continue
    
    return transactions


def parse_transaction_from_text(text):
    """Parse transaction from text when table extraction fails."""
    # Look for date pattern MM/DD/YYYY
    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
    if not date_match:
        return None
    
    date_str = date_match.group(1)
    
    try:
        # Parse date
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        
        # Remove date from text
        text_without_date = text.replace(date_str, '', 1).strip()
        
        # Look for amounts (numbers with decimal points)
        amount_matches = re.findall(r'([\d,]+\.\d{2})', text_without_date)
        
        if not amount_matches:
            return None
        
        # Try to find description (everything before the first amount)
        first_amount_pos = text_without_date.find(amount_matches[0])
        description = text_without_date[:first_amount_pos].strip() if first_amount_pos > 0 else "Unknown"
        
        # Determine if this is a credit or debit
        # If description contains UBER PAYOUT, it's likely a credit (positive)
        # Otherwise, it's likely a debit (negative)
        amount_value = float(amount_matches[0].replace(',', ''))
        
        if "UBER PAYOUT" in description.upper() or "REWARDS CREDIT" in description.upper():
            amount = amount_value  # Positive
        else:
            amount = -amount_value  # Negative
        
        # Skip unwanted transactions
        if any(skip in description.upper() for skip in [
            "OPENING BALANCE",
            "CLOSING BALANCE",
            "FUNDS TRANSFER TO CARD",
            "FUNDS TRANSFER FROM CARD",
            "BACKUP BALANCE"
        ]):
            return None
        
        return {
            'date': formatted_date,
            'payee': description,
            'amount': round(amount, 2)
        }
        
    except (ValueError, IndexError):
        return None


def simple_pdf_parse(pdf_path):
    """Simpler parsing method - extract all text and look for patterns."""
    transactions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    
    # Split into lines
    lines = all_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to parse as transaction
        txn = parse_transaction_from_text(line)
        if txn:
            transactions.append(txn)
    
    return transactions


def process_pdf_file(pdf_path, output_folder):
    """Process a single PDF file and generate CSV."""
    
    print(f"Processing: {os.path.basename(pdf_path)}")
    
    try:
        # First try table extraction
        transactions = extract_transactions_from_pdf(pdf_path)
        
        if not transactions:
            print(f"  No transactions found with table extraction. Trying text extraction...")
            transactions = simple_pdf_parse(pdf_path)
            
            if not transactions:
                print(f"  Warning: No transactions found in {pdf_path}")
                return
        
        # Create output filename
        basename = os.path.basename(pdf_path)
        csv_name = os.path.splitext(basename)[0] + '.csv'
        csv_path = os.path.join(output_folder, csv_name)
        
        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'payee', 'amount'])
            
            for txn in transactions:
                writer.writerow([txn['date'], txn['payee'], txn['amount']])
        
        print(f"  Generated: {csv_name} ({len(transactions)} transactions)")
        
        # Print first few transactions for verification
        print(f"  First 5 transactions:")
        for i, txn in enumerate(transactions[:5]):
            print(f"    {txn['date']}, {txn['payee']}, {txn['amount']}")
        
    except Exception as e:
        print(f"  Error processing {pdf_path}: {str(e)}")
        import traceback
        traceback.print_exc()


def process_all_pdfs(input_folder, output_folder):
    """Process all PDF files in a folder."""
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all PDF files
    pdf_files = []
    for f in os.listdir(input_folder):
        if f.lower().endswith('.pdf'):
            pdf_files.append(f)
    
    if not pdf_files:
        print(f"No PDF files found in {input_folder}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each file
    for pdf_file in sorted(pdf_files):
        pdf_path = os.path.join(input_folder, pdf_file)
        process_pdf_file(pdf_path, output_folder)
    
    print(f"\nProcessing complete!")


def main():
    """Main function."""
    
    # Set your folder paths here
    INPUT_FOLDER = "./pdf_statements"  # Folder with your PDFs
    OUTPUT_FOLDER = "./csv_output"     # Folder for output CSVs
    
    # Check if input folder exists
    if not os.path.exists(INPUT_FOLDER):
        print(f"Error: Input folder '{INPUT_FOLDER}' does not exist.")
        print(f"Please create it and put your PDF files in it.")
        return
    
    # Process all PDFs
    process_all_pdfs(INPUT_FOLDER, OUTPUT_FOLDER)
    
    print(f"\nCheck the '{OUTPUT_FOLDER}' folder for your CSV files.")


if __name__ == "__main__":
    main()