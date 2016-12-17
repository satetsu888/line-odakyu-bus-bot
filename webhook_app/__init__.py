from flask import Flask

def create_app(cfg=None):
    app = Flask(__name__)

    return app
