# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.snowballsearch package.
"""
import logging

from paperfetcher import snowballsearch
from paperfetcher.datastructures import DOIDataset
from paperfetcher.exceptions import SearchError

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
    test_1 = snowballsearch.CrossrefBackwardReferenceSearch._check_doi_has_references("10.1021/acs.jpcb.1c02191")
    test_2 = snowballsearch.CrossrefBackwardReferenceSearch._check_doi_has_references("xx.yy.zz/pqr123")
    assert(test_1)
    assert(not test_2)


def test_crback_from_dataset():
    test_ds = DOIDataset(["10.1021/acs.jpcb.1c02191"])
    test = snowballsearch.CrossrefBackwardReferenceSearch.from_DOIDataset(test_ds)
    assert(len(test.search_dois) == 1)
    assert("10.1021/acs.jpcb.1c02191" in test.search_dois)


def test_crback_fetch_all_reference_dois_errorhandling():
    try:
        snowballsearch.CrossrefBackwardReferenceSearch._fetch_all_reference_dois("xx.yy.zz/pqr123")
    except SearchError:
        return True


def test_crback_get_RISDataset():
    search = snowballsearch.CrossrefBackwardReferenceSearch([""])
    search.result_dois = ["10.1021/acs.jpcb.1c02191"]
    print(search.get_RISDataset())


def test_crback_get_RISDataset_errorhandling():
    search = snowballsearch.CrossrefBackwardReferenceSearch([""])
    search.result_dois = ["xx.yy.zz/pqr123"]
    print(search.get_RISDataset())


############################################################################
# COCIBackwardReferenceSearch unit tests
############################################################################


def test_cociback_check_doi_exists():
    test_1 = snowballsearch.COCIBackwardReferenceSearch._check_doi_exists("10.1021/acs.jpcb.1c02191")
    test_2 = snowballsearch.COCIBackwardReferenceSearch._check_doi_exists("xx.yy.zz/pqr123")
    assert(test_1)
    assert(not test_2)


def test_cociback_from_dataset():
    test_ds = DOIDataset(["10.1021/acs.jpcb.1c02191"])
    test = snowballsearch.COCIBackwardReferenceSearch.from_DOIDataset(test_ds)
    assert(len(test.search_dois) == 1)
    assert("10.1021/acs.jpcb.1c02191" in test.search_dois)


def test_cociback_fetch_all_reference_dois_errorhandling():
    try:
        snowballsearch.COCIBackwardReferenceSearch._fetch_all_reference_dois("xx.yy.zz/pqr123")
    except SearchError:
        return True


def test_cociback_get_RISDataset():
    search = snowballsearch.COCIBackwardReferenceSearch([""])
    search.result_dois = ["10.1021/acs.jpcb.1c02191"]
    print(search.get_RISDataset())


def test_cociback_get_RISDataset_errorhandling():
    search = snowballsearch.COCIBackwardReferenceSearch([""])
    search.result_dois = ["xx.yy.zz/pqr123"]
    print(search.get_RISDataset())


############################################################################
# COCIForwardCitationSearch unit tests
############################################################################


def test_cocifwd_check_doi_exists():
    test_1 = snowballsearch.COCIForwardCitationSearch._check_doi_exists("10.1021/acs.jpcb.1c02191")
    test_2 = snowballsearch.COCIForwardCitationSearch._check_doi_exists("xx.yy.zz/pqr123")
    assert(test_1)
    assert(not test_2)


def test_cocifwd_from_dataset():
    test_ds = DOIDataset(["10.1021/acs.jpcb.1c02191"])
    test = snowballsearch.COCIForwardCitationSearch.from_DOIDataset(test_ds)
    assert(len(test.search_dois) == 1)
    assert("10.1021/acs.jpcb.1c02191" in test.search_dois)


def test_cocifwd_fetch_all_citation_dois_errorhandling():
    try:
        snowballsearch.COCIForwardCitationSearch._fetch_all_citation_dois("xx.yy.zz/pqr123")
    except SearchError:
        return True


def test_cocifwd_get_RISDataset():
    search = snowballsearch.COCIForwardCitationSearch([""])
    search.result_dois = ["10.1021/acs.jpcb.1c02191"]
    print(search.get_RISDataset())


def test_cocifwd_get_RISDataset_errorhandling():
    search = snowballsearch.COCIForwardCitationSearch([""])
    search.result_dois = ["xx.yy.zz/pqr123"]
    print(search.get_RISDataset())
