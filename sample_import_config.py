import sys
from os import path
sys.path.insert(0, path.join(path.dirname(__file__)))

from IN.hdfcbank import hdfcbank_csv

CONFIG = [
    hdfcbank_csv.Importer("INR", "Assets:IN:HDFCBANK:Savings")
]