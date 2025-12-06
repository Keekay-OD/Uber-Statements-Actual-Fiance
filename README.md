# PDF Statement to CSV Converter

A Python script that extracts transaction data from bank statement PDFs and converts them to CSV format for easy import into accounting software or spreadsheet applications.

## Features

- Extracts transactions from PDF bank statements
- Converts to clean CSV format with columns: `date`, `payee`, `amount`
- Handles both Credits (positive amounts) and Debits (negative amounts)
- Supports multiple PDF files in batch processing
- Two parsing methods: Table extraction (primary) and Text extraction (fallback)

## Requirements

- Python 3.6 or higher
- Required Python packages:
  - `pdfplumber`
  - `csv` (standard library)
  - `datetime` (standard library)
  - `os`, `re`, `sys` (standard libraries)

## Installation

1. **Clone or download this repository:**
   ```bash
   git clone Uber-Statements-Actual-Fiance
   cd UberPDFCSVCON
   ```

2. **Install required package:**
   ```bash
   pip install pdfplumber
   ```

3. **Set up the folder structure:**
   Create the following folders in the same directory as the script:
   ```bash
   mkdir pdf_statements
   mkdir csv_output
   ```

   Your directory structure should look like:
   ```
   UberPDFCSVCON/
   ├── pdf_to_csv.py      # The main script
   ├── pdf_statements/    # Folder for your PDF files
   ├── csv_output/        # Folder for generated CSV files
   └── README.md          # This file
   ```

## Usage

1. **Place your PDF bank statements in the `pdf_statements` folder.**

2. **Run the script:**
   ```bash
   python3 pdf_to_csv.py
   ```

3. **Check the results:**
   - The script will process all PDF files in the `pdf_statements` folder
   - Generated CSV files will be saved in the `csv_output` folder
   - Each CSV file will have the same name as the original PDF file (with `.csv` extension)

4. **CSV Format:**
   The output CSV files will have the following columns:
   - `date`: Transaction date in YYYY-MM-DD format
   - `payee`: Merchant or transaction description
   - `amount`: Transaction amount (positive for credits/deposits, negative for debits/withdrawals)

## Example

Input (from PDF statement):
```
Date       Description              Credits  Debits  Balance
11/02/2025 COSTCO WHOLESALE W54     18.54    56.38
11/02/2025 UBER PAYOUT       4.54           50.76
```

Output (in CSV):
```csv
date,payee,amount
2025-11-02,COSTCO WHOLESALE W54,-18.54
2025-11-02,UBER PAYOUT,4.54
```

## File Structure

```
UberPDFCSVCON/
├── pdf_to_csv.py          # Main conversion script
├── pdf_statements/        # Input folder for PDF files
│   ├── statement1.pdf
│   ├── statement2.pdf
│   └── ...
├── csv_output/            # Output folder for CSV files
│   ├── statement1.csv
│   ├── statement2.csv
│   └── ...
├── .gitignore            # Git ignore file
└── README.md             # This documentation
```

## .gitignore

Create a `.gitignore` file with the following content to exclude input/output folders from version control:

```
# Ignore input/output folders
pdf_statements/
csv_output/

# Python cache and virtual environment
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs and temporary files
*.log
*.tmp
*.temp
```

## Troubleshooting

### Common Issues:

1. **"No PDF files found" error:**
   - Make sure PDF files are placed in the `pdf_statements` folder
   - Verify the folder name is exactly `pdf_statements`

2. **"Missing required positional argument" error:**
   - Make sure you're running the script with `python3 pdf_to_csv.py`

3. **No transactions extracted:**
   - The script uses two parsing methods. If table extraction fails, it will try text extraction
   - Check the console output for messages about which method was used

4. **Installation issues with pdfplumber:**
   ```bash
   pip install --upgrade pip
   pip install pdfplumber
   ```

### Parsing Methods:

The script uses two methods to extract data:
1. **Table Extraction (Primary):** Extracts data from PDF tables - works best for structured statements
2. **Text Extraction (Fallback):** Parses raw text - used when table extraction fails

The script will automatically use the fallback method if the primary method doesn't find transactions.

## Supported PDF Formats

The script is designed to work with bank statement PDFs that have transaction data in tabular format. It has been tested with Uber Pro Card statements but may work with other bank statements with similar formats.

## Limitations

- Designed for PDFs with transaction tables in a consistent format
- May require adjustments for PDFs with significantly different layouts
- Some transaction types (like internal transfers) are filtered out

## Contributing

Feel free to fork this repository and submit pull requests for improvements.

## License

This project is open source and available for personal and commercial use.
