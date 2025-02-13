"""
CSV Importer for CSV Tradebook from Zerodha, India.
"""

__copyright__ = "Copyright (C) 2024 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"


from beancount.core import data
from beancount.core import number
from beancount.core import amount
from beancount.core import position
from beancount.ingest import importer
from beancount.core.amount import D

from dateutil.parser import parse
# from decimal import Decimal

import csv
import datetime
import re
import logging
from os import path

class Importer(importer.ImporterProtocol):

    def __init__(self, currency, account_root, account_cash):
        self.currency = currency
        self.account_root = account_root
        self.account_cash = account_cash
        
    def identify(self, file):
        if not re.search("zerodha.*csv$", file.name):
            return False
        return re.match("symbol,isin,trade_date,exchange,segment,series,trade_type,auction,quantity,price,trade_id,order_id,order_execution_time", file.head())

    def file_name(self, file):
        return 'zerodha.{}.csv'.format(self.file_date(file))

    def file_account(self, _):
        return self.account_root

    def file_date(self, file):
        with open(file.name) as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                date= row['trade_date']
            return parse(date).date()

    def extract(self, file):
        entries = []
        index = 0

        with open(file.name) as infile:
            currency_precision = D("0.01")
            commodity_precision = D("0.0001")
            for index, row in enumerate(csv.DictReader(infile)):
                meta = data.new_metadata(file.name, index)
                date = parse(row['trade_date']).date()
                ticker = row['symbol']
                trade_type = row['trade_type']
                narration = f"{trade_type} {ticker} on {row['exchange']} (order id {row['order_id']})"
                price = number.round_to(D(row['price'].strip()), currency_precision)
                price_units = amount.Amount(price, self.currency)
                
                quantity = number.round_to(D(row['quantity']), commodity_precision)
                quantity_units = amount.Amount(quantity, ticker)

                total = amount.mul(price_units, quantity)

                # print(f"{date} {trade_type} {quantity} x {price_units} of {ticker} for {total}")

                if trade_type == 'buy':
                    

                    cost = position.Cost(price, self.currency, date, None)

                    txn = data.Transaction(
                        meta,
                        date,
                        self.FLAG,
                        None,
                        narration,
                        data.EMPTY_SET,
                        data.EMPTY_SET,
                        [
                            data.Posting(self.account_root, quantity_units, cost, None, None, None),
                            data.Posting(self.account_cash, -total, None, None, None, None),
                        ]
                        )
             
                elif trade_type == 'sell':
                    # this will need manual matching of lots
                    cost = position.Cost(None, self.currency, None, None)

                    txn = data.Transaction(
                        meta,
                        date,
                        self.FLAG,
                        None,
                        narration,
                        data.EMPTY_SET,
                        data.EMPTY_SET,
                        [
                            data.Posting(self.account_root, -quantity_units, cost, price_units, None, None),
                            data.Posting(self.account_cash, total, None, None, None, None),
                        ]
                    )
                else:
                    logging.error(f"unknown trade_type {trade_type}")
                    continue
                entries.append(txn)             

        return entries


