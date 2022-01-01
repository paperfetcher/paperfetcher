# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.handsearch package.
"""
import logging
import sys

from paperfetcher import handsearch

logger = logging.getLogger(__name__)

# Set logging default to DEBUG - this loads query-related data as well.
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

############################################################################
# CrossrefSearch unit tests
############################################################################


def test_check_issn_exists():
    result = handsearch.CrossrefSearch._check_issn_exists("1476-4687")
    assert(result)


def test_fetch_count():
    count = handsearch.CrossrefSearch._fetch_count("1476-4687")
    logger.info(count)
    assert(type(count) == int)


def test_fetch_batch():
    data = handsearch.CrossrefSearch._fetch_batch("1476-4687", size=5)
    logger.info(data)
    assert(type(data) == dict)
    assert(len(data['items']) == 5)


def test_content_negotiation():
    data = handsearch.CrossrefSearch._negotiate_ris(doi="10.1073/pnas.2018234118")
    logger.info(data)
