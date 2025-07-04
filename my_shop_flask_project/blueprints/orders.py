from flask import Blueprint, render_template
from flask_login import current_user
from models import Order, OrderItem, User
from extensions import db
from flask_login import login_required

# Define a Blueprint for order-related routes
orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/account")
@login_required
def account():
    """
     User account page route.

    - Requires login to access.
    - Retrieves the current logged-in user.
    - Queries all orders related to the current user from the database.
    - Passes the user object and their orders to the 'account.html' template for display.
    """

    # Current authenticated user
    user = current_user

    # Get all orders by this user
    orders = db.session.query(Order).filter_by(user_id = user.id).all()

    return render_template("account.html", user = user, orders = orders)
