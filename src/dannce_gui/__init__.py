import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path="/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/dannce_gui_instance",
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "db.sqlite")
    )

    if test_config is None:
        app.config.from_pyfile(
            "config.py",
        )
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Hello world"

    from . import db

    db.init_app(app)

    from . import api

    app.register_blueprint(api.bp_api)

    return app
