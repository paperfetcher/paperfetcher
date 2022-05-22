# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Content negotiators to fetch citations in different formats.
"""
from collections import OrderedDict
import logging

import rispy

from paperfetcher.apiclients import CrossrefQuery
from paperfetcher.exceptions import ContentNegotiationError, RISParsingError

# Logging
logger = logging.getLogger(__name__)


def crossref_negotiate_ris(doi):
    """Fetches citation corresponding to a DOI in RIS format by using the
    Crossref REST API.

    Args:
        doi: DOI to fetch citation for.

    Returns:
        dict: rispy-read dictionary of RIS content returned by Crossref REST API.
    """
    # Build content negotation query
    components = OrderedDict([("works", doi),
                              ("transform", "application/x-research-info-systems")])
    query = CrossrefQuery(components)

    # Execute query
    query()

    if not (query.response.status_code == 200):
        raise ContentNegotiationError("Could not get RIS metadata for DOI %s" % doi)

    # rispy conversion
    try:
        ris_data = rispy.loads(query.response.text)
        return ris_data

    except Exception:
        raise RISParsingError("Could not parse RIS metadata returned by Crossref for DOI %s" % doi)
