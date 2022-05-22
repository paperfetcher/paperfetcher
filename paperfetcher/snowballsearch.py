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
from paperfetcher.exceptions import SearchError, ContentNegotiationError, RISParsingError

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(GlobalConfig.loglevel)


class CrossrefBackwardReferenceSearch:
    """
    Retrieves (the DOIs of) all articles in the references of a list of (DOIs of) articles
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
        return query.response.status_code == 200  # OK?

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

        try:
            data = query.response.json()
            doi_dicts = data['message'].get('reference', None)
            if doi_dicts is None:
                return False
            if len(doi_dicts) == 0:
                return False
            return True

        except Exception:
            warnings.warn("Cannot decode results for the DOI %s" % doi)
            return False  # Cannot decode => has no references

    @classmethod
    def _fetch_all_reference_dois(cls, doi: str):
        """
        Fetches all references of DOI from Crossref.

        Args:
            doi (str): DOI to fetch references of.

        Returns:
            reference_dois (list): List of DOIs

        Raises:
            SearchError if unable to convert query response to JSON format and extract reference data from it.
        """
        components = OrderedDict([("works", doi)])
        query = CrossrefQuery(components)
        query()

        try:
            data = query.response.json()
            doi_dicts = data['message']['reference']

        except Exception:
            raise SearchError("Cannot decode results for the DOI %s" % doi)

        reference_dois = []
        for dict in doi_dicts:
            ref_doi = dict.get("DOI", None)
            if ref_doi is not None:
                reference_dois.append(ref_doi)
            else:
                warnings.warn("In references of %s, reference object %s does not have a DOI field. Skipping this reference." % (doi, dict))  # warn but continue

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
                warnings.warn("DOI %s not indexed in Crossref. Skipping this DOI." % doi)  # warn but continue
                continue  # move on to the next DOI

            if not self._check_doi_has_references(doi):
                warnings.warn("DOI %s does not have reference metadata in Crossref. Skipping this DOI." % doi)  # warn but continue
                continue  # move on to the next DOI

            # Fetch & update results
            try:
                doi_list = self._fetch_all_reference_dois(doi)
                self.result_dois.update(doi_list)

            except SearchError:
                warnings.warn("Error in retrieving reference metadata for DOI %s. Skipping this DOI." % doi)

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
            try:
                # Use Crossref for content negotation
                ris_ref = crossref_negotiate_ris(doi)[0]

            except (ContentNegotiationError, RISParsingError):
                warnings.warn("Failed to get RIS metadata for DOI %s. Appending just the DOI to the RIS dataset." % doi)
                ris_ref = {'type_of_reference': 'JOUR', 'doi': doi}

            # Add to list
            RIS_dicts.append(ris_ref)

        return RISDataset(RIS_dicts)


class COCIBackwardReferenceSearch:
    """
    Retrieves the (DOIs of) all articles in the references of a list of (DOIs of) articles
    by using the COCI REST API.

    Args:
        search_dois (list): List of DOIs (str) to fetch references of.

    Attributes:
        search_dois (list): List of DOIs (str) to fetch references of.
        result_dois (set): Set of DOIs which are referenced by the DOIs in `search_dois`.

    Example:
        >>> search = snowballsearch.COCIBackwardReferenceSearch(["10.1021/acs.jpcb.1c02191", "10.1073/pnas.2018234118"])
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
            COCIBackwardReferenceSearch
        """
        return cls(search_dataset._items)

    # Properties
    def __len__(self):
        return (len(self.result_dois))

    @classmethod
    def _check_doi_exists(cls, doi: str):
        """
        Checks if DOI is indexed in COCI.

        Args:
            doi (str): DOI to check.

        Returns:
            bool
        """
        components = OrderedDict([("references", doi)])
        query = COCIQuery(components)
        query()
        return query.response.status_code == 200

    @classmethod
    def _fetch_all_reference_dois(cls, doi: str):
        """
        Fetches all references of DOI from COCI.

        Args:
            doi (str): DOI to fetch references of.

        Returns:
            reference_dois (list): List of DOIs

        Raises:
            SearchError if unable to convert query response to JSON format and extract reference data from it.
        """
        components = OrderedDict([("references", doi)])
        query = COCIQuery(components)

        query()

        try:
            references = query.response.json()

            reference_dois = []

            for dict in references:
                ref_doi = dict["cited"]
                reference_dois.append(ref_doi)

            return reference_dois

        except Exception:
            raise SearchError("Cannot decode results for the DOI %s" % doi)

    # Perform search
    def __call__(self):
        if GlobalConfig.streamlit:
            iterable = stqdm(self.search_dois)
        else:
            iterable = tqdm(self.search_dois)

        for doi in iterable:
            # Checks
            if not self._check_doi_exists(doi):
                warnings.warn("DOI %s not found in COCI. Skipping this DOI." % doi)  # warn but continue
                continue

            try:
                # Fetch & update results
                doi_list = self._fetch_all_reference_dois(doi)
                self.result_dois.update(doi_list)

            except SearchError:
                warnings.warn("Error in retrieving reference metadata for DOI %s. Skipping this DOI." % doi)

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
            try:
                # Use Crossref for content negotation
                ris_ref = crossref_negotiate_ris(doi)[0]

            except (ContentNegotiationError, RISParsingError):
                warnings.warn("Failed to get RIS metadata for DOI %s. Appending just the DOI to the RIS dataset." % doi)
                ris_ref = {'type_of_reference': 'JOUR', 'doi': doi}

            # Add to list
            RIS_dicts.append(ris_ref)

        return RISDataset(RIS_dicts)


class COCIForwardCitationSearch:
    """
    Retrieves the (DOIs of) all articles citing a list of (DOIs of) articles
    by using the COCI REST API.

    Args:
        search_dois (list): List of DOIs (str) to fetch citations of.

    Attributes:
        search_dois (list): List of DOIs (str) to fetch citations of.
        result_dois (set): Set of DOIs which cite the DOIs in `search_dois`.

    Example:
        >>> search = snowballsearch.COCIForwardCitationSearch(["10.1021/acs.jpcb.8b11423", "10.1073/pnas.2018234118"])
        >>> search()
        >>> len(search)
        11
        >>> search.result_dois
        {'10.1039/c9sc02097g', '10.1021/acs.jpcb.1c05748', ... , '10.1021/acs.jpclett.9b02052'}
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
    def _check_doi_exists(cls, doi: str):
        """
        Checks if DOI is indexed in COCI.

        Args:
            doi (str): DOI to check.

        Returns:
            bool
        """
        components = OrderedDict([("citations", doi)])
        query = COCIQuery(components)
        query()
        return query.response.status_code == 200

    @classmethod
    def _fetch_all_citation_dois(cls, doi: str):
        """
        Fetches all citations of DOI from COCI.

        Args:
            doi (str): DOI to fetch citations of.

        Returns:
            citation_dois (list): List of DOIs

        Raises:
            SearchError if unable to convert query response to JSON format and extract citation data from it.
        """
        components = OrderedDict([("citations", doi)])
        query = COCIQuery(components)
        query()

        try:
            references = query.response.json()

            citation_dois = []

            for dict in references:
                cit_doi = dict["citing"]
                citation_dois.append(cit_doi)

            return citation_dois

        except Exception:
            raise SearchError("Cannot decode results for the DOI %s" % doi)

    # Perform search
    def __call__(self):
        if GlobalConfig.streamlit:
            iterable = stqdm(self.search_dois)
        else:
            iterable = tqdm(self.search_dois)

        for doi in iterable:
            # Checks
            if not self._check_doi_exists(doi):
                warnings.warn("DOI %s not found in COCI. Skipping this DOI." % doi)  # warn but continue
                continue

            try:
                # Fetch & update results
                doi_list = self._fetch_all_citation_dois(doi)
                self.result_dois.update(doi_list)

            except SearchError:
                warnings.warn("Error in retrieving citation metadata for DOI %s. Skipping this DOI." % doi)

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
            try:
                # Use Crossref for content negotation
                ris_ref = crossref_negotiate_ris(doi)[0]

            except (ContentNegotiationError, RISParsingError):
                warnings.warn("Failed to get RIS metadata for DOI %s. Appending just the DOI to the RIS dataset." % doi)
                ris_ref = {'type_of_reference': 'JOUR', 'doi': doi}

            # Add to list
            RIS_dicts.append(ris_ref)

        return RISDataset(RIS_dicts)
