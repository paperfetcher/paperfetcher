# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Classes to fetch all journal works (articles) matching a set of keywords and within a given date range by querying various APIs.

Note:
    Only the Crossref REST API is supported for now. Support for other APIs will be added soon.
"""

from collections import OrderedDict
import pickle
import logging

from tqdm import tqdm

from paperfetcher.apiclients import CrossrefQuery
from paperfetcher.datastructures import DOIDataset, CitationsDataset
from paperfetcher.exceptions import SearchError

# Logging
logger = logging.getLogger(__name__)


class CrossrefSearch:
    """
    Retrieves all works from a journal, given its ISSN, which match
    a set of keywords and are within a date range.

    Calling a CrossrefSearch object performs the search. A search object can be
    called with the arguments `display_progress_bar` (True/False; default=True) to
    toggle the display of a search progress bar, `select` (True/False; default=False), and
    `select_fields` (list) to query only a subset of metadata for each journal
    article.
    If select is False, a full (memory and time intensive) search is performed,
    fetching all metadata associated with each journal work.
    If select is True, a subset of fields to fetch can be specified using the
    select_fields parameter. Check the Crossref REST API doc
    for details on which field names are permissible.

    Args:
        ISSN (str): Journal (web) ISSN.
        type (str): Type of works to fetch (default="journal-article").
        keyword_list (list): List of keywords (str) to query with.
        from_date (str): Fetch articles published from (and after) this date (format="YYYY-MM-DD").
        until_date (str): Fetch articles published until this date (format="YYYY-MM-DD").
        batch_size (int): Number of works to fetch in each batch (default=20).
        sort_order (str): Order in which to sort works by date ("asc" or "desc", default="desc").

    Attributes:
        ISSN (str): Journal (web) ISSN.
        type (str): Type of works to fetch (default="journal-article").
        keyword_list (list): List of keywords (str) to query with.
        from_date (str): Fetch articles published from (and after) this date (format="YYYY-MM-DD").
        until_date (str): Fetch articles published until this date (format="YYYY-MM-DD").
        batch_size (int): Number of works to fetch in each batch (default=20).
        sort_order (str): Order in which to sort works by date ("asc" or "desc", default="desc").
        results (list): List of dictionaries, each dictionary corresponds to a work.

    Examples:
        >>> search = CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01", until_date="2020-01-01")
        >>> search()
        >>> len(search)
        13
        >>> ds = search.get_DOIDataset()
        >>> ds.to_df()
                             DOI
        0   10.1021/jacs.9b09103
        1   10.1021/jacs.9b06862
        2   10.1021/jacs.9b09111
        3   10.1021/jacs.9b05874
        4   10.1021/jacs.9b02820
        5   10.1021/jacs.9b05136
        6   10.1021/jacs.9b02742
        7   10.1021/jacs.9b00577
        8   10.1021/jacs.8b11448
        9   10.1021/jacs.8b12877
        10  10.1021/jacs.8b11667
        11  10.1021/jacs.8b08298
        12  10.1021/jacs.7b11537
    """
    def __init__(self, ISSN="", type='journal-article', keyword_list=None, from_date=None,
                 until_date=None, batch_size=20, sort_order='desc'):
        self.ISSN = ISSN
        self.type = type
        self.keyword_list = keyword_list
        self.from_date = from_date
        self.until_date = until_date
        self.batch_size = batch_size
        self.sort_order = sort_order

        # Results
        self.results = []

    # Properties
    def __len__(self):
        return len(self.results)

    # Search workers (class methods)
    @classmethod
    def _check_issn_exists(cls, issn: str):
        """Checks if ISSN exists in Crossref.

        Args:
            issn (str): ISSN of journal

        Returns:
            bool
        """
        components = OrderedDict([("journals", str(issn))])
        query = CrossrefQuery(components)
        query()
        return query.response.status_code == 200

    @classmethod
    def _fetch_count(cls, issn: str, query_params=OrderedDict()):
        """Fetches number of works in journal that match criteria.

        Args:
            issn (str): ISSN of journal to check
            query_params (collections.OrderedDict): Parameters for query (default={})
        Returns:
            int
        """
        # Retrive summary of results only
        query_params['rows'] = 0

        if cls._check_issn_exists(issn):
            components = OrderedDict([("journals", str(issn)),
                                      ("works", None)])
            query = CrossrefQuery(components,
                                  query_params=query_params)
            query()
            data = query.response.json()
            return data['message']['total-results']
        else:
            raise SearchError("ISSN does not exist.")

    @classmethod
    def _fetch_batch(cls, issn: str, query_params=OrderedDict(), size=20,
                     offset=0):
        """Fetches a batch of works.

        Args:
            issn (str): ISSN of journal to check
            query_params (collections.OrderedDict): Parameters for query (default={})
            size (int): Batch size (default=20)
            offset (int): Offset to fetch results from (default=0)

        Returns:
            data (dict): JSON response as Python dictionary.
        """
        # Set rows and offset
        query_params['rows'] = size
        query_params['offset'] = offset

        if cls._check_issn_exists(issn):
            components = OrderedDict([("journals", str(issn)),
                                      ("works", None)])
            query = CrossrefQuery(components,
                                  query_params=query_params)
            query()
            data = query.response.json()
            return data['message']
        else:
            raise SearchError("ISSN does not exist.")

    @classmethod
    def _extract_fields(cls, json_item, field_list, field_parsers_list):
        """Extracts data corresponding to given list of fields from the JSON
        response returned by the Crossref API.

        Args:
            json_item (dict): Item dictionary extracted from JSON response object.
            field_list (list): List of field names.
            field_parsers_list (list): List of field parser functions to parse field values.
                If field parser is None, the output string will be appended as is.

        Returns:
            output_item (list): List of extracted field values.
        """
        output_item = []
        for fidx in range(len(field_list)):
            field = field_list[fidx]
            field_parser = field_parsers_list[fidx]
            try:
                extracted_field = json_item[field]
                if field_parser is not None:
                    output_item.append(field_parser(extracted_field))
                else:
                    output_item.append(extracted_field)
            except KeyError:
                output_item.append("")
        return output_item

    def __call__(self, display_progress_bar=True, select=False, select_fields=[]):
        query_params = OrderedDict()
        query_params['query'] = "+".join(self.keyword_list)
        query_params['filter'] = "from-pub-date:{},until-pub-date:{}".format(
                                 self.from_date, self.until_date)
        query_params['facet'] = "type-name:{}".format(self.type)
        query_params['sort'] = "published"
        query_params['order'] = self.sort_order

        if(select):
            query_params['select'] = ",".join(select_fields)

        total_items = self._fetch_count(self.ISSN, query_params)
        logger.info("Fetching {} works.".format(total_items, self.batch_size))

        offsets = range(total_items)[::self.batch_size]

        if display_progress_bar:
            offsets = tqdm(offsets)
        else:
            logger.info("Fetching {} batches of works.".format(len(offsets)))

        for offset in offsets:
            batch = self._fetch_batch(self.ISSN, query_params, self.batch_size,
                                      offset)
            self.results += (batch['items'])

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
        Extracts DOIs from search results and returns them as a DOIDataset object.

        Returns:
            DOIDataset
        """
        DOIlist = []
        for work in self.results:
            DOIlist.append(work['DOI'])
        logger.debug(DOIlist)
        return DOIDataset(DOIlist)

    def get_CitationsDataset(self, field_list=[], field_parsers_list=[]):
        """
        Parses a selection of fields from search results and returns them as a CitationsDataset object.

        Args:
            field_list (list): Names of fields to parse (see Crossref REST API doc for permissible field name values).
            field_parsers_list (list): List of field parser functions corresponding to each field name. A `None` value means that no parser
                is needed for that field.

        Returns:
            CitationsDataset

        Example:
            >>> search = handsearch.CrossrefSearch(ISSN="1520-5126", keyword_list=["hydration"], from_date="2018-01-01",
            ...                                    until_date="2020-01-01")
            >>> search(select=True, select_fields=['DOI', 'URL', 'title', 'author', 'issued'])
            >>> ds = search.get_CitationsDataset(field_list=['DOI', 'URL', 'title', 'author', 'issued'],
            ...                                  field_parsers_list=[None, None, parsers.crossref_title_parser,
            ...                                                      parsers.crossref_authors_parser, parsers.crossref_date_parser])
        """
        Citationlist = []
        for work in self.results:
            Citationlist.append(self._extract_fields(work, field_list, field_parsers_list))
        logger.debug(Citationlist)
        return CitationsDataset(field_list, Citationlist)
