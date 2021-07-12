from paperfetcher.datastructures import Query, CrossrefQuery, QueryError


def test_query():
    query = Query("")


def test_query_fail():
    query = Query("https://www.google.google")
    try:
        query()
    except QueryError:
        return True
    else:
        return False


def test_crossref_query():
    query = CrossrefQuery()
    query()


def test_json():
    pass
