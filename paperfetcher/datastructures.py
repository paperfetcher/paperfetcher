"""Custom data structures (classes) for paperfetcher"""
import urllib
import json


class QueryError(Exception):
    pass


class Query:
    """Base class for queries."""
    def __init__(self, base_url=None):
        self.query = base_url
        self.response = None

    def __call__(self):
        """Runs query and stores response."""
        try:
            self.response = urllib.request.urlopen(self.query)
        except urllib.error.HTTPError as e:
            raise QueryError("Unable to run query, server responded with %s" % (e.code))
        except urllib.error.URLError as e:
            raise QueryError("Unable to run query, could not reach server. Reason: %s" % (e.reason))

    def parse_json_response(self):
        """Parses JSON response."""
        if self.response is None:
            raise RuntimeError("Need to execute query successfully first.")
        else:
            return json.loads(self.response.read().decode())


class CrossrefQuery(Query):
    """Class for Crossref queries"""
    def __init__(self):
        super().__init__("https://api.crossref.org/")
