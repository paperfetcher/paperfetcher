# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Client implementations to communicate with various APIs.
"""
from collections import OrderedDict
import logging
import requests
import sys

from paperfetcher import GlobalConfig
from paperfetcher.exceptions import QueryError

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(GlobalConfig.loglevel)


class Query:
    """
    Base class for structuring and executing HTTP GET queries.

    Args:
        base_url (str): Base URL for query (such as api.xyz.com/get).
        query_params (dict): Dictionary of query parameters.
        headers (dict): Dictionary of HTTP headers to pass along with the query.

    Attributes:
        query_base (str): Base URL for query (such as api.xyz.com/get).
        query_params (dict): Dictionary of query parameters.
        headers (dict): Dictionary of HTTP headers.
        response (requests.Response): Response recieved on executing GET query.

    Examples:
        A simple Query to the Github REST API:

        >>> query = Query("https://api.github.com")
        >>> query()
        >>> query.response
        <Response [200]>

        A Query to the Github REST API to fetch a list of all public repositories in the paperfetcher organization:

        >>> query = Query("https://api.github.com/orgs/paperfetcher/repos",
        ...               query_params={"type": "public"},
        ...               headers={"Accept": "application/vnd.github.v3+json"})
        >>> query()
        >>> query.response
        <Response [200]>
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
    """
    Class for structuring and executing Crossref REST API queries.

    Query components can be added to the base URL by passing an ordered dictionary to the components argument.
    For example, the components dictionary `{"comp1-key": "comp1-value", "comp2": None}` changes
    the query URL to `https://api.crossref.org/comp1-key/comp1-value/comp2/`.

    Args:
        components (collections.OrderedDict): Components to append to the base URL.
        query_params (collections.OrderedDict): Ordered dictionary of query parameters.

    Attributes:
        components (collections.OrderedDict): Components to append to the base URL.
        query_base (str): Base URL for query (https://api.crossref.org/...).
        query_params (collections.OrderedDict): Dictionary of query parameters.
        headers (dict): Dictionary of HTTP headers.
        response (requests.Response): Response recieved on executing GET query to the Crossref API.

    Examples:
        Querying the metadata of a paper with a known DOI:

        >>> query = CrossrefQuery(components={"works": "10.1021/acs.jpcb.1c02191"})
        >>> query()
        >>> query.response
        <Response [200]>
        >>> query.response.json()
        {'status': 'ok', 'message-type': 'work', 'message-version': '1.0.0',
        'message': {...}}

        Query to fetch all articles from a journal with a known ISSN:

        >>> components = OrderedDict([("journals", "1520-5126"),
                                  ("works", None)])
        >>> query = CrossrefQuery(components)
        >>> query()
        >>> query.response
        <Response [200]>
        >>> query.response.json()
        {'status': 'ok', 'message-type': 'work', 'message-version': '1.0.0',
        'message': {...}}
    """

    # Which version of the Crossref API to use.
    __API_VERSION = 1

    def __init__(self, components=OrderedDict(), query_params=OrderedDict()):
        # Crossref API etiquette
        headers = {'User-Agent': GlobalConfig.crossref_useragent}

        # Option to use Crossref Plus
        if GlobalConfig.crossref_plus:
            headers["Crossref-Plus-API-Token"] = GlobalConfig.crossref_plus_auth_token

        super().__init__("https://api.crossref.org/v{}/".format(self.__API_VERSION),
                         query_params=query_params,
                         headers=headers)

        # Specific to Crossref API call structure
        self.components = components

        # The order in which components and query params are added is preserved (this is important!).
        # Both components and query params will be unpacked only at call time.

    def __call__(self):
        # Unpack components
        for k, v in self.components.items():
            if v is not None:
                self.query_base += "%s/%s/" % (k, v)
            else:
                self.query_base += "%s/" % k

        # Call
        super().__call__()


class COCIQuery(Query):
    """
    Class for structuring and executing COCI REST API queries.

    Args:
        components (collections.OrderedDict): Components to append to the base URL.
        query_params (collections.OrderedDict): Ordered dictionary of query parameters.

    Attributes:
        components (collections.OrderedDict): Components to append to the base URL.
        query_base (str): Base URL for query (https://opencitations.net/index/coci/api/v{}/...).
        query_params (collections.OrderedDict): Dictionary of query parameters.
        headers (dict): Dictionary of HTTP headers.
        response (requests.Response): Response recieved on executing GET query to the COCI API.

    Examples:
        Querying the references of a paper with a known DOI:

        >>> query = COCIQuery(components=OrderedDict([("references", "10.1021/acs.jpcb.1c02191")]))
        >>> query()
        >>> query.response
        <Response [200]>
        >>> query.response.json()
        [{'oci': '020010002013610122837192512113701120002010901-0200100000236191212370201090809', 'creation': '2021-05-12', 'timespan': 'P9Y5M19D',
        ...}]

        Querying the citations of a paper with a known DOI:

        >>> query = COCIQuery(components=OrderedDict([("citations", "10.1021/acs.jpcb.1c02191")]))
        >>> query()
        >>> query.response
        <Response [200]>
        >>> query.response.json()
        [{'oci': '0200100000236252421370200020100050206-020010002013610122837192512113701120002010901', 'creation': '2021-10-02', 'timespan': 'P4M20D',
         'journal_sc': 'no', 'author_sc': 'no', 'citing': '10.1002/pol.20210526', 'cited': '10.1021/acs.jpcb.1c02191'}]
    """

    # Which version of the COCI  API to use.
    __API_VERSION = 1

    def __init__(self, components=OrderedDict(), query_params=OrderedDict()):
        super().__init__("https://opencitations.net/index/coci/api/v{}/".format(self.__API_VERSION),
                         query_params=query_params,
                         headers={})

        # Specific to COCI API call structure
        self.components = components

        # The order in which components and query params are added is preserved (this is important!).
        # Both components and query params will be unpacked only at call time.

    def __call__(self):
        # Unpack components
        for k, v in self.components.items():
            if v is not None:
                self.query_base += "%s/%s/" % (k, v)
            else:
                self.query_base += "%s/" % k

        # COCI-specific error handling
        if self.query_base[-1] == "/":
            self.query_base = self.query_base[:-1]

        # Call
        super().__call__()
