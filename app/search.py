from flask import current_app
import re


def add_to_index(index, model):
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
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
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
