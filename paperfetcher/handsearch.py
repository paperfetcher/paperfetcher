"""
Module documentation goes here.
"""

from collections import OrderedDict
from paperfetcher.exceptions import QueryError
from paperfetcher.datastructures import CrossrefQuery, DOIDataset, CitationsDataset
from tqdm import tqdm
import pickle

# Logging
import logging
logger = logging.getLogger(__name__)


class CrossrefSearch:
    """
    Retrieves all articles from a journal, given its ISSN, which match
    a set of keywords and are within a date range.
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

    ############################################################################
    # Properties
    ############################################################################
    def __len__(self):
        return len(self.results)

    ############################################################################
    # Search workers (class methods)
    ############################################################################
    @classmethod
    def _check_issn_exists(self, issn: str):
        """Checks if ISSN exists in Crossref.

        Args:
            issn: ISSN of journal
        Returns:
            bool
        """
        components = OrderedDict([("journals", str(issn))])
        query = CrossrefQuery(components)
        query()
        return query.response.status_code == 200

    @classmethod
    def _fetch_count(self, issn: str, query_params=OrderedDict()):
        """Fetches number of works in journal that match criteria.

        Args:
            issn: ISSN of journal to check
            query_params: Parameters for query
        Returns:
            int
        """
        # Retrive summary of results only
        query_params['rows'] = 0

        if self._check_issn_exists(issn):
            components = OrderedDict([("journals", str(issn)),
                                      ("works", None)])
            query = CrossrefQuery(components,
                                  query_params=query_params)
            query()
            data = query.response.json()
            return data['message']['total-results']
        else:
            raise QueryError("ISSN does not exist.")

    @classmethod
    def _fetch_batch(self, issn: str, query_params=OrderedDict(), size=20,
                     offset=0):
        """Fetches a batch of works.

        Args:
            issn: ISSN of journal to check
            query_params: Parameters for query
            size: Batch size (default=20)
            offset: Offset to fetch results from (default=0)
        Returns:
            data (dict): JSON response as Python dictionary.
        """
        # Set rows and offset
        query_params['rows'] = size
        query_params['offset'] = offset

        if self._check_issn_exists(issn):
            components = OrderedDict([("journals", str(issn)),
                                      ("works", None)])
            query = CrossrefQuery(components,
                                  query_params=query_params)
            query()
            data = query.response.json()
            return data['message']
        else:
            raise QueryError("ISSN does not exist.")

    @classmethod
    def _extract_fields(self, json_item, field_list, field_parsers_list):
        """Extracts data corresponding to given list of fields from the JSON
        response returned by the Crossref API.

        Args:
            json_item (dict): Item dictionary extracted from JSON response object.
            field_list (list): List of field names.
            field_parsers_list (list): List of field parser functions to parse field values.
                If field parser is None, the output string will be appended as is.
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

    ############################################################################
    # Perform search
    #
    # If select is False, a full (memory and time intensive) search is performed,
    # fetching all metadata associated with each journal work.
    # If select is True, a subset of fields to fetch can be specified using the
    # select_fields parameters.
    ############################################################################
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

    ############################################################################
    # Save and load state of search (query & results) to file.
    ############################################################################
    def save(self, file):
        with open(file, "wb") as f:
            pickle.dump(self.__dict__, f)

    def load(self, file):
        self.__dict__.clear()
        with open(file, "rb") as f:
            self.__dict__.update(pickle.load(f))

    ############################################################################
    # Transform raw search results into datasets
    ############################################################################
    def get_DOIDataset(self):
        DOIlist = []
        for work in self.results:
            DOIlist.append(work['DOI'])
        logger.debug(DOIlist)
        return DOIDataset(DOIlist)

    def get_CitationsDataset(self, field_list=[], field_parsers_list=[]):
        Citationlist = []
        for work in self.results:
            Citationlist.append(self._extract_fields(work, field_list, field_parsers_list))
        logger.debug(Citationlist)
        return CitationsDataset(field_list, Citationlist)
