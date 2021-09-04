# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.apiclients package.
"""
import logging
import sys

from paperfetcher.apiclients import Query, CrossrefQuery, QueryError

logger = logging.getLogger(__name__)

# Set logging default to DEBUG
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


"""Query tests"""


def test_query():
    query = Query("https://api.github.com")
    query()
    logger.info(query.response.text)


def test_query_fail():
    query = Query("https://www.google.google")
    try:
        query()
    except QueryError:
        return True
    else:
        return False


"""CrossrefQuery tests"""


def test_crossref_query():
    query = CrossrefQuery()
    query.query_base += "works"
    query()
    logger.info(query.response.text)


def test_json():
    query = CrossrefQuery()
    query.query_base += "works"
    query()
    logger.info(query.response.json())
