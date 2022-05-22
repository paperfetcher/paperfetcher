# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Integration tests for paperfetcher.handsearch package.
"""
import logging
import os

from paperfetcher import handsearch
from paperfetcher import parsers

logger = logging.getLogger(__name__)


def test_Crossref_JACS_nokeywords():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", from_date="2020-01-01",
                                       until_date="2020-04-01")
    # fast/low memory search
    search(select=True, select_fields=['DOI'])

    # Check raw
    for idx, result in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(result)
    print(len(search))
    assert(len(search) == 772)


def test_Crossref_JACS_emptykeywords():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=[""], from_date="2020-01-01",
                                       until_date="2020-04-01")
    # fast/low memory search
    search(select=True, select_fields=['DOI'])

    # Check raw
    for idx, result in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(result)
    print(len(search))
    assert(len(search) == 772)


def test_Crossref_JACS_hydration_DOIDataset():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
                                       until_date="2020-01-01")
    search()

    # Check raw
    for idx, result in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(result)
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
    for idx, result in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(result)
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
    ds.save_txt("./tmp/JACS_hydration.txt")

    # Check conversion to csv
    ds.save_csv("./tmp/JACS_hydration.csv")

    # Check conversion to xlsx
    ds.save_excel("./tmp/JACS_hydration.xlsx")


def test_Crossref_PNAS_hydrophobic_RISDataset():
    search = handsearch.CrossrefSearch(ISSN="1091-6490", keyword_list=["hydrophobic"], from_date="2020-01-01",
                                       until_date="2021-05-01")
    search(select=True, select_fields=["DOI", "abstract"])

    # Check raw
    for idx, result in enumerate(search.results):
        logger.info("{}/{}".format(idx + 1, len(search)))
        logger.info(result)
    assert(len(search) == 7)

    # RISDataset without abstract
    ds_noabs = search.get_RISDataset()
    print(ds_noabs.to_ris_string())

    # RISDataset with abstract
    ds_abs = search.get_RISDataset(extra_field_list=["abstract"],
                                   extra_field_parser_list=[None],
                                   extra_field_rispy_tags=["notes_abstract"])
    print(ds_abs.to_ris_string())

    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")

    # Check conversion to RIS without abstracts
    ds_noabs.save_ris("./tmp/PNAS_hydrophobic.ris")

    # Check conversion to RIS with abstracts
    ds_abs.save_ris("./tmp/PNAS_hydrophobic_withabstract.ris")


def test_Crossref_JACS_nomatch_keywords():
    search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["adsjkfhadjklhfjkahserkjhajsdhrf"], from_date="2020-01-01",
                                       until_date="2020-04-01")

    # fast/low memory search
    search(select=True, select_fields=['DOI', 'URL', 'title', 'author', 'issued', 'abstract'])

    print(len(search))
    assert(len(search) == 0)

    # Check DOIDataset
    ds = search.get_DOIDataset()
    print(len(ds))
    assert(len(ds) == 0)

    # Check citations dataset
    ds = search.get_CitationsDataset(field_list=['DOI', 'URL', 'title', 'author', 'issued'],
                                     field_parsers_list=[None, None, parsers.crossref_title_parser,
                                                         parsers.crossref_authors_parser, parsers.crossref_date_parser])
    print(len(ds))
    assert(len(ds) == 0)

    # RISDataset without abstract
    ds_noabs = search.get_RISDataset()
    print(ds_noabs.to_ris_string())
    print(len(ds_noabs))
    assert(len(ds_noabs) == 0)

    # RISDataset with abstract
    ds_abs = search.get_RISDataset(extra_field_list=["abstract"],
                                   extra_field_parser_list=[None],
                                   extra_field_rispy_tags=["notes_abstract"])
    print(ds_abs.to_ris_string())
    print(len(ds_abs))
    assert(len(ds_abs) == 0)
