# -*- coding: utf-8 -*-

from application.extensions import db
from datetime import datetime

__all__ = ['Cart', 'CartEntry']


class CartEntry(db.Document):
    meta = {
        'db_alias': 'cart_db'
    }
    item_id = db.StringField(required=True)
    title = db.StringField()
    primary_img = db.StringField()
    price = db.FloatField()
    created_at = db.DateTimeField(default=datetime.utcnow)

    def __unicode__(self):
        return '%s' % str(self.id)

    @property
    def fields(self):
        return ['item_id', 'title', 'primary_img', 'price', 'created_at']

    def to_json(self):
        result = {f: getattr(self, f) for f in self.fields}
        return result


class Cart(db.Document):
    meta = {
        'db_alias': 'cart_db',
        'indexes': ['user_id']
    }
    entries = db.ListField(db.ReferenceField('CartEntry'))
    logistic_free = db.FloatField()
    total_price = db.FloatField()
    user_id = db.StringField()

    def __repr__(self):
        return '<Cart: {}>'.format(self.id)

    @classmethod
    def get_cart_or_create(cls, user_id):
        try:
            cart = cls.objects.get(user_id=user_id)

        except:
            cart = cls(user_id=user_id).save()

        return cart

    def total_price(self):
        total_price = 0
        for i in self.entries:
            total_price += i.price
        self.total_price = total_price
        return total_price

