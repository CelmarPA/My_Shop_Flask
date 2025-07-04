from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.products import products_bp
from blueprints.cart import cart_bp
from blueprints.orders import orders_bp
from blueprints.main import main_bp  # Blueprint for home and general routes
from config import Config
from extensions import db, login_manager, csrf, migrate, mail
from flask import Flask


def create_app():
    """
    Application factory function.

    - Creates and configures the Flask app instance.
    - Initializes all Flask extensions with the app.
    - Registers all Blueprints with appropriate URL prefixes.
    - Sets up the user loader callback for Flask-Login.

    :return: Configured Flask app instance.
    """

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Flask extensions with the app instance
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # User loader callback for Flask-Login to reload user from session
    @login_manager.user_loader
    def load_user(user_id):
        from models import User   # Import here to avoid circular imports
        return User.query.get(int(user_id))

    # Register blueprints with their URL prefixes
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(main_bp)    # Home route without prefix

    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()     # Create tables if they don't exist

    app.run(debug=True)
