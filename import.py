from beancount.core import data
import beangulp

from IN.hdfcbank import hdfcbank_csv
from IN.mf_cas import mf_cas_pdf
from IN.zerodha import zerodha_tradebook_csv

importers = [
    hdfcbank_csv.Importer("INR", "Assets:IN:Hdfcbank:Savings"),
    mf_cas_pdf.Importer("PASSWORD", "INR", "Assets:Investments:MF", "Assets:MF:Cash", "Expenses:Fees"),
    zerodha_tradebook_csv.Importer("INR", "Assets:Investment:Equity:Stocks:Zerodha:1234", "Assets:Zerodha:Cash")
]


def process_extracted_entries(extracted_entries_list, ledger_entries):
    return [
        (filename, entries, account, importer) for filename, entries, account, importer in extracted_entries_list
    ]


hooks = [process_extracted_entries]

if __name__ == "__main__":
    ingest = beangulp.Ingest(importers, [])
    ingest()
