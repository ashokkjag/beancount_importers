"""
CSV Importer for HDFCBank, India.

Please select the option as "delimited" while importing your statements.

Some cleanup is needed which is included.
1) remove the empty line at the top
2) Trim the spaces before/after the CSV headers
3) remove the ',' inside narrations (which obviously shoundn't be there in first place)
"""

__copyright__ = "Copyright (C) 2025 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"


from beancount.core import data
from beancount.core import amount
from beancount.core.amount import D
from beancount.ingest import importer

from dateutil.parser import parse


import csv
import datetime
import re
from os import path

class Importer(importer.ImporterProtocol):

    def __init__(self, currency, account):
        self.currency = currency
        self.account = account

    def identify(self, file):
        if not re.search("hdfc.*csv$", file.name):
            return False

        lines_to_check = 5
        pattern = "Date.*Narration.*Value Dat.*Debit Amount.*Credit Amount.*Chq/Ref Number.*Closing Balance"
        with open(file.name) as infile:
            for _ in range(lines_to_check):
                line = next(infile).strip()
                if re.match(pattern, line):
                    return True
        return False


    def file_name(self, file):
        return 'hdfcbank.{}.csv'.format(self.file_date(file))

    def file_account(self, _):
        return self.account

    def file_date(self, file):
        transactions = self.cleanup_transactions(file)

        reader = csv.DictReader(transactions)
        for row in reader:
            date= row['Date']
        
        return parse(date, dayfirst=True).date()

    def cleanup_transactions(self, file):
        
        transactions = []
        with open(file.name) as infile:
            #transactions = [re.sub('NETBANK,','NETBANK',re.sub(' {2,}', ' ',line)) for line in infile if line.strip()]
            for line in infile:
                #strip all empty lines
                if line.strip():
                    line = re.sub(' {2,}', ' ',line) #2 or more spaces
                    line = re.sub('^\s*','', line) # spaces at beginning
                    line = re.sub('NETBANK,','NETBANK', line) #specific to NEFT

                    transactions.append(line)
        #remove unnecessary spaces in header
        transactions[0] = re.sub('\s*,\s*',',', transactions[0])
       
        return transactions
    
    def extract(self, file):
        entries = []
        index = 0

        transactions = self.cleanup_transactions(file)

        for index, row in enumerate(csv.DictReader(transactions)):
            meta = data.new_metadata(file.name, index)
            date = parse(row['Date'], dayfirst=True).date()
            narration =f"({row['Narration'].strip()})"
            credit_amt = D(row['Credit Amount'])              
            debit_amt = D(row['Debit Amount'])

            amt = credit_amt - debit_amt

            txn = data.Transaction(
                meta,
                date,
                self.FLAG, #flag
                None, #payee
                narration,
                data.EMPTY_SET, # tags,
                data.EMPTY_SET, # link
                [
                    data.Posting(self.account, 
                                    amount.Amount(D(amt), self.currency),
                                    None, None, None, None),
                ]
            )


            entries.append(txn)
        
        if index:
            balance = row['Closing Balance']
            entries.append(
                data.Balance(meta, 
                            date + datetime.timedelta(days=1),
                            self.account,
                            amount.Amount(D(balance), self.currency),
                            None, None))

        return entries
