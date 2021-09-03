"""
Custom data structures (classes) for paperfetcher.

@author Akash Pallath
This code is licensed under the MIT license (see LICENSE.txt for details).
"""
import contextlib
import csv
import logging

import pandas as pd

from paperfetcher.exceptions import DatasetError

# Logging
logger = logging.getLogger(__name__)


class Dataset:
    """Abstract class for datasets."""

    # Constructor
    def __init__(self, items: list = []):
        self._items = list(items)

    # Constructors to create objects from disk
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

    # Property
    def __len__(self):
        return len(self._items)

    def append(self, item):
        self._items.append(item)

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
    # Internal representation: list of DOIs
    def __init__(self, items: list):
        super().__init__(items)

    def to_df(self):
        """Converts dataset to DataFrame."""
        return pd.DataFrame(self._items, columns=['DOI'])

    def save_txt(self, file):
        """Saves dataset to .txt file."""
        if hasattr(file, 'write'):
            file_ctx = contextlib.nullcontext(file)
        else:
            if not file.endswith('.txt'):
                file = file + '.txt'
            file_ctx = open(file, "w")

        with file_ctx as f:
            for doi in self._items:
                f.write(doi + "\n")

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
        """Saves dataset to Excel file (uses Pandas)."""
        if not file.endswith('.xlsx'):
            file = file + '.xlsx'
        df = pd.DataFrame(self._items, columns=['DOI'])
        df.to_excel(file)


class CitationsDataset(Dataset):
    # Internal representation: list of fields
    def __init__(self, field_names: tuple, items: list = []):
        super().__init__(items)
        self.field_names = field_names
        self.num_fields = len(field_names)
        for itemidx, item in enumerate(self._items):
            if len(item) != self.num_fields:
                raise DatasetError("Item at index %d is of incorrect length." % itemidx)

    def append(self, item):
        if len(item) != self.num_fields:
            raise DatasetError("Item is of incorrect length.")
        super().append(item)

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
        """Saves dataset to .csv file."""
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
        """Saves dataset to Excel file (uses Pandas)."""
        if not file.endswith('.xlsx'):
            file = file + '.xlsx'
        df = pd.DataFrame(self._items, columns=self.field_names)
        df.to_excel(file)
