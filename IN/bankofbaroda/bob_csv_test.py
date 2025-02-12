__copyright__ = "Copyright (C) 2025 Ashok Kumar Jagadeeswaran"
__license__ = "GNU AGPLv3"

import unittest
from os import path

from beancount.ingest import regression_pytest as regtest
import bob_csv


# Create an importer instance for running the regression tests.
IMPORTER = bob_csv.Importer("INR", "Assets:Bankofbaroda")


@regtest.with_importer(IMPORTER)
@regtest.with_testdir(path.dirname(__file__))
class TestImporter(regtest.ImporterTestBase):
    pass


if __name__ == "__main__":
    unittest.main()