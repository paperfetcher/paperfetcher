# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).
"""
Unit test suite for paperfetcher.handsearch package.
"""
import logging
import sys

from paperfetcher import handsearch

logger = logging.getLogger(__name__)

############################################################################
# Unit tests
############################################################################


def test_crossref_ris():
    data = handsearch.crossref_negotiate_ris(doi="10.1073/pnas.2018234118")
    logger.info(data)
