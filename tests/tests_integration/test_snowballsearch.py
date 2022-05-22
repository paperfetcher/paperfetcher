# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Integration tests for paperfetcher.snowballsearch package.
"""
import logging
import os

from paperfetcher import snowballsearch

logger = logging.getLogger(__name__)


def test_CrossrefBackward():
    input_DOIs = ["10.1021/acs.jpcb.1c02191", "10.1073/pnas.2018234118"]
    test_output_DOI_members = ["10.1021/acs.jpcb.8b11423"]

    search = snowballsearch.CrossrefBackwardReferenceSearch(input_DOIs)
    search()

    print(len(search))  # should be 140
    assert(len(search) == 140)

    print(search.result_dois)
    for doi in test_output_DOI_members:
        assert(doi in search.result_dois)

    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")

    doi_ds = search.get_DOIDataset()

    ris_ds = search.get_RISDataset()

    # Check conversion to text
    doi_ds.save_txt("./tmp/snowball_crossref_back.txt")

    # Check conversion to RIS
    ris_ds.save_ris("./tmp/snowball_crossref_back.ris")


def test_CrossrefBackward_errorhandling():
    input_DOIs = ["10.1021/acs.jpcb.1c02191", "xx.yy.zz/12345.67890", "10.1146/annurev-conmatphys-040220-045516", "10.1073/pnas.2018234118"]
    # xx.yy.zz/12345.67890 does not exist
    # annual reviews does not, at present, index its references in Crossref

    test_output_DOI_members = ["10.1021/acs.jpcb.8b11423"]

    search = snowballsearch.CrossrefBackwardReferenceSearch(input_DOIs)
    search()

    print(len(search))  # should be 140
    assert(len(search) == 140)

    print(search.result_dois)
    for doi in test_output_DOI_members:
        assert(doi in search.result_dois)


def test_COCIBackward():
    input_DOIs = ["10.1021/acs.jpcb.1c02191", "10.1073/pnas.2018234118"]
    test_output_DOI_members = ["10.1021/acs.jpcb.8b11423"]

    search = snowballsearch.COCIBackwardReferenceSearch(input_DOIs)
    search()

    print(len(search))  # should be 140
    assert(len(search) == 140)

    print(search.result_dois)
    for doi in test_output_DOI_members:
        assert(doi in search.result_dois)

    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")

    doi_ds = search.get_DOIDataset()

    ris_ds = search.get_RISDataset()

    # Check conversion to text
    doi_ds.save_txt("./tmp/snowball_COCI_back.txt")

    # Check conversion to RIS
    ris_ds.save_ris("./tmp/snowball_COCI_back.ris")


def test_COCIBackward_errorhandling():
    input_DOIs = ["10.1021/acs.jpcb.1c02191", "xx.yy.zz/12345.67890", "10.1146/annurev-conmatphys-040220-045516", "10.1073/pnas.2018234118"]
    # xx.yy.zz/12345.67890 does not exist
    # annual reviews does not, at present, index its references in Crossref or COCI

    test_output_DOI_members = ["10.1021/acs.jpcb.8b11423"]

    search = snowballsearch.COCIBackwardReferenceSearch(input_DOIs)
    search()

    print(len(search))  # should be 140
    assert(len(search) == 140)

    print(search.result_dois)
    for doi in test_output_DOI_members:
        assert(doi in search.result_dois)


def test_COCIForward():
    input_DOIs = ["10.1021/acs.jpcb.8b11423", "10.1073/pnas.2018234118"]
    test_output_DOI_members = ["10.1021/acs.jpcb.1c02191"]

    search = snowballsearch.COCIForwardCitationSearch(input_DOIs)
    search()
    print(len(search))
    print(search.result_dois)
    for doi in test_output_DOI_members:
        assert(doi in search.result_dois)

    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")

    doi_ds = search.get_DOIDataset()

    ris_ds = search.get_RISDataset()

    # Check conversion to text
    doi_ds.save_txt("./tmp/snowball_COCI_fwd.txt")

    # Check conversion to RIS
    ris_ds.save_ris("./tmp/snowball_COCI_fwd.ris")


def test_COCIForward_errorhandling():
    input_DOIs = ["10.1021/acs.jpcb.8b11423", "xx.yy.zz/12345.67890", "10.1146/annurev-conmatphys-040220-045516", "10.1073/pnas.2018234118"]
    test_output_DOI_members = ["10.1021/acs.jpcb.1c02191"]

    search = snowballsearch.COCIForwardCitationSearch(input_DOIs)
    search()

    print(len(search))  # this will change with time, do NOT test this value

    print(search.result_dois)
    for doi in test_output_DOI_members:
        assert(doi in search.result_dois)
