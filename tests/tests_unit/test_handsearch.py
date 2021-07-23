from paperfetcher import handsearch
import logging
import sys
logger = logging.getLogger(__name__)

# Set logging default to DEBUG
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

############################################################################
# CrossrefSearch unit tests
############################################################################


def test_check_issn_exists():
    test_search = handsearch.CrossrefSearch()
    result = test_search._check_issn_exists("1476-4687")
    assert(result)


def test_fetch_count():
    test_search = handsearch.CrossrefSearch()
    count = test_search._fetch_count("1476-4687")
    logger.info(count)
    assert(type(count) == int)


def test_fetch_batch():
    test_search = handsearch.CrossrefSearch()
    data = test_search._fetch_batch("1476-4687", size=5)
    logger.info(data)
    assert(type(data) == dict)
    assert(len(data['items']) == 5)