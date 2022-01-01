# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.datastructures package.
"""
import os

from pathlib import Path
import pytest

from paperfetcher.datastructures import DOIDataset, CitationsDataset, RISDataset


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


@pytest.fixture
def ris_entry():
    entry = "TY  - JOUR\nDO  - 10.1073/pnas.2018234118\nUR  - http://dx.doi.org/10.1073/pnas.2018234118\nTI  - Identifying hydrophobic protein patches to inform protein interaction interfaces\nT2  - Proceedings of the National Academy of Sciences\nAU  - Rego, Nicholas B.\nAU  - Xi, Erte\nAU  - Patel, Amish J.\nPY  - 2021\nDA  - 2021/02/01\nPB  - Proceedings of the National Academy of Sciences\nSP  - e2018234118\nIS  - 6\nVL  - 118\nSN  - 1091-6490\nER  -"
    return entry


@pytest.fixture
def ris_file():
    path = Path(__file__).parent / "input_data/ris1.ris"
    return path


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


"""RISDataset tests"""


def test_RISDataset_constructors(ris_entry, ris_file):
    # Test constructor to load dataset from RIS-formatted string
    ds1 = RISDataset.from_ris_string(ris_entry)
    print(ds1)
    assert(len(ds1) == 1)

    # Test constructor to load dataset from RIS file
    ds2 = RISDataset.from_ris(ris_file)
    print(ds2)
    assert(len(ds2) == 2)


def test_RISDataset_ris_output(ris_entry):
    # Test RIS reconstruction
    ds = RISDataset.from_ris_string(ris_entry)
    ris_str = RISDataset.to_ris_string(ds)
    print(ris_entry)
    print("---")
    print(ris_str)
    assert(ris_entry.strip() == ris_str.strip())


def test_RISDataset_save_ris(ris_entry):
    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    ds = RISDataset.from_ris_string(ris_entry)
    ds.save_ris("./tmp/risunit.ris")
