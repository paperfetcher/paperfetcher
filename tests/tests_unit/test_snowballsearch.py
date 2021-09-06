# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.snowballsearch package.
"""
import logging
import sys

from paperfetcher import snowballsearch
from paperfetcher.datastructures import DOIDataset

logger = logging.getLogger(__name__)

# Set logging default to DEBUG
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

############################################################################
# CrossrefSearch unit tests
############################################################################


def test_check_doi_exists():
    test_1 = snowballsearch.CrossrefSearch._check_doi_exists("10.1021/acs.jpcb.1c02191")
    test_2 = snowballsearch.CrossrefSearch._check_doi_exists("xx.yy.zz/pqr123")
    assert(test_1)
    assert(not test_2)


def test_check_doi_has_references():
    test = snowballsearch.CrossrefSearch._check_doi_has_references("10.1021/acs.jpcb.1c02191")
    assert(test)


def test_from_dataset():
    test_ds = DOIDataset(["10.1021/acs.jpcb.1c02191"])
    test = snowballsearch.CrossrefSearch.from_DOIDataset(test_ds)
    assert(len(test.search_dois) == 1)
    assert("10.1021/acs.jpcb.1c02191" in test.search_dois)
