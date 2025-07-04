import os

class Config:
    """
    Default configuration class used by Flask app.

    Sensitive information (like passwords or API keys) are hardcoded here
    for simplicity. In production, it is highly recommended to use environment
    variables with os.getenv() instead, for better security and flexibility.
    """

    # Flask settings
    SECRET_KEY = "your-secret-key-supersecure"    # ⚠️ Replace with a secure key or use os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///store.db"    # ⚠️ For production, use a proper database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail settings (replace with environment variables for security)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "<your-email>@gmail.com"  # ⚠️ Replace with your email or use os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = "<your-password-mail>"    # ⚠️ Never expose credentials in code; use os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = "<your-email>@gmail.com"  # ⚠️ Replace with your email or use os.getenv("MAIL_USERNAME")

    # Stripe API keys (use environment variables in production!)
    STRIPE_SECRET_KEY = "sk_test_yourTokenPrivateHere" # ⚠️ Use os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = "pk_test_yourTokenPublicHere"

## -----------------------------------------------
# Alternative: Secure environment-based config
# -----------------------------------------------
# Uncomment this version for production use.

# class Config:
#     """
#     Secure configuration class using environment variables.
#     Recommended for production to avoid hardcoding secrets.
#     """
#     SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
#     SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#
#     # Flask-Mail
#     MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
#     MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
#     MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ("true", "1", "t")
#     MAIL_USERNAME = os.getenv("MAIL_USERNAME")
#     MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
#     MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
#
#     # Stripe
#     STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
#     STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
