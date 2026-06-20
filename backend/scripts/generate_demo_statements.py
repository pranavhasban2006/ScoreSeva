import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

# Ensure directory exists
os.makedirs('demo_data/statements', exist_ok=True)

def generate_transactions(start_date, months, generator_func):
    records = []
    current_date = start_date
    for month in range(months):
        records.extend(generator_func(current_date, month))
        # Move to next month safely
        try:
            current_date = current_date.replace(month=current_date.month + 1)
        except ValueError:
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                # Handle end of month issues (e.g. Jan 31 -> Feb 28)
                current_date = current_date.replace(month=current_date.month + 1, day=28)
                
    df = pd.DataFrame(records)
    # Recalculate balances properly based on starting balance
    # Assuming first record has the starting balance or generator handles it
    return df

def save_csv(df, filename):
    df.to_csv(f'demo_data/statements/{filename}', index=False)
    print(f"Saved {filename}")

# Generate dates for 6 months
start_date = datetime(2023, 7, 1)

def build_ramesh(start_date, month_idx):
    records = []
    base_date = start_date + pd.DateOffset(months=month_idx)
    
    # Starting balance for month 0 logic
    bal = 4500 if month_idx == 0 else 0
    
    # Salary
    salary_date = base_date + timedelta(days=random.randint(0, 3))
    records.append({'Date': salary_date.strftime('%d/%m/%Y'), 'Description': 'NEFT/UBER/SALARY', 'Debit': '', 'Credit': '15000.00'})
    
    # Phone bill
    phone_date = base_date + timedelta(days=4)
    records.append({'Date': phone_date.strftime('%d/%m/%Y'), 'Description': 'UPI/JIO PREPAID', 'Debit': '299.00', 'Credit': ''})
    
    # UPI Transfers out
    upi_date = base_date + timedelta(days=10)
    records.append({'Date': upi_date.strftime('%d/%m/%Y'), 'Description': 'UPI/FAMILY TRANSFER', 'Debit': str(random.randint(2000, 3000)) + '.00', 'Credit': ''})
    
    # Daily debits
    for i in range(1, 28, 4):
        debit_date = base_date + timedelta(days=i)
        records.append({'Date': debit_date.strftime('%d/%m/%Y'), 'Description': 'UPI/MERCHANT', 'Debit': str(random.randint(50, 500)) + '.00', 'Credit': ''})
        
    return records

def build_priya(start_date, month_idx):
    records = []
    base_date = start_date + pd.DateOffset(months=month_idx)
    
    # Irregular credits
    credit_date = base_date + timedelta(days=random.randint(5, 25))
    records.append({'Date': credit_date.strftime('%d/%m/%Y'), 'Description': 'CASH DEPOSIT', 'Debit': '', 'Credit': str(random.randint(8000, 12000)) + '.00'})
    
    # Phone bill
    phone_date = base_date + timedelta(days=random.randint(10, 15))
    records.append({'Date': phone_date.strftime('%d/%m/%Y'), 'Description': 'UPI/AIRTEL', 'Debit': '199.00', 'Credit': ''})
    
    # Small debits
    for i in range(2, 25, 7):
        debit_date = base_date + timedelta(days=i)
        records.append({'Date': debit_date.strftime('%d/%m/%Y'), 'Description': 'UPI/GROCERY', 'Debit': str(random.randint(30, 200)) + '.00', 'Credit': ''})
        
    return records

def build_vikram(start_date, month_idx):
    records = []
    base_date = start_date + pd.DateOffset(months=month_idx)
    
    # Missing credits in month 2 and 4
    if month_idx not in [2, 4]:
        credit_date = base_date + timedelta(days=5)
        records.append({'Date': credit_date.strftime('%d/%m/%Y'), 'Description': 'SALARY/ACME', 'Debit': '', 'Credit': '12500.00'})
        
    # High cash withdrawals
    atm_date = base_date + timedelta(days=10)
    records.append({'Date': atm_date.strftime('%d/%m/%Y'), 'Description': 'ATM CASH WDL', 'Debit': '5000.00', 'Credit': ''})
    
    # Bounces (month 1 and 3)
    if month_idx in [1, 3]:
        bounce_date = base_date + timedelta(days=15)
        records.append({'Date': bounce_date.strftime('%d/%m/%Y'), 'Description': 'ACH RETURN CHARGES', 'Debit': '500.00', 'Credit': ''})
        
    # Large unexplained debit in month 3
    if month_idx == 3:
        large_debit = base_date + timedelta(days=20)
        records.append({'Date': large_debit.strftime('%d/%m/%Y'), 'Description': 'UPI/UNKNOWN', 'Debit': '8000.00', 'Credit': ''})
        
    # Other debits
    for i in range(1, 20, 5):
        debit_date = base_date + timedelta(days=i)
        records.append({'Date': debit_date.strftime('%d/%m/%Y'), 'Description': 'UPI/POS', 'Debit': str(random.randint(500, 1500)) + '.00', 'Credit': ''})
        
    return records

def build_suresh(start_date, month_idx):
    records = []
    base_date = start_date + pd.DateOffset(months=month_idx)
    
    # Business deposits
    for _ in range(3):
        credit_date = base_date + timedelta(days=random.randint(1, 28))
        records.append({'Date': credit_date.strftime('%d/%m/%Y'), 'Description': 'UPI/SALE', 'Debit': '', 'Credit': str(random.randint(5000, 12000)) + '.00'})
        
    # GST
    gst_date = base_date.replace(day=20)
    records.append({'Date': gst_date.strftime('%d/%m/%Y'), 'Description': 'GST PAYMENT TAX', 'Debit': '2400.00', 'Credit': ''})
    
    # Cash withdrawals
    atm_date = base_date + timedelta(days=15)
    records.append({'Date': atm_date.strftime('%d/%m/%Y'), 'Description': 'ATM CASH', 'Debit': '8000.00', 'Credit': ''})
    
    # NEFT out
    neft_date = base_date + timedelta(days=25)
    records.append({'Date': neft_date.strftime('%d/%m/%Y'), 'Description': 'NEFT/VENDOR PAY', 'Debit': '15000.00', 'Credit': ''})
        
    return records

def build_arjun(start_date, month_idx):
    records = []
    base_date = start_date + pd.DateOffset(months=month_idx)
    
    # Small circular credits (total ~22k)
    records.append({'Date': (base_date + timedelta(days=2)).strftime('%d/%m/%Y'), 'Description': 'UPI/FRIEND', 'Debit': '', 'Credit': '10000.00'})
    records.append({'Date': (base_date + timedelta(days=12)).strftime('%d/%m/%Y'), 'Description': 'CASH DEPOSIT', 'Debit': '', 'Credit': '8000.00'})
    records.append({'Date': (base_date + timedelta(days=22)).strftime('%d/%m/%Y'), 'Description': 'IMPS/TRANSFER', 'Debit': '', 'Credit': '4000.00'})
    
    # Bounces
    if month_idx % 2 == 0:
        bounce_date = base_date + timedelta(days=15)
        records.append({'Date': bounce_date.strftime('%d/%m/%Y'), 'Description': 'CHQ BOUNCE CHARGES', 'Debit': '500.00', 'Credit': ''})
        
    # Stress debits
    records.append({'Date': (base_date + timedelta(days=5)).strftime('%d/%m/%Y'), 'Description': 'UPI/PAYMENT', 'Debit': '9000.00', 'Credit': ''})
    records.append({'Date': (base_date + timedelta(days=15)).strftime('%d/%m/%Y'), 'Description': 'ATM CASH', 'Debit': '7000.00', 'Credit': ''})
    records.append({'Date': (base_date + timedelta(days=25)).strftime('%d/%m/%Y'), 'Description': 'UPI/OUT', 'Debit': '5500.00', 'Credit': ''})
        
    return records

def build_deepak(start_date, month_idx):
    records = []
    base_date = start_date + pd.DateOffset(months=month_idx)
    
    if month_idx < 5:
        # Dormant: 2-3 tiny transactions
        for i in range(2):
            records.append({'Date': (base_date + timedelta(days=10+i*5)).strftime('%d/%m/%Y'), 'Description': 'UPI/SNACKS', 'Debit': '50.00', 'Credit': ''})
    else:
        # Active month
        # Daily small debits
        for i in range(1, 28, 2):
            amt = str(random.randint(50, 200)) + '.00'
            records.append({'Date': (base_date + timedelta(days=i)).strftime('%d/%m/%Y'), 'Description': 'UPI/MERCHANT', 'Debit': amt, 'Credit': ''})
            
        # 60,000 credit 4 days before end (approx day 26)
        records.append({'Date': (base_date + timedelta(days=26)).strftime('%d/%m/%Y'), 'Description': 'NEFT/TRANSFER', 'Debit': '', 'Credit': '60000.00'})
        
        # 4 round-trip cycles
        for i in range(4):
            dt_debit = base_date + timedelta(days=5 + i*4)
            dt_credit = dt_debit + timedelta(days=1)
            # Make sure these are round numbers to hit the 55% round numbers requirement
            records.append({'Date': dt_debit.strftime('%d/%m/%Y'), 'Description': 'UPI/OUT', 'Debit': '8000.00', 'Credit': ''})
            records.append({'Date': dt_credit.strftime('%d/%m/%Y'), 'Description': 'UPI/IN', 'Debit': '', 'Credit': '7800.00'})
            
        # Add some more round numbers to hit >40%
        for i in range(6):
            records.append({'Date': (base_date + timedelta(days=2 + i*3)).strftime('%d/%m/%Y'), 'Description': 'UPI/EXPENSE', 'Debit': '1000.00', 'Credit': ''})
            records.append({'Date': (base_date + timedelta(days=3 + i*3)).strftime('%d/%m/%Y'), 'Description': 'UPI/INCOME', 'Debit': '', 'Credit': '2000.00'})

    return records

def process_and_save(generator, filename, starting_balance):
    records = []
    current_date = start_date
    for month in range(6):
        records.extend(generator(current_date, month))
        try:
            current_date = current_date.replace(month=current_date.month + 1)
        except ValueError:
            current_date = current_date + pd.DateOffset(months=1)
            
    df = pd.DataFrame(records)
    # Sort by date
    df['DateObj'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df = df.sort_values('DateObj').reset_index(drop=True)
    
    balances = []
    current_bal = starting_balance
    for _, row in df.iterrows():
        dr = float(row['Debit']) if row['Debit'] != '' else 0.0
        cr = float(row['Credit']) if row['Credit'] != '' else 0.0
        current_bal = current_bal + cr - dr
        balances.append(f"{current_bal:.2f}")
        
    df['Balance'] = balances
    df = df.drop(columns=['DateObj'])
    save_csv(df, filename)

if __name__ == "__main__":
    print("Generating demo statements...")
    process_and_save(build_ramesh, "ramesh_statement.csv", 4500)
    process_and_save(build_priya, "priya_statement.csv", 2200)
    process_and_save(build_vikram, "vikram_statement.csv", 3000)
    process_and_save(build_suresh, "suresh_statement.csv", 18000)
    process_and_save(build_arjun, "arjun_statement.csv", 5000)
    process_and_save(build_deepak, "deepak_statement.csv", 1000)
    print("Done.")
