# -*- coding: utf-8 -*-
import datetime
import json

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_babel import gettext as _

from application.utils import get_session_key, paginate
import application.models as Models
import application.services.json_tmpl as Json


item = Blueprint('item', __name__, url_prefix='/api/items')


@item.route('/favors_id', methods=['GET'])
@login_required
def favor_items():
    if current_user.is_authenticated:
        user = current_user
        favor_items = user.favor_items
        return jsonify(message='OK', id_list=favor_items)


@item.route('/favors_count', methods=['GET'])
@login_required
def favors_count():
    if current_user.is_authenticated:
        user = current_user
        favor_items = user.favor_items
        return jsonify(message='OK', count=len(favor_items))


@item.route('/favor/<string:item_id>', methods=['GET'])
@login_required
def item_favor(item_id):
    item = Models.Item.objects(item_id=item_id).first_or_404()
    id = item.item_id
    if current_user.is_authenticated:
        user = current_user
        if id not in user.favor_items:
            user.favor_items.append(id)
            user.save()
            return jsonify(message='OK')
        else:
            return jsonify(message='you already marker this item')


@item.route('/unfavor/<string:item_id>', methods=['GET'])
@login_required
def item_unfavor(item_id):
    item = Models.Item.objects(item_id=item_id).first_or_404()
    id = item.item_id
    if current_user.is_authenticated:
        user = current_user
        if id in user.favor_items:
            user.favor_items.remove(id)
            user.save()
            return jsonify(message='OK')
        else:
            return jsonify(message="Failed, you didn't mark this item")
