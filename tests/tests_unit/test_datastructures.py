from paperfetcher.datastructures import Query, CrossrefQuery, QueryError


def test_query():
    query = Query("https://api.github.com")
    query()
    print(query.response.text)


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
    query.query_base += "works"
    query()
    print(query.response.text)


def test_json():
    query = CrossrefQuery()
    query.query_base += "works"
    query()
    print(query.response.json())
