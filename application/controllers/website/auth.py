# -*- coding: utf-8 -*-
import time
import random
import application.models as Models
from flask import Blueprint, request, jsonify, current_app, redirect, render_template
from flask_login import current_user, login_user, logout_user, \
    login_required
import application.services.json_tmpl as Json
from flask_babel import gettext as _
from configs.config import TIMEOUT_ACTIVE
from application.extensions import r


auth = Blueprint('auth', __name__, url_prefix='/api/auth')
'''
/user_info                  GET
/logout                     GET
/login_mobile_number        POST
/login_with_token           POST
/signup                     POST
/verify                     GET
/forget_password            POST
/change_password            POST
'''


def random_generator():
    return str(random.randint(100000, 999999))


def put_redis(user_id, timeout=TIMEOUT_ACTIVE):
    vcode = random_generator()
    while r.get(vcode):
        vcode = random_generator()
    if r.set(vcode, user_id, ex=timeout):
        return vcode
    else:
        return False


def sms_active(vcode):
    user_id = r.get(vcode)
    return user_id


@auth.route('/user_info', methods=['GET'])
@login_required
def user_info():
    if not current_user.is_authenticated:
        return jsonify(message='Failed', logged_in=False)

    info = Json.get_user_info(current_user)
    return jsonify(message='OK', logged_in=True, user=info)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify(message='OK')
    else:
        return jsonify(message='There is not authenticated user')


@auth.route('/login_mobile_number', methods=['POST'])
def login_mobile_number():
    data = request.json
    mobile_number = data.get('mobile_number', '')
    user, authenticated = Models.User.authenticate(
        mobile_number=mobile_number, password=data.get('password', ''))
    print(user.roles)
    if not authenticated:
        return jsonify(message='Failed, wrong password or username')

    if "ADMIN" in user.roles:
        login_user(user, remember=True)
        return jsonify(message='OK', user=Json.get_user_info(user),
                       remember_token=user.generate_auth_token())

    if not user.verified:
        return jsonify(message='Failed, you need to active your account through sms')
    login_user(user, remember=True)
    return jsonify(message='OK', user=Json.get_user_info(user),
                   remember_token=user.generate_auth_token())


@auth.route('/login_with_token', methods=['POST'])
def login_with_token():
    data = request.json
    token = data.get('token', '')
    user = Models.User.verify_auth_token(token)
    if not user:
        return jsonify(message='Failed')
    login_user(user, remember=True)
    return jsonify(message='OK', user=Json.get_user_info(user),
                   remember_token=user.generate_auth_token())


@auth.route('/signup', methods=['POST'])
def mobile_number_signup():
    data = request.json
    mobile_number = data.get('mobile_number')
    password = data.get('password')
    name = data.get('name')
    if not password:
        # 不能为空
        return jsonify(message='Failed', error=_(u'Please fill in.'))

    if Models.User.objects(account__mobile_number=mobile_number):
        repetition = Models.User.objects(account__mobile_number=mobile_number).first_or_404()
        if not repetition.verified:
            repetition.delete()
        else:
            return jsonify(message='Failed', error=_(u'This mobile_number has been registered.'))

    if not name:
        name = 'No.' + str(time.time()).replace('.','')
    user = Models.User.create(mobile_number=mobile_number, password=password, name=name)

    #login_user(user, remember=True)
    return jsonify(message='Verification code has been sent to your phone, please check it to complete registration',
                   verification=put_redis(str(user.id)))


@auth.route('/verify', methods=['POST'])
def sms_verify():
    data = request.json
    vcode = data.get('vcode')
    uer_id = sms_active(vcode)
    user = Models.User.objects(id=uer_id).first_or_404()
    user.verify()
    login_user(user, remember=True)
    return jsonify(message='OK', user_id=str(user.id))


@auth.route('/forget_password', methods=['POST'])
def forget_password():
    data = request.json
    mobile_number = data.get('mobile_number')
    user = Models.User.objects(account__mobile_number=mobile_number).first_or_404()
    if user:
        return jsonify(message='Verification code has been sent to your phone, please check it to change your password',
                       verification=put_redis(str(user.id)))
    else:
        return jsonify(message="This mobile number hasn't  been registered")


@auth.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    vcode = data.get('vcode')
    password = data.get('password')
    uer_id = sms_active(vcode)
    user = Models.User.objects(id=uer_id).first_or_404()
    user.account.password = password
    user.save()
    return jsonify(message="OK")
