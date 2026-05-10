from flask import Flask, redirect, url_for
from config import Config
from database.models import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import blueprints here to avoid circular imports
        from backend.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        from backend.trips import trips_bp
        app.register_blueprint(trips_bp, url_prefix='/trips')

        from backend.features import features_bp
        app.register_blueprint(features_bp)

        from backend.profile import profile_bp
        app.register_blueprint(profile_bp)

        from backend.api import api_bp
        app.register_blueprint(api_bp)

        # Create all database tables
        db.create_all()

    @app.route('/')
    def index():
        return redirect(url_for('trips.dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
