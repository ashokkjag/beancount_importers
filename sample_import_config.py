import sys
from os import path
sys.path.insert(0, path.join(path.dirname(__file__)))

from IN.hdfcbank import hdfcbank_csv
from IN.icicibank import icicibank_xls
from IN.bankofbaroda import bob_csv
from IN.zerodha import zerodha_tradebook_csv
from IN.mf_cas import mf_cas_pdf


CONFIG = [
    hdfcbank_csv.Importer("INR", "Assets:IN:HDFCBank:Savings"),
    icicibank_xls.Importer("INR", "Assets:IN:ICICIBank:Savings"),
    bob_csv.Importer("INR", "Assets:IN:BankOfBaroda:Savings"),
    zerodha_tradebook_csv.Importer("INR", "Assets:Investments:Zerodha", "Assets:Zerodha:Cash"),
    mf_cas_pdf.Importer("PASSWORD", "INR", "Assets:Investments:MF", "Assets:MF:Cash"),
]