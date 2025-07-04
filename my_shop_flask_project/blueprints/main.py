from datetime import date
from extensions import db
from flask import Blueprint, render_template
from flask_login import current_user
from models.product import Products
from models.order import Review, Order
from sqlalchemy import func

# Define a Blueprint for main site routes
main_bp = Blueprint("main", __name__)

# Get the current year (useful for templates, e.g. in footer)
current_year = date.today().year


@main_bp.route("/")
def home():
    """
    Home page route.

    Queries the database for the first 3 products to display on the homepage.

    Passes:
        - products: list of Products objects
        - logged_in: boolean, whether the user is authenticated
        - current_year: int, the current year for template footer
    """

    # Query for top 3 products by average rating (descending)
    top_products = (
        db.session.query(Products)
        .outerjoin(Review)   # Join Reviews to Products (include products with no reviews)
        .group_by(Products.id)  # Group by product to compute average rating per product
        .order_by(func.avg(Review.rating).desc().nullslast())   # Order by avg rating, placing products with no rating last
        .limit(3)   # Limit to top 3 products
        .all()
    )

    # Render 'index.html' template, passing the products and user info
    return render_template("index.html", top_products=top_products, logged_in = current_user.is_authenticated, current_year = current_year)
