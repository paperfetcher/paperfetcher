# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Integration tests for paperfetcher.handsearch package.
"""
import logging
import os
import sys

from paperfetcher import handsearch
from paperfetcher import parsers

logger = logging.getLogger(__name__)

# Set logging default to INFO
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def test_Crossref_JACS_hydration_DOIDataset():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search()

    # Check raw
    for idx, batch in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(batch)
    assert(len(search) == 13)

    # Check DOIDataset
    ds = search.get_DOIDataset()
    assert(len(ds) == 13)
    assert("10.1021/jacs.8b11448" in ds._items)

    # Check conversion to DataFrame
    df = ds.to_df()
    print(df)

    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")

    # Check conversion to text
    df = ds.save_txt("./tmp/JACS_hydration_DOIs.txt")
    print(df)

    # Check conversion to csv
    df = ds.save_csv("./tmp/JACS_hydration_DOIs.csv")
    print(df)

    # Check conversion to xlsx
    df = ds.save_excel("./tmp/JACS_hydration_DOIs.xlsx")
    print(df)


def test_Crossref_JACS_hydration_CitationsDataset():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search(select=True, select_fields=['DOI', 'URL', 'title', 'author', 'issued'])

    # Check raw
    for idx, batch in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(batch)
    assert(len(search) == 13)

    # Check DOIDataset
    ds = search.get_DOIDataset()
    assert(len(ds) == 13)
    assert("10.1021/jacs.8b11448" in ds._items)

    # Check CitationsDataset
    ds = search.get_CitationsDataset(field_list=['DOI', 'URL', 'title', 'author', 'issued'],
                                     field_parsers_list=[None, None, parsers.crossref_title_parser,
                                                         parsers.crossref_authors_parser, parsers.crossref_date_parser])
    print(ds._items)
    assert(len(ds) == 13)

    # Check conversion to DataFrame
    df = ds.to_df()
    print(df)

    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")

    # Check conversion to text
    df = ds.save_txt("./tmp/JACS_hydration.txt")
    print(df)

    # Check conversion to csv
    df = ds.save_csv("./tmp/JACS_hydration.csv")
    print(df)

    # Check conversion to xlsx
    df = ds.save_excel("./tmp/JACS_hydration.xlsx")
    print(df)
