"""
CSV Importer for Bank Of Baroda, India.
"""

__copyright__ = "Copyright (C) 2025 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"


from beancount.core import data
from beancount.core import amount
from beancount.core.amount import D
from beancount.ingest import importer

from dateutil.parser import parse

import csv
import re
import datetime
from os import path

class Importer(importer.ImporterProtocol):

    def __init__(self, currency, account):
        self.currency = currency
        self.account = account

    def identify(self, file):
        if not re.search("bob.*csv$", file.name):
            return False

        lines_to_check = 25
        pattern = r"TRAN DATE.*,NARRATION.*CHQ.NO..*WITHDRAWAL.*,DEPOSIT.*BALANCE.*"

        with open(file.name) as infile:
            for _ in range(lines_to_check):
                line = next(infile).strip()
                if re.match(pattern, line):
                    return True
                
        return False

    def file_name(self, file):
        return 'bob.{}.csv'.format(self.file_date(file))

    def file_account(self, _):
        return self.account

    def file_date(self, file):

        transactions = self.fetch_transactions(file.name)

        reader = csv.DictReader(transactions)
        for row in reader:
            date= row['DATE']
        
        return parse(date, dayfirst=True).date()

    def fetch_transactions(self,file):
        pattern = r"(BALANCE.INR.,$|Cr,$)"
        with open(file) as infile:
            transactions = []
            for line in infile:
                if line.strip() and re.search(pattern, line):
                    transactions.append(line)
            
        return transactions

    def extract(self, file):
        entries = []
        index = 0
        balance = 0

        transactions = self.fetch_transactions(file.name)

        for index, row in enumerate(csv.DictReader(transactions)):
            meta = data.new_metadata(file.name, index)
            date = parse(row['TRAN DATE'], dayfirst=True).date()
            narration=f"({row['NARRATION'].strip()})"
            debit_amt = D(row['WITHDRAWAL(DR)'])
            credit_amt = D(row['DEPOSIT(CR)'])
            balance = float()

            amt = credit_amt - debit_amt

            txn = data.Transaction(
                meta,
                date,
                self.FLAG,
                None, #payee
                narration,
                data.EMPTY_SET, #tags
                data.EMPTY_SET, #links
                [
                        data.Posting(self.account, amount.Amount(D(amt), self.currency), None, None, None, None),
                ]    
            )

            entries.append(txn)
    
            # Bank of Baroda CSV files are reverse date sorted. 
            # Balance assertion for first entry.
            if index == 0:
                balance = row['BALANCE(INR)'].replace("Cr", "").replace("Dr", "")
                entries.append(
                    data.Balance(meta, 
                                date + datetime.timedelta(days=1),
                                self.account,
                                amount.Amount(D(balance), self.currency),
                                None, None))
        

        return entries


