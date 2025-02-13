# beancount-importers
Some beancount V2 importers for India

Currently supported institutions
- Banks
    - HDFCBank
        - csv/Delimited - File name should match pattern `hdfc.*.csv`
    - ICICIBank
        - xls - File name should match pattern `icici.*.xls`
    - Bank of Baroda
        - csv - File name should match pattern `bob.*.csv`
- Brokers
    - Zerodha
        - CSV Tradebook - File name should match pattern `zerodha.*.csv`
            - Importer adds the symbol name as the commodity name
            - Sell transactions will need manual lot matching

# instructions to use
```
bean-extract sample_import_config.py <filename>
```

# Regression testing
You can run regression tests using

```python
pytest -s -v
```