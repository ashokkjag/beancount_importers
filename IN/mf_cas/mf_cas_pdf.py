"""
CSV Importer for CAMS/Kfintech Consolidated Account Statement (CAS)

Uses CASParser[1] to convert to CSV

[1]https://github.com/codereverser/casparser
"""

__copyright__ = "Copyright (C) 2025 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"


from beancount.core import data
from beancount.core import amount
from beancount.core import account
from beancount.core.number import D
from beancount.core.position import Cost
from beancount.ingest import importer

from dateutil.parser import parse

import casparser

import csv
import re
import logging
from os import path



class Importer(importer.ImporterProtocol):

    def __init__(self, password, base_currency, account_root, account_cash):
        self.password = password
        self.base_currency = base_currency
        self.account_root = account_root
        self.account_cash = account_cash

    def identify(self, file):

        if not re.search("cas.*pdf$", file.name):
            return False
        
        transactions = self.fetch_transactions(file)

        if re.search("amc,folio,pan,scheme,advisor,isin,amfi,date,description,amount,units,nav,balance,type,dividend", transactions[0]):
            return True
        return False

    def file_name(self, file):
        return 'mf_cas.{}.pdf'.format(self.file_date(file))

    def file_account(self, _):
        return self.account_root

    def file_date(self, file):
        transactions = self.fetch_transactions(file)
        reader = csv.DictReader(transactions)
        for row in reader:
            date= row['Date']
        return parse(date, dayfirst=True).date()
    
    def fetch_transactions(self, file):
        csv_str = casparser.read_cas_pdf(file.name, self.password, output="csv")
        transactions = csv_str.splitlines()
        return transactions

    def extract(self, file):
        entries = []
        index = 0
        dummy_cost_date = parse("1900-01-01").date()
        dummy_cost_price = D("0")

        transactions = self.fetch_transactions(file)

        for index, row in enumerate(csv.DictReader(transactions)):
            folio = row['folio'].split('/')[0]
            mfShortName = row['amc'].removesuffix("Mutual Fund").strip().replace(' ','')
            accountName = account.join(self.account_root, mfShortName, folio)
            date = parse(row['date']).date()
            meta = data.new_metadata(file.name, index, {"scheme" : row['scheme']})
            narration=f"{row['type']} ({row['description']})"
            isin = row['isin'].strip()
            units = D(row['units'])
            transactionType = row['type']
            value=amount.Amount(D(row['amount']), self.base_currency)
            nav = D(row['nav'])
            
            # print(f"{transactionType} - {units} {isin}({value}) - {accountName} {row['scheme']}")
            
            if transactionType in ("PURCHASE", "SWITCH_IN"):
                
                cost = Cost(nav, self.base_currency, date, None)
                txn = data.Transaction(meta, 
                                        date, 
                                        self.FLAG, 
                                        None, 
                                        narration, 
                                        data.EMPTY_SET,
                                        data.EMPTY_SET,
                                        [
                                            data.Posting(accountName, amount.Amount(units, isin), cost, None, None, None),
                                            data.Posting(self.account_cash, -value, None, None, None, None),
                                        ]
                                    )
            elif transactionType in ("REDEMPTION", "SWITCH_OUT"):
                
                cost = Cost(dummy_cost_price, self.base_currency, dummy_cost_date, None)
                price = amount.Amount(nav, self.base_currency)
                txn = data.Transaction(meta,
                                        date,
                                        self.FLAG,
                                        None,
                                        narration,
                                        data.EMPTY_SET,
                                        data.EMPTY_SET,
                                        [
                                            data.Posting(accountName, amount.Amount(units, isin), cost, price, None, None),
                                            data.Posting(self.account_cash, -value, None, None, None, None ),
                                        ]
                                        )
            elif transactionType in ("STT_TAX", "STAMP_DUTY_TAX"):
                
                txn = data.Transaction(meta,
                                        date,
                                        self.FLAG,
                                        None,
                                        narration,
                                        data.EMPTY_SET,
                                        data.EMPTY_SET,
                                        [
                                            data.Posting(self.account_cash, -value, None, None, None, None ),
                                        ]
                                        )
            else:
                logging.error(f"{transactionType} is unknown. Ignoring line")
                continue

            entries.append(txn)
            

        return entries


