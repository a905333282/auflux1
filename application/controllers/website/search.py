from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_babel import gettext as _
from application.utils import get_session_key, paginate
import application.models as Models
import application.services.json_tmpl as Json
from application.extensions import es
from configs.config import ES_INDEX
from configs.config import ES_TYPE

search = Blueprint('search', __name__, url_prefix='/api/search')


def search_dsl_generator(price_low=None, price_high=None, filter_list=None, key_word=None, count=20, page=0):
    must = []

    if key_word:
        must.append({"match": {"title": key_word}})

    if filter_list:
        for i in filter_list.keys():
            must.append({"match": {i: filter_list[i]}})

    filter_temp = [{"range": {"price": {"gte": None, "lte": None}}}]

    if price_low:
        filter_temp[0]["range"]["price"]["gte"] = price_low
    if price_high:
        filter_temp[0]["range"]["price"]["lte"] = price_high

    dsl = {
        "query": {
            "bool": {
                "must": must,
                "filter": filter_temp,
            },
        },
        "from": count * page,
        "size": count * (page + 1)
    }

    return dsl


@search.route('/', methods=['GET'])
@login_required
def root():
    if current_user.is_authenticated:
        print(list(request.args))
        key_word = request.args.get('key_word')
        page = int(request.args.get('page'))
        dsl = search_dsl_generator(key_word=key_word, page=page)
        result = es.search(index=ES_INDEX, doc_type=ES_TYPE, body=dsl)
        return jsonify(message='OK', result={"count": result['hits']['total']['value'],
                                             "entries_count": len(result['hits']['hits']),
                                             "items": result['hits']['hits']})


@search.route('/filter', methods=['POST'])
@login_required
def filter_query():
    if current_user.is_authenticated:
        contact = request.json
        key_word = None
        filters = None
        low_price = None
        high_price = None
        page = 0
        query_elements = list(contact.keys())
        if 'key_word' in query_elements:
            key_word = contact["key_word"]
            print(key_word)
        if 'filters' in query_elements:
            filters = contact["filters"]
            print(filters)
        if 'low_price' in query_elements:
            low_price = contact["low_price"]
            print(low_price)
        if 'high_price' in query_elements:
            high_price = contact["high_price"]
            print(high_price)
        if 'page' in query_elements:
            page = contact["page"]
            print(page)

        dsl = search_dsl_generator(key_word=key_word, filter_list=filters, price_low=low_price,
                                   price_high=high_price, page=page)

        result = es.search(index=ES_INDEX, doc_type=ES_TYPE, body=dsl)
        return jsonify(message='OK', result={"count": result['hits']['total']['value'],
                                             "entries_count": len(result['hits']['hits']),
                                             "items": result['hits']['hits']})


'''def filter_query():
    if current_user.is_authenticated:
        key_word = None
        filters = None
        low_price = None
        high_price = None
        page = None
        query_elements = list(request.args)
        if 'key_word' in query_elements:
            key_word = request.args.get('key_word')
            print(key_word)
        if 'filters' in query_elements:
            filters = request.args.get('filters')
            print(filters)
        if 'low_price' in query_elements:
            low_price = request.args.get("low_price")
            print(low_price)
        if 'high_price' in query_elements:
            high_price = request.args.get("high_price")
            print(high_price)
        if 'page' in query_elements:
            page = int(request.args.get("page"))
            print(page)

        dsl = search_dsl_generator(key_word=key_word, filter_list=filters, price_low=low_price, price_high=high_price, page=page)
        result = es.search(index=ES_INDEX, doc_type=ES_TYPE, body=dsl)
        return jsonify(message='OK', result={"count": result['hits']['total']['value'],
                                             "entries_count": len(result['hits']['hits']),
                                             "items": result['hits']['hits']})'''