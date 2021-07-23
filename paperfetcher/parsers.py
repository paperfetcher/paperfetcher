"""Functions to parse data returned from queries.

New parsers can be added here.
"""


def crossref_parse_date(date):
    """Function to parse date.

    Returns:
        str"""
    return "-".join([str(num) for num in date['date-parts'][0]])


def crossref_parse_authors(author_array):
    """Function to parse authors.

    Returns:
        str"""
    try:
        authors = ", ".join(d['family'] for d in author_array)
    except (KeyError, TypeError):
        authors = ""
    return authors


def crossref_parse_title(title):
    """Function to parse title.

    Returns:
        str"""
    return " ".join(title[0].split())
