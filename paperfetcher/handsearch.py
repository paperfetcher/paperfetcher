from collections import OrderedDict
from paperfetcher.exceptions import QueryError
from paperfetcher.datastructures import CrossrefQuery


class CrossrefSearch:
    def __init__(self):
        self.ISSN_list = []
        self.keyword_list = []

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
        raise NotImplementedError()

    ############################################################################
    # Perform search
    ############################################################################
    def __call__(self):
        pass
