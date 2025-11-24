from beancount.core import data
import beangulp

from IN.hdfcbank import hdfcbank_csv

importers = [
    hdfcbank_csv.Importer("INR", "Assets:IN:hdfcbank:Savings"),
]


def process_extracted_entries(extracted_entries_list, ledger_entries):
    return [
        (filename, entries, account, importer) for filename, entries, account, importer in extracted_entries_list
    ]


hooks = [process_extracted_entries]

if __name__ == "__main__":
    ingest = beangulp.Ingest(importers, hooks)
    ingest()