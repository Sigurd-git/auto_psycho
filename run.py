#!/usr/bin/env python3
"""
Application entry point for the Auto Psycho TAT Platform.
This script starts the Flask development server.
"""

import os
from src.auto_psycho.app import create_app

if __name__ == "__main__":
    # Get configuration from environment
    config_name = os.environ.get("FLASK_ENV", "development")

    # Create application
    app = create_app(config_name)

    # Run application
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT", 8000))
