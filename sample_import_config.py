import sys
from os import path
sys.path.insert(0, path.join(path.dirname(__file__)))

from IN.hdfcbank import hdfcbank_csv
from IN.icicibank import icicibank_xls
from IN.bankofbaroda import bob_csv


CONFIG = [
    hdfcbank_csv.Importer("INR", "Assets:IN:HDFCBank:Savings"),
    icicibank_xls.Importer("INR", "Assets:IN:ICICIBank:Savings"),
    bob_csv.Importer("INR", "Assets:IN:BankOfBaroda:Savings"),
]