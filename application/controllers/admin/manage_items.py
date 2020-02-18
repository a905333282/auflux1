import json
from flask import Blueprint, jsonify, request, Response, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from configs.regions_list import REGION_HIERARCHY
import application.models as Models
from application.extensions import es
from configs.config import ES_INDEX
from configs.config import ES_TYPE
from PIL import Image
import uuid
import boto3

manage_items = Blueprint('manage_items', __name__, url_prefix='/api/manage_items')


AWS_ACCESS_KEY_ID = 'AKIAJYQHJGFNOI2SWVKA'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'aufluxtestv1'


def add_to_es(data, id, index=ES_INDEX, doc_type=ES_TYPE,):
    result = es.index(index=index, doc_type=doc_type, body=data, id=id)
    return result


def is_admin():
    roles = current_user.roles
    if 'ADMIN' in roles:
        return True
    else:
        return False


def not_null(dic):
    result = {}
    for i in dic.keys():
        if dic[i] in [None, u"None", "", "null"]: continue
        else:
            result[i] = dic[i]
    return result


'''
@app.route('/upload_new_item', methods=['POST'])
def upload_new_item():
    name = request.form['user_name']
    number = request.form['number']
    user_img = request.files['file'].read()
    user_img = io.BytesIO(user_img)
    roiImg = Image.open(user_img)
    filename = r'auflux/{}/{}.jpeg'.format(uniId(number), str(uuid.uuid1()))
    path = r'auflux/{}'.format(uniId(number))
    if not os.path.exists(path):
        os.makedirs(path)
    roiImg.save(filename)
    filename = r'auflux/{}/{}.jpeg'.format(uniId(number), str(uuid.uuid1()))
    path = r'auflux/{}'.format(uniId(number))
    if not os.path.exists(path):
        os.makedirs(path)
    roiImg.save(filename)
    return ('success')'''


def bytes2s3(image, aws_path):
    s3 = boto3.resource('s3',
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    try:
        s3.Bucket('aufluxtestv1').put_object(Key=aws_path, Body=image)

    except Exception as e:
        pass


@manage_items.route('/upload_new_item', methods=['POST'])
@login_required
def upload_new_item():
    user_img = request.files['file'].read()
    print(type(user_img))
    bytes2s3(user_img, aws_path = 'auflux/15485/picture.jpeg')
    return jsonify(message="Failed", desc='aaa')


@manage_items.route('/add_item', methods=['POST'])
@login_required
def add_item():
    if is_admin():

        data = request.form
        user_imgs = request.files

        if not data or not user_imgs:
            return jsonify(message="Failed", desc='Wrong format of data')

        uni_id = str(uuid.uuid1())

        n = 0
        for image in user_imgs:
            bytes2s3(user_imgs[image].read(), aws_path='auflux/{}/picture{}.jpeg'.format(uni_id, n))
            n = n + 1

        data_temp = {}
        for key in data:
            data_temp[key] = data[key]

        data_temp["item_id"] = uni_id
        item_id = Models.Item.create(data_temp)
        result = add_to_es(data=data_temp, id=uni_id)

        return jsonify(message='OK', item_id=item_id, data=data_temp, elastic_result=result)

    else:
        return jsonify(message='False', error='Permission denied')
'''@manage_items.route('/add_item', methods=['POST'])
@login_required
def add_item():
    if is_admin():
        try:
            data = request.json
            data = not_null(data)
            #print(data)
            #user_imgs = request.files

            #print(type(user_imgs))

            uni_id = str(uuid.uuid1())
            
            for i in 
            bytes2s3(user_img, aws_path='auflux/{}/picture.jpeg'.format(uni_id))
            
            data["item_id"] = uni_id
            item_id = Models.Item.create(data)
            result = add_to_es(data=data, id=uni_id)

            return jsonify(message='OK', item_id=item_id, data=data, elastic_result=result)
        except Exception as e:
            return jsonify(message="Failed", desc='Wrong format of json')

    else:
        return jsonify(message='False', error='Permission denied')'''
