"""
CSV Importer for ICICIBank, India.
"""

__copyright__ = "Copyright (C) 2025 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"


from beancount.core import data
from beancount.core import amount
from beancount.core.amount import D
from beancount.ingest import importer

from dateutil.parser import parse

import re
import csv
import datetime

class Importer(importer.ImporterProtocol):

    def __init__(self, currency, account):
        self.currency = currency
        self.account = account

    def identify(self, file):
        if re.search("icici.*xls$", file.name):
            return True 
        return False

    def file_name(self, file):
        return 'icicibank.{}.xls'.format(self.file_date(file))

    def file_account(self, _):
        return self.account

    def file_date(self, file):
        
        transactions = self.fetch_transactions(file)
        
        reader = csv.DictReader(transactions)
        
        for row in reader:
            date= row['Value Date']
        
        return parse(date, dayfirst=True).date()
    
    def fetch_transactions(self, file):
        import xlrd
        import re

        transactions = []

        workbook = xlrd.open_workbook(file.name)
        sheet = workbook.sheet_by_index(0)
        last_col = sheet.ncols - 1

        for rownum in range(sheet.nrows): 
            if sheet.row_values(rownum)[last_col] != '':
                transaction = ",".join(sheet.row_values(rownum)[1:])
                transaction = re.sub(r'\s+', ' ', transaction)
                transactions.append(transaction)
                
        transactions[0] = transactions[0].replace(' (INR )', '')
        
        return transactions

    def extract(self, file):
        entries = []
        index = 0
        transactions = self.fetch_transactions(file)
        
        for index, row in enumerate(csv.DictReader(transactions)):
            meta = data.new_metadata(file.name, index)
            date = parse(row['Transaction Date'], dayfirst=True).date()
            narration=f"({row['Transaction Remarks'].strip()})"
            debit_amt = D(row['Withdrawal Amount'])
            credit_amt = D(row['Deposit Amount'])
            amt = credit_amt - debit_amt

            txn = data.Transaction(
                meta,
                date,
                self.FLAG, #flag
                None, #payee
                narration,
                data.EMPTY_SET, # tags
                data.EMPTY_SET, # links
                [
                    data.Posting(self.account, 
                                    amount.Amount(D(amt), self.currency),
                                    None, None, None, None)
                ]
            )

            entries.append(txn)

        if index:
            balance = row['Balance']
            entries.append(
                data.Balance(meta, 
                            date + datetime.timedelta(days=1),
                            self.account,
                            amount.Amount(D(balance), self.currency),
                            None, None))

        return entries


