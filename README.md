# beancount-importers
Some beancount importers for India

Currently supported institutions
- Banks
    - HDFCBank
        - csv/Delimited
    - ICICIBank
        - xls
    - Bank of Baroda
        - csv

# instructions to use
```
bean-extract sample_import_config.py <filename>
```

# Regression testing
You can run regression tests using

```python
pytest -s -v
```