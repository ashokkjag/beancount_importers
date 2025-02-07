"""Unit tests for HDFCBank CSV importer (using pytest)."""

__copyright__ = "Copyright (C) 2025 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"

import unittest
from os import path

from beancount.ingest import regression_pytest as regtest
from . import hdfcbank_csv


# Create an importer instance for running the regression tests.
IMPORTER = hdfcbank_csv.Importer("INR", "Assets:HDFCBank")


@regtest.with_importer(IMPORTER)
@regtest.with_testdir(path.dirname(__file__))
class TestImporter(regtest.ImporterTestBase):
    pass


if __name__ == "__main__":
    unittest.main()