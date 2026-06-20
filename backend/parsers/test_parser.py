import io
import pandas as pd
from datetime import datetime
from bank_statement_parser import BankStatementParser

def generate_fake_csv():
    # 6 months of data, starting from Jan 1, 2024
    start_date = datetime(2024, 1, 1)
    
    records = []
    balance = 50000.0
    
    for month in range(6):
        current_date = start_date + pd.DateOffset(months=month)
        
        # Salary credit (around 5th of month)
        salary_date = current_date.replace(day=5)
        balance += 60000.0
        records.append({
            'Date': salary_date.strftime('%d/%m/%Y'),
            'Narration': 'NEFT/SALARY/ACME CORP',
            'Debit': '',
            'Credit': '60000.00',
            'Balance': str(balance)
        })
        
        # EMI debit (around 10th)
        emi_date = current_date.replace(day=10)
        balance -= 15000.0
        records.append({
            'Date': emi_date.strftime('%d/%m/%Y'),
            'Narration': 'ACH/HOME LOAN EMI',
            'Debit': '15000.00',
            'Credit': '',
            'Balance': str(balance)
        })
        
        # Grocery
        grocery_date = current_date.replace(day=15)
        balance -= 5000.0
        records.append({
            'Date': grocery_date.strftime('%d/%m/%Y'),
            'Narration': 'UPI/GROCERY STORE',
            'Debit': '5000.00',
            'Credit': '',
            'Balance': str(balance)
        })
        
        # Cash withdrawal
        cash_date = current_date.replace(day=20)
        balance -= 10000.0
        records.append({
            'Date': cash_date.strftime('%d/%m/%Y'),
            'Narration': 'ATM CASH WDL',
            'Debit': '10000.00',
            'Credit': '',
            'Balance': str(balance)
        })
        
        # Bounce event (only in one month to show it)
        if month == 2:
            bounce_date = current_date.replace(day=25)
            balance -= 500.0
            records.append({
                'Date': bounce_date.strftime('%d/%m/%Y'),
                'Narration': 'CHQ RETURN CHARGES',
                'Debit': '500.00',
                'Credit': '',
                'Balance': str(balance)
            })

    df = pd.DataFrame(records)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

def main():
    print("Generating synthetic HDFC-style CSV statement...")
    csv_file = generate_fake_csv()
    
    print("Running BankStatementParser...")
    parser = BankStatementParser()
    result = parser.parse(csv_file, file_type='csv')
    
    print("\nParsed Features:")
    for key, value in result['features'].items():
        print(f"{key}: {value}")
        
    print(f"\nTotal transactions parsed: {len(result['transactions'])}")

if __name__ == "__main__":
    main()
