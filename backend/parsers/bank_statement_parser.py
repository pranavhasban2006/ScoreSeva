import pandas as pd
import pdfplumber
import re
from datetime import datetime
import numpy as np

class BankStatementParser:
    def __init__(self):
        self.date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%d %b %Y', '%d %b, %Y', '%Y-%m-%d', '%d-%b-%Y', '%d/%m/%y']
        
    def _parse_date(self, date_str):
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None

    def _clean_amount(self, amt_str):
        if pd.isna(amt_str) or not str(amt_str).strip():
            return 0.0
        try:
            return float(str(amt_str).replace(',', '').strip())
        except ValueError:
            return 0.0

    def parse_pdf(self, file_obj):
        transactions = []
        # Matches formats like DD/MM/YYYY, DD-MM-YYYY, DD MMM YYYY, DD-MMM-YYYY
        date_pattern = re.compile(r'(\d{2}[/-]\d{2}[/-]\d{2,4}|\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*-\d{4})', re.IGNORECASE)
        
        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                for line in lines:
                    match = date_pattern.search(line)
                    if match:
                        date_str = match.group(1)
                        date_obj = self._parse_date(date_str)
                        if not date_obj:
                            continue
                        
                        # Process the rest of the line
                        parts = line[match.end():].split()
                        
                        numbers = []
                        desc_parts = []
                        for part in parts:
                            clean_part = part.replace(',', '')
                            try:
                                val = float(clean_part)
                                numbers.append(val)
                            except ValueError:
                                desc_parts.append(part)
                                
                        desc = " ".join(desc_parts)
                        
                        if len(numbers) >= 1:
                            balance = numbers[-1] if len(numbers) >= 2 else None
                            if len(numbers) >= 3:
                                dr = numbers[-3]
                                cr = numbers[-2]
                                bal = numbers[-1]
                                if cr > 0:
                                    transactions.append({'date': date_obj, 'amount': cr, 'description': desc, 'transaction_type': 'CR', 'balance': bal})
                                elif dr > 0:
                                    transactions.append({'date': date_obj, 'amount': dr, 'description': desc, 'transaction_type': 'DR', 'balance': bal})
                            elif len(numbers) == 2:
                                amt = numbers[-2]
                                bal = numbers[-1]
                                if 'CR' in line.upper() or 'DEPOSIT' in line.upper() or 'CREDIT' in line.upper():
                                    transactions.append({'date': date_obj, 'amount': amt, 'description': desc, 'transaction_type': 'CR', 'balance': bal})
                                else:
                                    transactions.append({'date': date_obj, 'amount': amt, 'description': desc, 'transaction_type': 'DR', 'balance': bal})

        return transactions

    def parse_csv(self, file_obj):
        try:
            df = pd.read_csv(file_obj)
        except Exception:
            file_obj.seek(0)
            df = pd.read_csv(file_obj, skipinitialspace=True)
            
        cols = [str(c).lower() for c in df.columns]
        
        date_col = next((c for c in cols if 'date' in c), None)
        desc_col = next((c for c in cols if any(x in c for x in ['desc', 'narration', 'particular', 'remark'])), None)
        bal_col = next((c for c in cols if 'bal' in c), None)
        
        dr_col = next((c for c in cols if any(x in c for x in ['debit', 'withdrawal', 'dr'])), None)
        cr_col = next((c for c in cols if any(x in c for x in ['credit', 'deposit', 'cr'])), None)
        amt_col = next((c for c in cols if 'amount' in c), None)
        type_col = next((c for c in cols if 'type' in c), None)

        transactions = []
        for _, row in df.iterrows():
            if date_col and pd.notna(row[df.columns[cols.index(date_col)]]):
                date_str = str(row[df.columns[cols.index(date_col)]])
                date_obj = self._parse_date(date_str)
                if not date_obj:
                    continue
                
                desc = str(row[df.columns[cols.index(desc_col)]]) if desc_col else ""
                bal = self._clean_amount(row[df.columns[cols.index(bal_col)]]) if bal_col else None
                
                dr_val = self._clean_amount(row[df.columns[cols.index(dr_col)]]) if dr_col else 0.0
                cr_val = self._clean_amount(row[df.columns[cols.index(cr_col)]]) if cr_col else 0.0
                
                if dr_col and cr_col:
                    if cr_val > 0:
                        transactions.append({'date': date_obj, 'amount': cr_val, 'description': desc, 'transaction_type': 'CR', 'balance': bal})
                    if dr_val > 0:
                        transactions.append({'date': date_obj, 'amount': dr_val, 'description': desc, 'transaction_type': 'DR', 'balance': bal})
                elif amt_col:
                    amt_val = self._clean_amount(row[df.columns[cols.index(amt_col)]])
                    t_type = str(row[df.columns[cols.index(type_col)]]).upper() if type_col else ""
                    if 'CR' in t_type or 'C' in t_type or 'DEPOSIT' in t_type:
                        transactions.append({'date': date_obj, 'amount': amt_val, 'description': desc, 'transaction_type': 'CR', 'balance': bal})
                    else:
                        transactions.append({'date': date_obj, 'amount': amt_val, 'description': desc, 'transaction_type': 'DR', 'balance': bal})
                        
        return transactions

    def extract_features(self, transactions):
        if not transactions:
            return {
                "monthly_income_actual": 0.0,
                "income_regularity_score": 0.0,
                "avg_monthly_balance": 0.0,
                "salary_detected": False,
                "emi_obligation_ratio": 0.0,
                "bounce_count": 0,
                "savings_rate": 0.0,
                "spending_volatility": 0.0,
                "cash_withdrawal_ratio": 0.0,
                "hidden_emi_count": 0,
                "large_cr_spike_count": 0,
                "end_of_month_stress_count": 0,
                "financial_stress_score": 0.0,
                "merchant_diversity_score": 0.0,
                "statement_months": 0
            }

        df = pd.DataFrame(transactions)
        df['month_year'] = df['date'].dt.to_period('M')
        
        statement_months = df['month_year'].nunique()
        
        cr_df = df[df['transaction_type'] == 'CR']
        dr_df = df[df['transaction_type'] == 'DR']
        
        monthly_cr = cr_df.groupby('month_year')['amount'].sum()
        monthly_dr = dr_df.groupby('month_year')['amount'].sum()
        
        # INCOME FEATURES
        monthly_income_actual = monthly_cr.median() if not monthly_cr.empty else 0.0
        
        income_std = monthly_cr.std() if len(monthly_cr) > 1 else 0.0
        income_mean = monthly_cr.mean() if not monthly_cr.empty else 0.0
        income_regularity_score = max(0, 100 - (income_std / income_mean * 100)) if income_mean > 0 else 0.0
        
        eom_balances = df.sort_values('date').groupby('month_year').last()['balance'].dropna()
        avg_monthly_balance = eom_balances.mean() if not eom_balances.empty else 0.0
        
        salary_detected = False
        if not cr_df.empty:
            for _, group in cr_df.groupby('amount'):
                if len(group) >= max(1, statement_months * 0.8):
                    days = group['date'].dt.day
                    if days.std() <= 3:
                        salary_detected = True
                        break

        # SPENDING FEATURES
        # EMI Obligation Ratio
        emi_total = 0.0
        main_emi_amount = 0.0
        hidden_emi_count = 0
        if not dr_df.empty:
            recurring_drs = dr_df.groupby('amount').filter(lambda x: len(x) >= max(1, statement_months * 0.8))
            if not recurring_drs.empty:
                for amt, group in recurring_drs.groupby('amount'):
                    if group['date'].dt.day.std() <= 5:
                        emi_total += amt
                        if amt > main_emi_amount:
                            main_emi_amount = amt
                        
                for amt, group in recurring_drs.groupby('amount'):
                    if group['date'].dt.day.std() <= 5:
                        lower_bound = main_emi_amount * 0.98
                        upper_bound = main_emi_amount * 1.02
                        if not (lower_bound <= amt <= upper_bound):
                            hidden_emi_count += 1
                        
        emi_obligation_ratio = (emi_total / monthly_income_actual) if monthly_income_actual > 0 else 0.0
        
        bounce_keywords = ["RTN", "BOUNCE", "RETURN", "DISHONOUR"]
        bounce_count = len(df[df['description'].str.upper().str.contains('|'.join(bounce_keywords), na=False)])
        
        avg_cr = income_mean
        avg_dr = monthly_dr.mean() if not monthly_dr.empty else 0.0
        savings_rate = ((avg_cr - avg_dr) / avg_cr * 100) if avg_cr > 0 else 0.0
        
        dr_std = monthly_dr.std() if len(monthly_dr) > 1 else 0.0
        spending_volatility = (dr_std / avg_dr) if avg_dr > 0 else 0.0
        
        # RISK FEATURES
        cash_keywords = ["ATM", "CASH"]
        cash_withdrawals = dr_df[dr_df['description'].str.upper().str.contains('|'.join(cash_keywords), na=False)]['amount'].sum()
        total_dr = dr_df['amount'].sum()
        cash_withdrawal_ratio = (cash_withdrawals / total_dr * 100) if total_dr > 0 else 0.0
        
        if monthly_income_actual > 0:
            large_cr_spike_count = sum(monthly_cr > 3 * monthly_income_actual)
        else:
            large_cr_spike_count = 0
            
        min_monthly_balances = df.groupby('month_year')['balance'].min()
        end_of_month_stress_count = sum(min_monthly_balances < 500)
        
        financial_stress_score = min(100, (bounce_count * 20) + (end_of_month_stress_count * 10))
        
        categories = ["grocery", "medical", "fuel", "education", "rent", "entertainment", "transfer"]
        unique_categories = set()
        for desc in df['description'].str.lower():
            for cat in categories:
                if cat in desc:
                    unique_categories.add(cat)
        merchant_diversity_score = min(100, (len(unique_categories) / 10) * 100)
        
        features = {
            "monthly_income_actual": float(monthly_income_actual),
            "income_regularity_score": float(income_regularity_score),
            "avg_monthly_balance": float(avg_monthly_balance),
            "salary_detected": bool(salary_detected),
            "emi_obligation_ratio": float(emi_obligation_ratio),
            "bounce_count": int(bounce_count),
            "savings_rate": float(savings_rate),
            "spending_volatility": float(spending_volatility),
            "cash_withdrawal_ratio": float(cash_withdrawal_ratio),
            "hidden_emi_count": int(hidden_emi_count),
            "large_cr_spike_count": int(large_cr_spike_count),
            "end_of_month_stress_count": int(end_of_month_stress_count),
            "financial_stress_score": float(financial_stress_score),
            "merchant_diversity_score": float(merchant_diversity_score),
            "statement_months": int(statement_months)
        }
        
        return features

    def parse(self, file_path_or_obj, file_type='pdf'):
        if isinstance(file_path_or_obj, str):
            with open(file_path_or_obj, 'rb') as f:
                return self._parse_obj(f, file_type)
        else:
            return self._parse_obj(file_path_or_obj, file_type)

    def _parse_obj(self, obj, file_type):
        if file_type.lower() == 'pdf':
            transactions = self.parse_pdf(obj)
        else:
            transactions = self.parse_csv(obj)
            
        features = self.extract_features(transactions)
        
        return {
            "transactions": transactions,
            "features": features
        }
