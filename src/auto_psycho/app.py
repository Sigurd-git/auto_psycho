"""
Main Flask application for the Auto Psycho TAT Platform.
This module initializes and configures the Flask application.
"""

import os
from flask import Flask
from src.auto_psycho.config import config
from src.auto_psycho.models import db


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function to create and configure Flask app.

    Args:
        config_name: Configuration environment name ('development', 'production', 'testing')

    Returns:
        Configured Flask application instance
    """
    # Create Flask application instance
    app = Flask(__name__)

    # Determine configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Create database tables
    with app.app_context():
        # Ensure data directory exists in project root
        basedir = os.path.abspath(os.path.dirname(__file__))
        project_dir = os.path.dirname(os.path.dirname(basedir))
        data_dir = os.path.join(project_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        db.create_all()

    return app


def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.

    Args:
        app: Flask application instance
    """
    from src.auto_psycho.views.main import main_bp
    from src.auto_psycho.views.experiment import experiment_bp
    from src.auto_psycho.views.admin import admin_bp
    from src.auto_psycho.views.api import api_bp

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(experiment_bp, url_prefix="/experiment")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")


# Create application instance for development
if __name__ == "__main__":
    app = create_app("development")
    app.run(debug=True, host="0.0.0.0", port=5000)
