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

############################################################################
# CrossrefBackwardReferenceSearch unit tests
############################################################################


def test_crback_check_doi_exists():
    test_1 = snowballsearch.CrossrefBackwardReferenceSearch._check_doi_exists("10.1021/acs.jpcb.1c02191")
    test_2 = snowballsearch.CrossrefBackwardReferenceSearch._check_doi_exists("xx.yy.zz/pqr123")
    assert(test_1)
    assert(not test_2)


def test_crback_check_doi_has_references():
    test = snowballsearch.CrossrefBackwardReferenceSearch._check_doi_has_references("10.1021/acs.jpcb.1c02191")
    assert(test)


def test_crback_from_dataset():
    test_ds = DOIDataset(["10.1021/acs.jpcb.1c02191"])
    test = snowballsearch.CrossrefBackwardReferenceSearch.from_DOIDataset(test_ds)
    assert(len(test.search_dois) == 1)
    assert("10.1021/acs.jpcb.1c02191" in test.search_dois)
