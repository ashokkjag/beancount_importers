import sys
from os import path
sys.path.insert(0, path.join(path.dirname(__file__)))

from IN.hdfcbank import hdfcbank_csv
from IN.icicibank import icicibank_xls


CONFIG = [
    hdfcbank_csv.Importer("INR", "Assets:IN:HDFCBank:Savings"),
    icicibank_xls.Importer("INR", "Assets:IN:ICICIBank:Savings")
]