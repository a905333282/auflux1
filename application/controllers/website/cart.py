# -*- coding: utf-8 -*-
import json

from flask import Blueprint
from flask import request, jsonify
from flask_login import current_user, user_logged_in, login_required
from application.models.cart import Cart, CartEntry
from application.models.inventory.item import Item


cart = Blueprint('cart', __name__, url_prefix='/api/cart')


def get_cart():
    if current_user.is_authenticated:
        user = current_user
        user_id = str(user.id)
        current_cart = Cart.get_cart_or_create(user_id)
        return current_cart


@cart.route('/add/<string:item_id>', methods=['GET'])
@login_required
def add_to_cart(item_id):
    current_cart = get_cart()

    items = current_cart.entries
    if item_id in [i.item_id for i in items]:
        return jsonify(message='Failed, This item already has been add to your cart')
    else:
        if not Item.objects(item_id=item_id):
            return jsonify(message='Failed, item not exist')
        item = Item.objects(item_id=item_id).first_or_404()
        meta = item.to_cart()
        cart_entry = CartEntry(**meta)
        cart_entry.save()
        current_cart.entries.insert(0, cart_entry)
        current_cart.save()
        return jsonify(message='OK', cart_id=str(current_cart.id))


@cart.route('/remove/<string:item_id>', methods=['GET'])
@login_required
def remove_from_cart(item_id):
    cart_entry = CartEntry.objects(item_id=item_id).first_or_404()
    current_cart = get_cart()
    if cart_entry not in current_cart.entries:
        return jsonify(message='Failed',
                       error=_('invalid item_id for current user'))
    current_cart.update(pull__entries=cart_entry)
    cart_entry.delete()
    return jsonify(message='OK')


@cart.route('/all', methods=['GET'])
@login_required
def all_items_in_cart():
    current_cart = get_cart()
    items = current_cart.entries
    total_price=[]
    cart_content=[]
    for item in items:
        total_price.append(item.price)
        cart_content.append(item.to_json())
    return jsonify(message='OK', total_price=sum(total_price), cart_content=cart_content, count=len(total_price))