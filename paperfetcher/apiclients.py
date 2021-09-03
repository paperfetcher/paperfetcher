"""
Client implementations to communicate with various APIs.

@author Akash Pallath
This code is licensed under the MIT license (see LICENSE.txt for details).
"""
from collections import OrderedDict
import logging
import requests
import sys

from paperfetcher import _useragent, _crossref_plus, _crossref_plus_auth_token
from paperfetcher.exceptions import QueryError

# Logging
logger = logging.getLogger(__name__)


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
