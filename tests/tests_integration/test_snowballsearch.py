# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Integration tests for paperfetcher.snowballsearch package.
"""
from paperfetcher import snowballsearch

import logging
import sys

logger = logging.getLogger(__name__)

# Set logging default to INFO
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def test_Crossref_JPCB():
    input_DOIs = ["10.1021/acs.jpcb.1c02191", "10.1073/pnas.2018234118"]
    test_output_DOI_members = ["10.1021/acs.jpcb.8b11423"]

    search = snowballsearch.CrossrefSearch(input_DOIs)
    search()
    print(len(search))
    print(search.result_dois)
    for doi in test_output_DOI_members:
        assert(doi in search.result_dois)
