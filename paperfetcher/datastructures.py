"""
Custom data structures (classes) for paperfetcher.
"""

from collections import OrderedDict
from paperfetcher import _useragent, _crossref_plus, _crossref_plus_auth_token
from paperfetcher.exceptions import QueryError, DatasetError
import requests
import sys

# Logging
import logging
logger = logging.getLogger(__name__)

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

    def _log_request(self, response, *args, **kwargs):
        logger.debug("\n-----Request-----\nMethod: {}\nURL: {}\nBody: {}\nHeaders: {}\n-----------------\n".
                     format(response.request.method,
                            response.request.url,
                            response.request.body,
                            response.request.headers))

    def __call__(self):
        """Runs query and stores response."""
        try:
            self.__response = requests.get(self.query_base, params=self.query_params,
                                           headers=self.headers, hooks={'response': self._log_request})

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
# Structures for storing results.
################################################################################


class Dataset:
    """Abstract class for datasets."""
    def __init__(self, items: list = []):
        self._items = list(items)

    def __len__(self):
        return len(self._items)

    def append(self, item):
        self._items.append(item)

    # Basic functionality.

    def to_df(self, file):
        """Converts dataset to DataFrame."""
        # Child class must implement this.
        pass

    def save_txt(self, file):
        """Saves dataset to .txt file."""
        # Child class must implement this.
        pass

    def save_csv(self, file):
        """Saves dataset to .csv file."""
        # Child class must implement this.
        pass

    def save_xls(self, file):
        """Saves dataset to Excel file."""
        # Child class must implement this.
        pass


class DOIDataset(Dataset):
    # Internal representation: list of DOIs
    def __init__(self, items: list):
        super().__init__(items)

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

    def save_RIS(self, file):
        """Saves dataset to RIS file."""
        pass


class CitationsDataset(Dataset):
    # Internal representation: list of fields
    def __init__(self, num_fields: int, items: list = []):
        super().__init__(items)
        self.num_fields = num_fields
        for itemidx, item in enumerate(self._items):
            if len(item) != self.num_fields:
                raise DatasetError("Item at index %d is of incorrect length." % itemidx)

    def append(self, item):
        if len(item) != self.num_fields:
            raise DatasetError("Item is of incorrect length.")
        super().append(item)
