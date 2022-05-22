# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.handsearch package.
"""
import logging

from paperfetcher import handsearch
from paperfetcher.exceptions import SearchError

logger = logging.getLogger(__name__)

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


def test_fetch_count_errorhandling():
    try:
        handsearch.CrossrefSearch._fetch_count("XXXXX")
    except SearchError as e:
        print(str(e))


def test_fetch_batch():
    data = handsearch.CrossrefSearch._fetch_batch("1476-4687", size=5)
    logger.info(data)
    assert(type(data) == dict)
    assert(len(data['items']) == 5)


def test_fetch_batch_errorhandling():
    try:
        handsearch.CrossrefSearch._fetch_batch("XXXXX", size=5)
    except SearchError as e:
        print(str(e))
