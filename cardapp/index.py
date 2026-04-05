from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)

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
    "specs_route": "/docs"
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

# Khởi tạo Swagger
swagger = Swagger(app, config=swagger_config, template=template)

# ==========================================
#CÁC ROUTE TRONG INDEX.PY
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)