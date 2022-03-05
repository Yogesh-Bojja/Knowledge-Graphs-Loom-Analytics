from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.pdf import bp as pdf_bp

    app.register_blueprint(pdf_bp, url_prefix="/pdf")

    from app.graph import bp as graph_bp

    app.register_blueprint(graph_bp, url_prefix="/graph")

    app.config["SECRET_KEY"] = "pdfUpload"
    app.config["UPLOAD_EXTENSIONS"] = [".pdf"]

    return app
