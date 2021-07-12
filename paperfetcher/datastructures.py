"""Custom data structures (classes) for paperfetcher"""
from collections import OrderedDict
from paperfetcher import _useragent, _crossref_plus, _crossref_plus_auth_token
from paperfetcher.exceptions import QueryError
import requests
import sys

################################################################################
# Structures for storing query information, executing queries, and
# storing raw query results.
################################################################################


class Query:
    """
    Base class for queries.

    Parameters:
        query_base: Base URL for query (such as api.xyz.com/get)
        query_params: Dictionary of query parameters
    """
    def __init__(self, base_url=None, query_params: dict = {}, headers: str = {}):
        self.query_base = base_url
        self.query_params = query_params
        self.headers = headers
        # Output
        self.__response = None

    @property
    def response(self):
        if self.__response is not None:
            return self.__response
        else:
            raise RuntimeError("Need to run Query first before accessing its response.")

    def __call__(self):
        """Runs query and stores response."""
        try:
            self.__response = requests.get(self.query_base, params=self.query_params, headers=self.headers)

        except requests.exceptions.ConnectionError as e:
            raise QueryError("Unable to run query, could not reach server:" + str(e)).with_traceback(sys.exc_info()[2])

        except requests.exceptions.Timeout as e:
            raise QueryError("Unable to run query, request timed out:" + str(e)).with_traceback(sys.exc_info()[2])

        except requests.exceptions.HTTPError as e:
            raise QueryError("Unable to run query, HTTP error:" + str(e)).with_traceback(sys.exc_info()[2])

        except requests.exceptions.RequestException as e:
            raise QueryError("Unable to run query, exception:" + str(e)).with_traceback(sys.exc_info()[2])


class CrossrefQuery(Query):
    """Class for Crossref queries"""

    # Which version of the Crossref API to use.
    __API_VERSION = 3

    def __init__(self, components=OrderedDict(), query_params=OrderedDict()):
        # Crossref API etiquette
        headers = {'User-Agent': _useragent}

        # Option to use Crossref Plus
        if _crossref_plus:
            headers["Crossref-Plus-API-Token"] = _crossref_plus_auth_token

        super().__init__("https://api.crossref.org/",
                         query_params=query_params,
                         headers=headers)

        # Components can be added later too.
        # The order in which components are added is preserved (this is important!).
        # All the components will be unpacked only at call time.
        self.components = components

    def __call__(self):
        # Unpack components
        for k, v in self.components.items():
            if v is not None:
                self.query_base += "%s/%s/" % (k, v)
            else:
                self.query_base += "%s/" % k

        # Call
        super().__call__()


################################################################################
# Structures for storing citation datasets.
################################################################################


class CitationDataset:
    """Abstract class for citation datasets."""
    def __init__(self, items: list):
        self.items = list(items)

    # Basic functionality for all child classes to implement.

    def to_df(self, file):
        """Converts dataset to DataFrame."""
        pass

    def save_txt(self, file):
        """Saves dataset to .txt file."""
        pass

    def save_csv(self, file):
        """Saves dataset to .csv file."""
        pass

    def save_xls(self, file):
        """Saves dataset to Excel file."""
        pass


class DOIDataset(CitationDataset):
    def __init__(self, items: list):
        super().__init__()

    def save_RIS(self, file):
        """Saves dataset in RIS format to file."""
        pass


class BibDataset(CitationDataset):
    def __init__(self, items: list):
        super().__init__()

    def save_RIS(self, file):
        """Saves dataset in RIS format to file."""
        pass


class CustomDataset(CitationDataset):
    def __init__(self, items: list):
        super().__init__()
