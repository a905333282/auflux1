# -*- coding: utf-8 -*-
import datetime
import hashlib
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from application.extensions import db, bcrypt
from flask import current_app
from flask_login import UserMixin
from configs.enum import USER_GENDER, USER_ROLE, NOTI_TYPE
from configs import signals


__all__ = ['UserAccount', 'UserInformation', 'User']


class UserInformation(db.EmbeddedDocument):
    gender = db.StringField(max_length=1, choices=USER_GENDER)


class UserAccount(db.EmbeddedDocument):
    '''
    The UserAccount class contains user personal informations
    and account settings
    '''
    created_at = db.DateTimeField(default=datetime.datetime.utcnow,
                                  required=True)

    # login related
    mobile_number = db.StringField(required=True, unique=True)
    email = db.EmailField()
    is_email_verified = db.BooleanField(default=False)
    _password = db.StringField(max_length=255)
    activation_key = db.StringField(max_length=255)
    activate_key_expire_date = db.DateTimeField()

    # ===============================================
    # password
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password).decode('utf-8')
        print (self._password)

    def check_password(self, password):
        if self.password is None:
            return False
        print(self.password)
        return bcrypt.check_password_hash(self.password, password)

    def to_json(self):
        return dict(created_at=str(self.created_at),
                    mobile_number=self.mobile_number)


class User(db.Document, UserMixin):
    '''
    The User class contains only basic and frequently used information


    Superclass UserMixin can provide four authenticate methods required
    by Flask-Login.
    '''
    meta = {
        'db_alias': 'user_db',
    }
    name = db.StringField(required=True)
    account = db.EmbeddedDocumentField('UserAccount')
    information = db.EmbeddedDocumentField('UserInformation')

    selling_items = db.ListField(db.StringField())
    sold_items = db.ListField(db.StringField())
    owned_item = db.ListField(db.StringField())
    bought_item = db.ListField(db.StringField())

    roles = db.ListField(db.StringField())

    # favor related (item_ids)
    num_favors = db.IntField(default=0, min_value=0)
    favor_items = db.ListField(db.StringField())

    addresses = db.ListField(db.ReferenceField('Address'))
    default_address = db.ReferenceField('Address')

    verified = db.BooleanField(default=False)
    is_deleted = db.BooleanField(default=False)
    deleted_date = db.DateTimeField()

    def __unicode__(self):
        return '%s' % str(self.id)
        #return u'{}'.format(self.name)

    @property
    def avatar_thumb(self):
        return self.avatar_url[:23] + 'avatar_thumbs/80x80/' + self.avatar_url[23:]

    @db.queryset_manager
    def active(doc_cls, queryset):
        return queryset.filter(is_deleted=False)

    @property
    def is_admin(self):
        return USER_ROLE.ADMIN in self.roles

    @classmethod
    def is_verified(self):
        return self.verified

    def verify(self):
        self.verified = True
        self.save()
        return True

    def to_json(self):
        data = dict(name=self.name,
                    created_at=str(self.account.created_at),
                    id=str(self.id)
                )
        return data

    @classmethod
    def authenticate(cls, mobile_number=None, password=None):
        if mobile_number:
            user = cls.active(account__mobile_number=mobile_number).first()
        else:
            user = None
        if user:
            authenticated = user.account.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    def generate_auth_token(self, expires_in=604800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': str(self.id)}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.objects(id=data['id']).first()


    @classmethod
    def create(cls, mobile_number, password, name, email=None):


        # account
        account = UserAccount(mobile_number=mobile_number,
                              email=email,
                              is_email_verified=True)
        account.password = password

        user = User(name=name,
                    roles=[USER_ROLE.MEMBER],
                    information=UserInformation(),
                    account=account)

        user.save()

        signals.user_signup.send('system', user=user)
        return user


