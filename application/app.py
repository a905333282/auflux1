from flask import Flask


from application.controllers.website.auth import auth
from application.controllers.website.address import address
from application.controllers.website.item import item
from application.controllers.website.cart import cart
from application.controllers.website.search import search
from application.controllers.admin.manage_items import manage_items



from application.extensions import db, login_manager, babel, admin, principal
from configs.config import BaseConfig
from application.extensions import es
from flask_principal import identity_loaded

from configs.config import ES_INDEX
from configs.config import ES_TYPE

app = Flask(__name__)

#admin
app.register_blueprint(manage_items)
es.indices.create(index=ES_INDEX, ignore=400)
#website
app.register_blueprint(auth)
app.register_blueprint(address)
app.register_blueprint(item)
app.register_blueprint(cart)
app.register_blueprint(search)

db.init_app(app)
babel.init_app(app)


app.config.from_object(BaseConfig())
db.register_connection(**app.config.get('USER_DB_CONFIG'))
db.register_connection(**app.config.get('DATA_DB_CONFIG'))
db.register_connection(**app.config.get('INVENTORY_DB_CONFIG'))
db.register_connection(**app.config.get('CART_DB_CONFIG'))

login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    import application.models as Models
    return Models.User.objects(id=id, is_deleted=False).first()
login_manager.login_message = ('Please log in to access this page.')
login_manager.needs_refresh_message = (
        'Please reauthenticate to access this page.')