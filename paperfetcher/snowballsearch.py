"""
Module documentation goes here.

@author Akash Pallath
This code is licensed under the MIT license (see LICENSE.txt for details).
"""
from collections import OrderedDict
import logging
import pickle
import warnings

from tqdm import tqdm

from paperfetcher.apiclients import CrossrefQuery
from paperfetcher.datastructures import DOIDataset
from paperfetcher.exceptions import QueryError

# Logging
logger = logging.getLogger(__name__)


class CrossrefSearch:
    """
    Retrieves the (DOIs of) all articles cited by a list of (DOIs of) articles.
    """
    def __init__(self, search_dois: list):
        self.search_dois = search_dois
        self.result_dois = set()  # prevent duplicates

    # Alternate constructor
    @classmethod
    def from_DOIDataset(cls, search_dataset: DOIDataset):
        return cls(search_dataset._items)

    # Properties
    def __len__(self):
        return (len(self.result_dois))

    @classmethod
    def _check_doi_exists(cls, doi: str):
        components = OrderedDict([("works", doi)])
        query = CrossrefQuery(components)
        query()
        return query.response.status_code == 200

    @classmethod
    def _check_doi_has_references(cls, doi: str):
        components = OrderedDict([("works", doi)])
        query = CrossrefQuery(components)
        query()

        data = query.response.json()
        doi_dicts = data['message'].get('reference', None)
        if doi_dicts is None:
            return False
        if len(doi_dicts) == 0:
            return False
        return True

    @classmethod
    def _fetch_all_reference_dois(cls, doi: str):
        components = OrderedDict([("works", doi)])
        query = CrossrefQuery(components)
        query()

        data = query.response.json()
        doi_dicts = data['message']['reference']

        reference_dois = []
        for dict in doi_dicts:
            ref_doi = dict.get("DOI", None)
            if ref_doi is not None:
                reference_dois.append(ref_doi)
            else:
                warnings.warn("In references of %s, reference object %s does not have a DOI field." % (doi, dict))  # warn but continue

        return reference_dois

    # Perform search
    def __call__(self):
        for doi in tqdm(self.search_dois):
            # Checks
            if not self._check_doi_exists(doi):
                raise QueryError("DOI %s does not exist." % doi)  # terminate

            if not self._check_doi_has_references(doi):
                warnings.warn("DOI %s does not have reference metadata in Crossref." % doi)  # warn but continue
                break

            # Fetch & update results
            doi_list = self._fetch_all_reference_dois(doi)
            self.result_dois.update(doi_list)

    # Save/load state of search (query & results) to/from file.
    def save(self, file):
        with open(file, "wb") as f:
            pickle.dump(self.__dict__, f)

    def load(self, file):
        self.__dict__.clear()
        with open(file, "rb") as f:
            self.__dict__.update(pickle.load(f))

    # Transform list of DOIs into dataset
    def get_DOIDataset(self):
        return DOIDataset(list(self.result_dois))
