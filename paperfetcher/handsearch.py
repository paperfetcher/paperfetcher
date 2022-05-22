# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Classes to fetch all journal works (articles) matching a set of keywords and
within a given date range by querying various APIs.
"""

from collections import OrderedDict
import logging
import warnings

from tqdm import tqdm
from stqdm import stqdm

from paperfetcher import GlobalConfig
from paperfetcher.apiclients import CrossrefQuery
from paperfetcher.content_negotiators import crossref_negotiate_ris
from paperfetcher.datastructures import DOIDataset, CitationsDataset, RISDataset
from paperfetcher.exceptions import SearchError

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(GlobalConfig.loglevel)


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

    Note:
        Performing a search with no keywords and select=False can be very time- and memory- intensive.
        The search object will complain when such a search is performed.

    Args:
        ISSN (str): Journal (web) ISSN.
        type (str): Type of works to fetch (default="journal-article").
        keyword_list (list): List of keywords (str) to query with (default=None).
        from_date (str): Fetch articles published from (and after) this date (format="YYYY-MM-DD", default=None).
        until_date (str): Fetch articles published until this date (format="YYYY-MM-DD", default=None).
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

        Raises:
            SearchError if ISSN does not exist, or if unable to decode JSON response.
        """
        # Retrive summary of results only
        query_params['rows'] = 0

        if cls._check_issn_exists(issn):
            components = OrderedDict([("journals", str(issn)),
                                      ("works", None)])
            query = CrossrefQuery(components,
                                  query_params=query_params)
            query()

            try:
                data = query.response.json()
                return data['message']['total-results']

            except Exception:
                raise SearchError("Cannot decode results for the ISSN %s" % issn)
        else:
            raise SearchError("ISSN %s is not indexed in Crossref." % issn)

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

        Raises:
            SearchError if ISSN does not exist, or if unable to decode JSON response.
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

            try:
                data = query.response.json()
                return data['message']

            except Exception:
                raise SearchError("Cannot decode results for offset %d of the ISSN %s" % (offset, issn))
        else:
            raise SearchError("ISSN %s is not indexed in Crossref." % issn)

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

        Raises:
            SearchError if field parser is missing.
        """
        output_item = []
        for fidx in range(len(field_list)):
            field = field_list[fidx]

            try:
                field_parser = field_parsers_list[fidx]

            except IndexError:
                raise SearchError("No field parser corresponding to field %s was provided." % field)

            try:
                extracted_field = json_item[field]
                if field_parser is not None:
                    output_item.append(field_parser(extracted_field))
                else:
                    output_item.append(extracted_field)

            except KeyError:
                output_item.append("")

        return output_item

    def dry_run(self, select=False, select_fields=[]):
        """
        How many works will this search fetch?
        """
        query_params = OrderedDict()
        if self.keyword_list is None:
            if not select:
                warnings.warn("Search with no keywords and no select can be slow and memory intensive. Consider setting select=True and using select_fields to fetch only a subset of fields.")
        elif len(self.keyword_list) == 0:
            if not select:
                warnings.warn("Search with no keywords and no select can be slow and memory intensive. Consider setting select=True and using select_fields to fetch only a subset of fields.")
        else:
            query_params['query'] = "+".join(self.keyword_list)

        if self.from_date is not None and self.until_date is not None:
            query_params['filter'] = "from-pub-date:{},until-pub-date:{}".format(
                                     self.from_date, self.until_date)
        elif self.from_date is not None:
            query_params['filter'] = "from-pub-date:{}".format(
                                     self.from_date)
        elif self.until_date is not None:
            query_params['filter'] = "until-pub-date:{}".format(
                                     self.until_date)

        query_params['facet'] = "type-name:{}".format(self.type)
        query_params['sort'] = "published"
        query_params['order'] = self.sort_order

        if(select):
            if(len(select_fields) == 0):
                raise SearchError("select_fields cannot be empty when select is True.")
            query_params['select'] = ",".join(select_fields)

        total_items = self._fetch_count(self.ISSN, query_params)

        return total_items

    def __call__(self, display_progress_bar=True, select=False, select_fields=[]):
        query_params = OrderedDict()
        if self.keyword_list is None:
            if not select:
                warnings.warn("Search with no keywords and no select can be slow and memory intensive. Consider setting select=True and using select_fields to fetch only a subset of fields.")
        elif len(self.keyword_list) == 0:
            if not select:
                warnings.warn("Search with no keywords and no select can be slow and memory intensive. Consider setting select=True and using select_fields to fetch only a subset of fields.")
        else:
            query_params['query'] = "+".join(self.keyword_list)

        if self.from_date is not None and self.until_date is not None:
            query_params['filter'] = "from-pub-date:{},until-pub-date:{}".format(
                                     self.from_date, self.until_date)
        elif self.from_date is not None:
            query_params['filter'] = "from-pub-date:{}".format(
                                     self.from_date)
        elif self.until_date is not None:
            query_params['filter'] = "until-pub-date:{}".format(
                                     self.until_date)

        query_params['facet'] = "type-name:{}".format(self.type)
        query_params['sort'] = "published"
        query_params['order'] = self.sort_order

        if(select):
            if(len(select_fields) == 0):
                raise SearchError("select_fields cannot be empty when select is True.")
            query_params['select'] = ",".join(select_fields)

        total_items = self._fetch_count(self.ISSN, query_params)
        logger.info("Fetching {} works.".format(total_items))

        offsets = range(total_items)[::self.batch_size]

        if display_progress_bar:
            if GlobalConfig.streamlit:
                offsets = stqdm(offsets, desc="Fetching {} batches of {} articles".format(len(offsets), self.batch_size))
            else:
                offsets = tqdm(offsets, desc="Fetching {} batches of {} articles".format(len(offsets), self.batch_size))
        else:
            logger.info("Fetching {} batches of {} articles.".format(len(offsets), self.batch_size))

        for offset in offsets:
            try:
                batch = self._fetch_batch(self.ISSN, query_params, self.batch_size,
                                          offset)
                self.results += (batch['items'])

            except (SearchError, Exception):
                # Do not fail in the middle of a search
                warnings.warn("Error in fetching batch of items from %d - %d. Omitting these items from search results." % (offset, offset + self.batch_size))

    def get_DOIDataset(self):
        """
        Extracts DOIs from search results and returns them as a DOIDataset object.

        Returns:
            DOIDataset
        """
        DOIlist = []
        for work in self.results:
            try:
                DOIlist.append(work['DOI'])
            except Exception:
                warnings.warn("Work {} did not contain a DOI. Omitting from search results.".format(str(work)))
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
            try:
                fields = self._extract_fields(work, field_list, field_parsers_list)
                Citationlist.append(fields)
            except Exception:
                warnings.warn("Could not extract data from work {}. Omitting from search results.".format(str(work)))
        logger.debug(Citationlist)
        return CitationsDataset(field_list, Citationlist)

    def get_RISDataset(self, extra_field_list=[], extra_field_parser_list=[], extra_field_rispy_tags=[]):
        """
        Extracts DOIs from search results and fetches RIS data for each DOI using
        Crossref's content negotiation service.

        Extra fields in the search results that are not automatically populated
        by Crossref's content negotation service can be mapped to the RIS format (through rispy's mapping)
        using the `extra_fields`, `extra_field_parser_list`, and `extra_field_rispy_tags`
        arguments.

        Args:
            extra_field_list (list): List of extra fields to parse and include in RIS file (see Crossref REST API doc for permissible field name values).
            extra_field_parser_list (list): List of field parser functions corresponding to each extra field name. A `None` value means that no parser
                is needed for that field.
            extra_field_rispy_tags (list): List of rispy tags for each extra field.
        """
        RIS_dicts = []

        if GlobalConfig.streamlit:
            results = stqdm(self.results, desc="Converting results to RIS format.")
        else:
            results = tqdm(self.results, desc="Converting results to RIS format.")

        for work in results:
            try:
                # Extract DOI and extra fields
                doi_plus = self._extract_fields(work, ['DOI'] + extra_field_list, [None] + extra_field_parser_list)
                ris_ref = crossref_negotiate_ris(doi_plus[0])[0]

            except Exception:
                try:
                    doi = work['DOI']
                    ris_ref = {'type_of_reference': 'JOUR', 'doi': doi}
                    warnings.warn("Failed to get RIS metadata for DOI %s. Appending just the DOI to the RIS dataset." % doi)

                except Exception:
                    warnings.warn("Failed to get DOI from work {}. Skipping.".format(str(work)))
                    continue

            # Add in extra fields
            for fieldidx, field in enumerate(extra_field_list):
                tag = extra_field_rispy_tags[fieldidx]
                ris_ref[tag] = doi_plus[1 + fieldidx]

            # Add to list
            RIS_dicts.append(ris_ref)

        return RISDataset(RIS_dicts)
