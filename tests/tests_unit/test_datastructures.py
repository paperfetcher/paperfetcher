# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.datastructures package.
"""
import logging
import os
import sys

import pytest

from paperfetcher.datastructures import DOIDataset, CitationsDataset

logger = logging.getLogger(__name__)

# Set logging default to DEBUG
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


"""DOIDataset tests"""


@pytest.fixture
def doids():
    data = ["10.xxyy/0.0.0.000001",
            "10.xxyy/0.0.0.000002",
            "10.xxyy/0.0.0.000003",
            "10.xxyy/0.0.0.000004",
            "10.xxyy/0.0.0.000005"]
    return DOIDataset(data)


@pytest.fixture
def citds():
    field_names = ["DOI", "URL", "title", "author", "issued"]
    data = [["10.xxyy/0.0.0.000001", "https://dx.doi.org/10.xxyy/0.0.0.000001", "A study of A", "P, Q and R", "2020-02-20"],
            ["10.xxyy/0.0.0.000002", "https://dx.doi.org/10.xxyy/0.0.0.000002", "An investigation into B", "Q, R and P", "2020-03-20"],
            ["10.xxyy/0.0.0.000003", "https://dx.doi.org/10.xxyy/0.0.0.000003", "The causes of C in D", "R, P and Q", "2020-04-20"],
            ["10.xxyy/0.0.0.000004", "https://dx.doi.org/10.xxyy/0.0.0.000004", "Characterizing the role of E on F", "P and Q", "2020-05-20"],
            ["10.xxyy/0.0.0.000005", "https://dx.doi.org/10.xxyy/0.0.0.000005", "The G effect", "Q and P", "2020-06-20"]]
    return CitationsDataset(field_names, data)


def test_DOIDataset_to_df(doids):
    df = doids.to_df()
    print(df)


def test_DOIDataset_save_txt(doids):
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    doids.save_txt("./tmp/doiunit.txt")


def test_DOIDataset_save_csv(doids):
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    doids.save_csv("./tmp/doiunit.csv")


def test_DOIDataset_save_excel(doids):
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    doids.save_excel("./tmp/doiunit.xlsx")


"""CitationsDataset tests"""


def test_CitationsDataset_to_df(citds):
    df = citds.to_df()
    print(df)


def test_CitationsDataset_save_txt(citds):
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    citds.save_txt("./tmp/citunit.txt")


def test_CitationsDataset_save_csv(citds):
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    citds.save_csv("./tmp/citunit.csv")


def test_CitationsDataset_save_xlsx(citds):
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    citds.save_excel("./tmp/citunit.xlsx")
