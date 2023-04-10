from flask import current_app
import re


def create_index_if_not_exists(es, index_name):
    """Creates an index if it does not exist.

       Args:
           es: Elasticsearch instance.
           index_name (str): Name of the index to check/create.

       """
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)


def add_to_index(index, model):
    """Adds a document to the Elasticsearch index.

        Args:
            index (str): Name of the Elasticsearch index.
            model: The database model for which to add the document.

        """
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    hashtags = re.findall(r'#\w+', model.body)
    if hashtags:
        payload['hashtags'] = hashtags
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)


def remove_from_index(index, model):
    """Removes a document from the Elasticsearch index.

    Args:
        index (str): Name of the Elasticsearch index.
        model: The database model for which to remove the document.

    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    """Queries the Elasticsearch index.

    Args:
        index (str): Name of the Elasticsearch index.
        query (str): Query to be searched in the Elasticsearch index.
        page (int): Page number of the results to be returned.
        per_page (int): Number of results to be returned per page.

    Returns:
        ids: A list of ids of the matching documents.
        total: The total number of matching documents.

    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        size=per_page,
        from_=(page - 1) * per_page,
        query={"multi_match": {'query': query, 'fields': ['*']}})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']


def query_hashtag(index):
    """Queries the Elasticsearch index to get a list of unique hashtags.

    Args:
        index (str): Name of the Elasticsearch index.

    Returns:
        A list of tuples, where each tuple contains a hashtag and its count.

    """
    if not current_app.elasticsearch:
        return [], 0
    query = {
        'query': {
            'exists': {
                'field': 'hashtags'
            }
        },
        'size': 0,
        'aggregations': {
            'hashtags': {
                'terms': {
                    'field': 'hashtags.keyword'
                }
            }
        }
    }

    search = current_app.elasticsearch.search(index=index, body=query)
    buckets = search['aggregations']['hashtags']['buckets']
    return [(bucket['key'], bucket['doc_count']) for bucket in buckets]


def query_by_hashtag(index, hashtag, page, per_page):
    """Queries the Elasticsearch index to get a list of documents containing a specific hashtag.

       Args:
           index (str): Name of the Elasticsearch index.
           hashtag (str): Hashtag to be searched in the Elasticsearch index.
           page (int): Page number of the results to be returned.
           per_page (int): Number of results to be returned per page.

       Returns:
           res: A list of documents containing the given hashtag.
           total: The total number of documents containing the given hashtag.

       """
    if not current_app.elasticsearch:
        return [], 0
    query = {
        "query": {
            "match": {
                "hashtags": hashtag
            }
        }
    }
    search = current_app.elasticsearch.search(index=index, body=query, size=per_page,
        from_=(page - 1) * per_page)
    res = [hit['_source'] for hit in search['hits']['hits']]
    return res, search['hits']['total']['value']
