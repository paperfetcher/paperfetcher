"""Definitions of all Exceptions raised by paperfetcher."""


class QueryError(Exception):
    """Exception raised when query fails."""
    pass


class SearchError(Exception):
    """Exception raised when search fails."""
    pass


class DatasetError(Exception):
    """Exception raised when an incorrect operation is performed on a dataset."""
    pass
