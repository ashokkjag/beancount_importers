"""Unit tests for Zerodha tradebook CSV importer (using pytest)."""

__copyright__ = "Copyright (C) 2025 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"

import unittest
from os import path

from beancount.ingest import regression_pytest as regtest
from . import zerodha_tradebook_csv


# Create an importer instance for running the regression tests.
IMPORTER = zerodha_tradebook_csv.Importer("INR", "Assets:Investments:Zerodha", "Assets:Zerodha:Cash")


@regtest.with_importer(IMPORTER)
@regtest.with_testdir(path.dirname(__file__))
class TestImporter(regtest.ImporterTestBase):
    pass


if __name__ == "__main__":
    unittest.main()