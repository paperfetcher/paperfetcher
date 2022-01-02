# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Classes to fetch all journal articles in the references of (i.e. backward search)
or citing (i.e. forward search) a set of journal articles.

For backward search, you can use either Crossref or COCI (should be equivalent).
For forward search, you can only use COCI at the moment.
"""
from collections import OrderedDict
import logging
import warnings

from tqdm import tqdm
from stqdm import stqdm

from paperfetcher import GlobalConfig
from paperfetcher.apiclients import CrossrefQuery, COCIQuery
from paperfetcher.content_negotiators import crossref_negotiate_ris
from paperfetcher.datastructures import DOIDataset, RISDataset
from paperfetcher.exceptions import SearchError

# Logging
logger = logging.getLogger(__name__)


class CrossrefBackwardReferenceSearch:
    """
    Retrieves the (DOIs of) all articles in the references of a list of (DOIs of) articles
    by using the Crossref REST API.

    Args:
        search_dois (list): List of DOIs (str) to fetch references of.

    Attributes:
        search_dois (list): List of DOIs (str) to fetch references of.
        result_dois (set): Set of DOIs which are referenced by the DOIs in `search_dois`.

    Example:
        >>> search = snowballsearch.CrossrefBackwardReferenceSearch(["10.1021/acs.jpcb.1c02191", "10.1073/pnas.2018234118"])
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
        Constructs a search object from a DOIDataset.

        Args:
            search_dataset (DOIDataset): Dataset of DOIs to fetch references of.

        Returns:
            CrossrefBackwardReferenceSearch
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
        if GlobalConfig.streamlit:
            iterable = stqdm(self.search_dois)
        else:
            iterable = tqdm(self.search_dois)

        for doi in iterable:
            # Checks
            if not self._check_doi_exists(doi):
                raise SearchError("DOI %s does not exist." % doi)  # terminate

            if not self._check_doi_has_references(doi):
                warnings.warn("DOI %s does not have reference metadata in Crossref." % doi)  # warn but continue
                break

            # Fetch & update results
            doi_list = self._fetch_all_reference_dois(doi)
            self.result_dois.update(doi_list)

    def get_DOIDataset(self):
        """
        Returns search results as a DOIDataset object.

        Returns:
            DOIDataset
        """
        return DOIDataset(list(self.result_dois))

    def get_RISDataset(self):
        """
        Returns search results as an RISDataset object. Uses the Crossref REST
        API for content negotation.

        Returns:
            RISDataset
        """
        RIS_dicts = []

        if GlobalConfig.streamlit:
            result_dois = stqdm(self.result_dois, desc="Converting results to RIS format.")
        else:
            result_dois = tqdm(self.result_dois, desc="Converting results to RIS format.")

        for doi in result_dois:
            # Use Crossref for content negotation
            ris_ref = crossref_negotiate_ris(doi)[0]

            # Add to list
            RIS_dicts.append(ris_ref)

        return RISDataset(RIS_dicts)


class COCIBackwardReferenceSearch:
    """
    Retrieves the (DOIs of) all articles in the references of a list of (DOIs of) articles
    by using the COCI REST API.
    """
    def __init__(self, search_dois: list):
        self.search_dois = search_dois
        self.result_dois = set()  # prevent duplicates

    # Alternate constructor
    @classmethod
    def from_DOIDataset(cls, search_dataset: DOIDataset):
        """
        Constructs a search object from a DOIDataset.

        Args:
            search_dataset (DOIDataset): Dataset of DOIs to fetch references of.

        Returns:
            COCIBackwardReferenceSearch
        """
        return cls(search_dataset._items)

    # Properties
    def __len__(self):
        return (len(self.result_dois))

    @classmethod
    def _fetch_all_reference_dois(cls, doi: str):
        """
        Fetches all references of DOI from COCI.

        Args:
            doi (str): DOI to fetch references of.

        Returns:
            reference_dois (list): List of DOIs
        """
        components = OrderedDict([("references", doi)])
        query = COCIQuery(components)

        query()

        references = query.response.json()

        reference_dois = []

        for dict in references:
            ref_doi = dict["cited"]
            reference_dois.append(ref_doi)

        return reference_dois

    # Perform search
    def __call__(self):
        if GlobalConfig.streamlit:
            iterable = stqdm(self.search_dois)
        else:
            iterable = tqdm(self.search_dois)

        for doi in iterable:
            # Fetch & update results
            doi_list = self._fetch_all_reference_dois(doi)
            self.result_dois.update(doi_list)

    def get_DOIDataset(self):
        """
        Returns search results as a DOIDataset object.

        Returns:
            DOIDataset
        """
        return DOIDataset(list(self.result_dois))

    def get_RISDataset(self):
        """
        Returns search results as an RISDataset object. Uses the Crossref REST
        API for content negotation.

        Returns:
            RISDataset
        """
        RIS_dicts = []

        if GlobalConfig.streamlit:
            result_dois = stqdm(self.result_dois, desc="Converting results to RIS format.")
        else:
            result_dois = tqdm(self.result_dois, desc="Converting results to RIS format.")

        for doi in result_dois:
            # Use Crossref for content negotation
            ris_ref = crossref_negotiate_ris(doi)[0]

            # Add to list
            RIS_dicts.append(ris_ref)

        return RISDataset(RIS_dicts)


class COCIForwardCitationSearch:
    """
    Retrieves the (DOIs of) all articles citing a list of (DOIs of) articles
    by using the COCI REST API.
    """
    def __init__(self, search_dois: list):
        self.search_dois = search_dois
        self.result_dois = set()  # prevent duplicates

    # Alternate constructor
    @classmethod
    def from_DOIDataset(cls, search_dataset: DOIDataset):
        """
        Constructs a search object from a DOIDataset.

        Args:
            search_dataset (DOIDataset): Dataset of DOIs to fetch references of.

        Returns:
            COCIForwardReferenceSearch
        """
        return cls(search_dataset._items)

    # Properties
    def __len__(self):
        return (len(self.result_dois))

    @classmethod
    def _fetch_all_citation_dois(cls, doi: str):
        """
        Fetches all citations of DOI from COCI.

        Args:
            doi (str): DOI to fetch citations of.

        Returns:
            citation_dois (list): List of DOIs
        """
        components = OrderedDict([("citations", doi)])
        query = COCIQuery(components)
        query()

        references = query.response.json()

        citation_dois = []

        for dict in references:
            cit_doi = dict["citing"]
            citation_dois.append(cit_doi)

        return citation_dois

    # Perform search
    def __call__(self):
        if GlobalConfig.streamlit:
            iterable = stqdm(self.search_dois)
        else:
            iterable = tqdm(self.search_dois)

        for doi in iterable:
            # Fetch & update results
            doi_list = self._fetch_all_citation_dois(doi)
            self.result_dois.update(doi_list)

    def get_DOIDataset(self):
        """
        Returns search results as a DOIDataset object.

        Returns:
            DOIDataset
        """
        return DOIDataset(list(self.result_dois))

    def get_RISDataset(self):
        """
        Returns search results as an RISDataset object. Uses the Crossref REST
        API for content negotation.

        Returns:
            RISDataset
        """
        RIS_dicts = []

        if GlobalConfig.streamlit:
            result_dois = stqdm(self.result_dois, desc="Converting results to RIS format.")
        else:
            result_dois = tqdm(self.result_dois, desc="Converting results to RIS format.")

        for doi in result_dois:
            # Use Crossref for content negotation
            ris_ref = crossref_negotiate_ris(doi)[0]

            # Add to list
            RIS_dicts.append(ris_ref)

        return RISDataset(RIS_dicts)
