from paperfetcher import handsearch
from paperfetcher import parsers
import logging
import sys
logger = logging.getLogger(__name__)

# Set logging default to INFO
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def test_Crossref_JACS_hydration_raw():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search()
    for idx, batch in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(batch)
    assert(len(search) == 13)


def test_Crossref_JACS_hydration_DOIDataset():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search()
    ds = search.get_DOIDataset()
    assert(len(ds) == 13)
    assert("10.1021/jacs.8b11448" in ds._items)


def test_Crossref_JACS_hydration_select_DOIDataset():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search(select=True, select_fields=["DOI"])
    ds = search.get_DOIDataset()
    assert(len(ds) == 13)
    assert("10.1021/jacs.8b11448" in ds._items)


def test_Crossref_JACS_hydration_CitationsDataset():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search()
    ds = search.get_CitationsDataset(field_list=['DOI', 'URL', 'title', 'author', 'issued'],
                                     field_parsers_list=[None, None, parsers.crossref_title_parser,
                                                         parsers.crossref_authors_parser, parsers.crossref_date_parser])
    print(ds._items)
    assert(len(ds) == 13)


def test_Crossref_JACS_hydration_select_CitationsDataset():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search(select=True, select_fields=['DOI', 'URL', 'title', 'author', 'issued'])
    ds = search.get_CitationsDataset(field_list=['DOI', 'URL', 'title', 'author', 'issued'],
                                     field_parsers_list=[None, None, parsers.crossref_title_parser,
                                                         parsers.crossref_authors_parser, parsers.crossref_date_parser])
    print(ds._items)
    assert(len(ds) == 13)
