"""
Entry point for BMSmart backend.
"""
import os
from app import create_app

# Get configuration from environment variable, default to development
config_name = os.environ.get('FLASK_CONFIG', 'development')

# Create the Flask app using the factory
app = create_app(config_name)

if __name__ == '__main__':
    # Run Flask server in debug mode
    app.run(
        debug=True,
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000))
    )
