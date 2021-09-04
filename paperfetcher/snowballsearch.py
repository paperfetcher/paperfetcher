# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Classes to fetch all journal articles cited by a set of journal articles by querying various APIs.

Note:
    Only the Crossref REST API is supported for now. Support for other APIs will be added soon.
"""
from collections import OrderedDict
import logging
import pickle
import warnings

from tqdm import tqdm

from paperfetcher.apiclients import CrossrefQuery
from paperfetcher.datastructures import DOIDataset
from paperfetcher.exceptions import SearchError

# Logging
logger = logging.getLogger(__name__)


class CrossrefSearch:
    """
    Retrieves the (DOIs of) all articles cited by a list of (DOIs of) articles.

    Args:
        search_dois (list): List of DOIs (str) to fetch references of.

    Attributes:
        search_dois (list): List of DOIs (str) to fetch references of.
        result_dois (set): Set of DOIs which are cited by the DOIs in `search_dois`.

    Example:
        >>> search = snowballsearch.CrossrefSearch(["10.1021/acs.jpcb.1c02191", "10.1073/pnas.2018234118"])
        >>> search()
        >>> len(search)
        140
        >>> search.result_dois
        {'10.1021/jp972543+', '10.1073/pnas.0708088105',  ... ,  '10.1073/pnas.0705830104'}
    """
    def __init__(self, search_dois: list):
        self.search_dois = search_dois
        self.result_dois = set()  # prevent duplicates

    # Alternate constructor
    @classmethod
    def from_DOIDataset(cls, search_dataset: DOIDataset):
        """
        Constructs a CrossrefSearch object from a DOIDataset.

        Args:
            search_dataset (DOIDataset): Dataset of DOIs to fetch references of.

        Returns:
            CrossrefSearch
        """
        return cls(search_dataset._items)

    # Properties
    def __len__(self):
        return (len(self.result_dois))

    @classmethod
    def _check_doi_exists(cls, doi: str):
        """
        Checks if DOI is indexed in Crossref.

        Args:
            doi (str): DOI to check.

        Returns:
            bool
        """
        components = OrderedDict([("works", doi)])
        query = CrossrefQuery(components)
        query()
        return query.response.status_code == 200

    @classmethod
    def _check_doi_has_references(cls, doi: str):
        """
        Checks if DOI has references indexed in Crossref.

        Args:
            doi (str): DOI to check.

        Returns:
            bool
        """
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
        """
        Fetches all references of DOI from Crossref.

        Args:
            doi (str): DOI to fetch references of.

        Returns:
            reference_dois (list): List of DOIs

        Raises:
            SearchError if DOI is not indexed in Crossref.
        """
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
                raise SearchError("DOI %s does not exist." % doi)  # terminate

            if not self._check_doi_has_references(doi):
                warnings.warn("DOI %s does not have reference metadata in Crossref." % doi)  # warn but continue
                break

            # Fetch & update results
            doi_list = self._fetch_all_reference_dois(doi)
            self.result_dois.update(doi_list)

    def save(self, file):
        """
        Saves search object (query and results) to file.

        Args:
            file (str): Name of file (.pkl extension)
        """
        with open(file, "wb") as f:
            pickle.dump(self.__dict__, f)

    def load(self, file):
        """
        Loads search data (query data and results) from file.

        Args:
            file (str): Name of file (.pkl extension)
        """
        self.__dict__.clear()
        with open(file, "rb") as f:
            self.__dict__.update(pickle.load(f))

    def get_DOIDataset(self):
        """
        Returns search results as a DOIDataset object.

        Returns:
            DOIDataset
        """
        return DOIDataset(list(self.result_dois))
