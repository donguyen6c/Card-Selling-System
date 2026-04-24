import re
from flask import Flask, jsonify, request, redirect, render_template, session
from flasgger import Swagger, swag_from
from cardapp.apis import carts_api, auth_api
from cardapp import dao, login, app, utils
from cardapp.models import CardType

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs",
}


template = {
    "swagger": "2.0",
    "info": {
        "title": "CaoThe Website",
        "description": "Hệ thống cung cấp thẻ Viettel, Mobi, Vina, Garena, Zing...",
        "contact": {
            "responsibleOrganization": "Selling Card Team",
            "email": "donguyen6c@gmail.com",
        },
        "version": "1.0.1"
    },
    "basePath": "/",
    "schemes": ["http", "https"]
}

# ==========================================
# CÁC ROUTE TRONG INDEX.PY
# ==========================================
app.register_blueprint(auth_api.auth_bp)

app.register_blueprint(carts_api.carts_api)

app.register_blueprint(inven_bp)

app.register_blueprint(history_bp)

swagger = Swagger(app, config=swagger_config, template=template)

@app.route('/')
def index():
    categories = dao.load_categories()
    products = dao.load_products()
    banners = dao.load_banners()

    phone_categories = [p for p in categories if p.card_type == CardType.PHONE]
    game_categories = [g for g in categories if g.card_type == CardType.GAME]

    cart = session.get('cart', {})
    t10_count = sum(c['quantity'] for c in cart.values() if c['price'] <= 30000)
    t5_count = sum(c['quantity'] for c in cart.values() if 30000 < c['price'] <= 300000)
    t3_count = sum(c['quantity'] for c in cart.values() if c['price'] > 300000)

    return render_template('index.html', categories=categories, products=products, banners=banners,
                           phone_categories=phone_categories, game_categories=game_categories, cart_tier_stats={'t10': t10_count, 't5': t5_count, 't3': t3_count})

@app.context_processor
def common_response():
    cart = session.get('cart', {})
    cart_stats = utils.stats_cart(cart)
    return {
        'cart_stats': cart_stats
    }

@app.route('/promotion')
def promotion_view():
    discounts = dao.load_discounts()
    return render_template('promotion.html', discounts=discounts)

@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)

if __name__ == '__main__':
    app.run(debug=True)

