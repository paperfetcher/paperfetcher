"""
Module documentation goes here.
"""

from collections import OrderedDict
from paperfetcher.exceptions import QueryError
from paperfetcher.datastructures import CrossrefQuery
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
        self.result_batches = []

    ############################################################################
    # Search workers
    ############################################################################
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

    def _extract_fields(self, json_response, field_list, field_parsers_list):
        """Extracts data corresponding to given list of fields from the JSON
        response returned by the Crossref API.

        Args:
            json_response: JSON response.
            field_list (list): List of field names.
            field_parsers_list (list): List of field parser functions to parse field values.
                If field parser is None, the output string will be appended as is.
        """
        output_list = []
        for item in json_response['items']:
            output_item = []
            for fidx in range(len(field_list)):
                field = field_list[fidx]
                field_parser = field_parsers_list[fidx]
                try:
                    extracted_field = item[field]
                    if field_parser is not None:
                        output_item.append(field_parser(extracted_field))
                    else:
                        output_item.append(extracted_field)
                except KeyError:
                    output_item.append("")
            output_list.append(output_item)

        return output_list

    ############################################################################
    # Perform search
    ############################################################################
    def __call__(self, display_progress_bar=True):
        query_params = OrderedDict()
        query_params['query'] = "+".join(self.keyword_list)
        query_params['filter'] = "from-pub-date:{},until-pub-date:{}".format(
                                 self.from_date, self.until_date)
        query_params['facet'] = "type-name:{}".format(self.type)
        query_params['sort'] = "published"
        query_params['order'] = self.sort_order

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
            self.result_batches += batch

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
    # Transform raw search results into dataset
    ############################################################################

    def get_DOIDataset(self):
        pass

    def get_CitationDataset(self, field_list=[]):
        pass
