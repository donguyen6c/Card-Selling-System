import pytest
from flask import Flask

from selenium.webdriver.chrome.service import Service
from cardapp import db
from selenium import webdriver
from cardapp.apis import carts_api, pay_api

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 2
    app.config["SECRET_KEY"] = "01-05-2026-cardselling-system"
    db.init_app(app)

    app.register_blueprint(carts_api.carts_api)
    app.register_blueprint(pay_api.pay_api)
    return app

@pytest.fixture
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def mock_cloudinary(monkeypatch):
    def fake_upload(file):
        return {'secure_url':'https://fake-image.com'}

    monkeypatch.setattr('cloudinary.uploader.upload',fake_upload)

@pytest.fixture
def driver():
    service = Service(executable_path='.venv/chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()