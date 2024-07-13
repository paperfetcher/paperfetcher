# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Custom data structures for paperfetcher.
"""
import contextlib
import csv
import logging

import pandas as pd
import rispy
from rispy.config import LIST_TYPE_TAGS, TAG_KEY_MAPPING

from paperfetcher import GlobalConfig
from paperfetcher.exceptions import DatasetError

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(GlobalConfig.loglevel)


class Dataset:
    """
    Abstract interface that defines functions for child Dataset classes to implement.

    Datasets are designed to store [usually tabular] data (as input to or output from paperfetcher searches), export
    data to pandas DataFrames, and load/save data to disk using common data formats (txt, csv, xlsx).

    Args:
        items (iterable): Items to store in dataset (default=[]).
    """
    def __init__(self, items: list = []):
        self._items = list(items)

    @classmethod
    def from_txt(cls, file):
        """Loads dataset from .txt file."""
        # Child class must implement this.
        raise NotImplementedError()

    @classmethod
    def from_csv(cls, file):
        """Loads dataset from .csv file."""
        # Child class must implement this.
        raise NotImplementedError()

    @classmethod
    def from_excel(cls, file):
        """Loads dataset from Excel file file."""
        # Child class must implement this.
        raise NotImplementedError()

    # Properties
    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return self.__class__.__name__ + " with {} items: ".format(len(self)) + repr(self._items)

    def append(self, item):
        """Adds an item to the dataset."""
        self._items.append(item)

    def extend(self, items: list):
        """Adds each item from a list of items to the dataset."""
        self._items.extend(items)

    # Export to pandas
    def to_df(self):
        """Converts dataset to DataFrame."""
        # Child class must implement this.
        raise NotImplementedError()

    # Export to disk
    def save_txt(self, file):
        """Saves dataset to .txt file."""
        # Child class must implement this.
        raise NotImplementedError()

    def save_csv(self, file):
        """Saves dataset to .csv file."""
        # Child class must implement this.
        raise NotImplementedError()

    def save_excel(self, file):
        """Saves dataset to Excel file."""
        # Child class must implement this.
        raise NotImplementedError()


class DOIDataset(Dataset):
    """
    Stores a dataset of DOIs.

    DOIDatasets can be exported to pandas DataFrames, and loaded from or saved to disk
    in text, CSV, or Excel file formats.

    Args:
        items (list): List of DOIs (str) to store (default=[]).

    Examples:
        To create a DOIDataset object from a list of DOIs:

        >>> ds = DOIDataset(["x1.y1.z1/123123", "x2.y2.z2/456456"])

        To add a DOI to the DOIDataset object:

        >>> ds.append("x3.y3.z3/789789")

        To export the DOIDataset object to a pandas DataFrame:

        >>> df = ds.to_df()
        >>> df
                       DOI
        0  x1.y1.z1/123123
        1  x2.y2.z2/456456
        3  x3.y3.z3/789789

        To save data to disk:

        >>> ds.save_txt("dois.txt")
        >>> ds.save_csv("dois.csv")
        >>> ds.save_excel("dois.xlsx")
    """
    def __init__(self, items: list = []):
        super().__init__(items)

    def extend_dataset(self, ds: 'DOIDataset'):
        """Appends all items from DOIDataset ds to the end of the current dataset."""
        self.extend(ds._items)

    def to_df(self):
        """Converts dataset to DataFrame."""
        return pd.DataFrame(self._items, columns=['DOI'])

    def to_txt_string(self):
        """Returns a string which can be written to .txt file"""
        txt = ""
        for doi in self._items:
            txt = txt + doi + "\n"
        return txt

    def save_txt(self, file):
        """Saves dataset to .txt file."""
        if hasattr(file, 'write'):
            file_ctx = contextlib.nullcontext(file)
        else:
            if not file.endswith('.txt'):
                file = file + '.txt'
            file_ctx = open(file, "w")

        with file_ctx as f:
            f.write(self.to_txt_string())

    def save_csv(self, file):
        """Saves dataset to .csv file."""
        if hasattr(file, 'write'):
            file_ctx = contextlib.nullcontext(file)
        else:
            if not file.endswith('.csv'):
                file = file + '.csv'
            file_ctx = open(file, "w")

        with file_ctx as f:
            write = csv.writer(f)
            write.writerow(["DOI"])
            write.writerows([[item] for item in self._items])

    def save_excel(self, file):
        """Saves dataset to Excel file."""
        if not file.endswith('.xlsx'):
            file = file + '.xlsx'
        df = pd.DataFrame(self._items, columns=['DOI'])
        df.to_excel(file)


class CitationsDataset(Dataset):
    """
    Stores a tabular dataset of citations, with multiple custom fields.

    CitationsDatasets can be exported to pandas DataFrames, and loaded from or saved to disk
    in text, CSV, or Excel file formats.

    Args:
        field_names (tuple): Names (str) of fields.
        items (list): List of citations to store (default=[]). Each citation should be an iterable of length len(field_names).

    Examples:
        To create a CitationsDataset object to store the DOI, URL, article title, authors, and date of issue for each citation:

        >>> field_names = ["DOI", "URL", "title", "author", "issued"]
        >>> data = [["10.xxyy/0.0.0.000001", "https://dx.doi.org/10.xxyy/0.0.0.000001", "A study of A", "P, Q and R", "2020-02-20"],
        ...         ["10.xxyy/0.0.0.000002", "https://dx.doi.org/10.xxyy/0.0.0.000002", "An investigation into B", "Q, R and P", "2020-03-20"],
        ...         ["10.xxyy/0.0.0.000003", "https://dx.doi.org/10.xxyy/0.0.0.000003", "The causes of C in D", "R, P and Q", "2020-04-20"],
        ...         ["10.xxyy/0.0.0.000004", "https://dx.doi.org/10.xxyy/0.0.0.000004", "Characterizing the role of E on F", "P and Q", "2020-05-20"]]
        >>> ds = CitationsDataset(field_names, data)

        To add a citation to the CitationsDataset:

        >>> ds.append(["10.xxyy/0.0.0.000005", "https://dx.doi.org/10.xxyy/0.0.0.000005", "The G effect", "Q and P", "2020-06-20"])

        To export the DOIDataset object to a pandas DataFrame:

        >>> df = ds.to_df()
        >>> df
                            DOI                                      URL                              title      author      issued
        0  10.xxyy/0.0.0.000001  https://dx.doi.org/10.xxyy/0.0.0.000001                       A study of A  P, Q and R  2020-02-20
        1  10.xxyy/0.0.0.000002  https://dx.doi.org/10.xxyy/0.0.0.000002            An investigation into B  Q, R and P  2020-03-20
        2  10.xxyy/0.0.0.000003  https://dx.doi.org/10.xxyy/0.0.0.000003               The causes of C in D  R, P and Q  2020-04-20
        3  10.xxyy/0.0.0.000004  https://dx.doi.org/10.xxyy/0.0.0.000004  Characterizing the role of E on F     P and Q  2020-05-20
        4  10.xxyy/0.0.0.000005  https://dx.doi.org/10.xxyy/0.0.0.000005                       The G effect     Q and P  2020-06-20

        To save data to disk:

        >>> ds.save_txt("cits.txt")
        >>> ds.save_csv("cits.csv")
        >>> ds.save_excel("cits.xlsx")
    """
    def __init__(self, field_names: tuple, items: list = []):
        super().__init__(items)
        self.field_names = field_names
        self.num_fields = len(field_names)
        for itemidx, item in enumerate(self._items):
            if len(item) != self.num_fields:
                raise DatasetError("Item at index %d is of incorrect length." % itemidx)

    def append(self, item):
        """Adds a citation to the dataset."""
        if len(item) != self.num_fields:
            raise DatasetError("Item is of incorrect length.")
        super().append(item)

    def extend(self, items):
        """Adds each citation from a list of citations (i.e. eacher inner list of nested list) to the dataset."""
        for itemidx, item in enumerate(items):
            if len(item) != self.num_fields:
                raise DatasetError("Item at index %d is of incorrect length." % itemidx)
        super().extend(items)

    def to_df(self):
        """Converts dataset to DataFrame."""
        return pd.DataFrame(self._items, columns=self.field_names)

    def save_txt(self, file):
        """Saves dataset to .txt file."""
        if hasattr(file, 'write'):
            file_ctx = contextlib.nullcontext(file)
        else:
            if not file.endswith('.txt'):
                file = file + '.txt'
            file_ctx = open(file, "w")

        with file_ctx as f:
            f.write("\t".join(self.field_names) + "\n")
            for item in self._items:
                f.write("\t".join(item) + "\n")

    def save_csv(self, file):
        """Saves dataset to .csv file. The first row of the CSV file contains field names."""
        if hasattr(file, 'write'):
            file_ctx = contextlib.nullcontext(file)
        else:
            if not file.endswith('.csv'):
                file = file + '.csv'
            file_ctx = open(file, "w")

        with file_ctx as f:
            write = csv.writer(f)
            write.writerow(self.field_names)
            write.writerows(self._items)

    def save_excel(self, file):
        """Saves dataset to Excel file (uses Pandas). The first row of the Excel file contains field names."""
        if not file.endswith('.xlsx'):
            file = file + '.xlsx'
        df = pd.DataFrame(self._items, columns=self.field_names)
        df.to_excel(file)


# rispy modification to remove header containing reference number from RIS output
class HeadlessRISWriter(rispy.writer.BaseWriter):
    START_TAG = "TY"
    PATTERN = "{tag}  - {value}"
    DEFAULT_MAPPING = TAG_KEY_MAPPING
    DEFAULT_LIST_TAGS = LIST_TYPE_TAGS
    DEFAULT_DELIMITER_MAPPING = {"UR": ";"}
    

class RISDataset(Dataset):
    """
    Stores a dataset of RIS items. RIS items are rispy-readable dictionaries.

    An RISDataset can be created from an RIS-formatted string, or from an RIS file.
    An RISDataset can be written to an RIS-formatted string, or to an RIS file.
    Individual item dictionaries in an RISDataset can be modified to add new tags or change
    the values of existing tags.

    Args:
        items (list): List of citations to store (default=[]). Each citation should be a rispy-readable dictionary.

    Examples:
        To create an RISDataset from a list of rispy-readable dictionaries (see rispy doc on GitHub for details):

        >>> dict_list = [{'journal_name': ...}, {'journal_name: ...'}, ...]
        >>> ds = RISDataset(dict_list)

        To load an RISDataset from an RIS-formatted string:
        >>> ds = RISDataset.from_ris_string(ris_string)

        To load an RISDataset from an RIS file:
        >>> ds = RISDataset.from_ris(ris_file)
    """
    def __init__(self, items: list = []):
        super().__init__(items)

    @classmethod
    def from_ris_string(cls, ris_string):
        """Loads dataset from RIS-formatted string."""
        items = rispy.loads(ris_string)
        return cls(items)

    @classmethod
    def from_ris(cls, file):
        """Loads dataset from RIS file."""
        with open(file, 'r') as f:
            items = rispy.load(f)
        return cls(items)

    def extend_dataset(self, ds: 'RISDataset'):
        """Appends all items from RISDataset ds to the end of the current dataset."""
        self.extend(ds._items)

    def to_ris_string(self, headers=False):
        """Returns a string which can be written to .ris file.

        Args:
            headers (bool, default=False): If set to true, writes reference number before each RIS entry."""
        if headers:
            return rispy.dumps(self._items)
        else:
            return rispy.dumps(self._items, implementation=HeadlessRISWriter)

    def save_ris(self, filename, headers=False):
        """Saves dataset to .ris file.

        Args:
            filename: Path to file to write RIS data to.
            headers (bool, default=False): If set to true, writes reference number before each RIS entry."""
        if headers:
            with open(filename, 'w') as f:
                rispy.dump(self._items, f)
        else:
            with open(filename, 'w') as f:
                rispy.dump(self._items, f, implementation=HeadlessRISWriter)
