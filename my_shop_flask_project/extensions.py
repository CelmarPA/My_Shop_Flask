# extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail

# Global instances of Flask extensions.
# These will be initialized later in the main app factory function,
# allowing for better application modularity and testing.

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
mail = Mail()
