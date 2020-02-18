from . import auth
from . import address
from . import item
from . import cart
from . import search

website_blueprints = [
    auth.auth,
    address.address,
    item.item,
    cart.cart,
    search.search
]
