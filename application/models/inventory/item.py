# -*- coding: utf-8 -*-
from datetime import datetime
from math import ceil

from mongoengine.errors import DoesNotExist
from flask import current_app, url_for, g
from application.extensions import db
from configs.enum import SEX_TAG, CURRENCY, ITEM_STATUS
from application.utils import update_modified



__all__ = ['Item']


@update_modified.apply
class Item(db.Document):
    meta = {
        'db_alias': 'inventory_db'
    }

    owner = db.StringField()
    owner_id = db.StringField()
    item_id = db.StringField(primary_key=True) # id
    eth_token = db.StringField()
    ## price
    price = db.FloatField()
    primary_img = db.StringField()
    images = db.ListField(db.StringField())
    # basic information
    title = db.StringField()
    brand = db.StringField()
    condition = db.StringField()
    description = db.StringField(default='')
    madein = db.StringField()
    #color = db.ListField(db.StringField())
    location = db.StringField()

    main_category = db.StringField()
    sub_category = db.StringField()
    sex_tag = db.StringField()
    tags = db.ListField(db.StringField())

    availability = db.BooleanField(default=True)
    state = db.StringField()

    # time
    created_at = db.DateTimeField(default=datetime.utcnow)
    modified = db.DateTimeField()
    creator = db.StringField()

    def __unicode__(self):
        return '%s' % self.item_id

    def __repr__(self):
        return '%s' % self.item_id

    @property
    def cart_fields(self):
        return ['item_id', 'title', 'primary_img', 'price']

    def to_cart(self):
        result = {f: getattr(self, f) for f in self.cart_fields}
        return result

    @db.queryset_manager
    def available_items(doc_cls, queryset):
        return queryset.filter(availability=True)

    @property
    def small_thumbnail(self):
        return self.primary_img[:23] + 'thumbnails/150x150/' + self.primary_img[23:]

    @property
    def large_thumbnail(self):
        return self.primary_img[:23] + 'thumbnails/400x400/' + self.primary_img[23:]

    @classmethod
    def create(cls, item):

        item = Item(**item).save()
        item_id = item.item_id

        return item_id



