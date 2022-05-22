# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.handsearch package.
"""
import logging
import sys

from paperfetcher import handsearch
from paperfetcher.exceptions import ContentNegotiationError

logger = logging.getLogger(__name__)

############################################################################
# Unit tests
############################################################################


def test_crossref_ris():
    data = handsearch.crossref_negotiate_ris(doi="10.1073/pnas.2018234118")
    print(data)


def test_crossref_ris_errorhandling():
    try:
        handsearch.crossref_negotiate_ris(doi="xx.yy.xx/1020304050")
    except ContentNegotiationError:
        return True
