from extensions import db
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from models.product import Products
from models.order import Review, Order
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from utils.helpers import user_bought_product
from utils.validators import admin_required

# Define a Blueprint for products-related routes
products_bp = Blueprint("products", __name__)


@products_bp.route("/products")
def products():
    """
    Route to display all products with review summaries.

    - Fetches all products.
    - For the authenticated user:
      * Determines which products have been bought.
      * Determines which products the user has reviewed.
    - Retrieves:
      * All reviews for each product.
      * The first 5 reviews for quick display.
      * Average rating per product.
    - Passes all data to the 'products.html' template for rendering.
    """

    products = Products.query.all()

    # Set of product IDs bought by current user
    bought_products = set()
    if current_user.is_authenticated:
        orders = Order.query.filter_by(user_id=current_user.id).all()
        for order in orders:
            for item in order.items:
                bought_products.add(item.product_id)
    bought_products = list(bought_products)

    # Dictionaries to hold review data for each product
    reviews_by_product = {}
    first_5_reviews_by_product = {}
    avg_rating_by_product = {}
    reviewed_products = set()

    for product in products:
        # Get all reviews for product, newest first
        all_reviews = Review.query.filter_by(product_id=product.id).order_by(Review.id.desc()).all()
        reviews_by_product[product.id] = all_reviews
        first_5_reviews_by_product[product.id] = all_reviews[:5]

        # Calculate average rating for product, default 0 if no reviews
        avg = db.session.query(func.avg(Review.rating)).filter(Review.product_id == product.id).scalar()
        avg_rating_by_product[product.id] = round(avg or 0, 2)

        # Track products reviewed by the current user
        if current_user.is_authenticated:
            for r in all_reviews:
                if r.user_id == current_user.id:
                    reviewed_products.add(product.id)
                    break

    # For controlling modal review form display (not perfect without AJAX)
    modal_product_id = None

    return render_template(
        "products.html",
        products=products,
        reviews_by_product=reviews_by_product,
        first_5_reviews_by_product=first_5_reviews_by_product,
        avg_rating_by_product=avg_rating_by_product,
        bought_products=bought_products,
        reviewed_products=reviewed_products,
        logged_in=current_user.is_authenticated,
        current_user=current_user,
        anonymize_name=lambda name: name[:1].upper() + "***",   # Helper to anonymize usernames
        modal_product_id=modal_product_id
    )


@products_bp.route("/product/<int:product_id>/reviews")
def product_reviews(product_id):
    """
    Show detailed reviews for a single product.

    - Fetch the product or 404.
    - Retrieve all reviews for this product, ordered by newest.
    - Calculate average rating.
    - For authenticated users, determine if they have reviewed and their bought products.
    - Pass all info to 'product_reviews.html' template.

    :param product_id: (int) product id
    """

    product = Products.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product.id).order_by(Review.id.desc()).all()
    avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
    avg_rating = round(avg_rating or 0, 2)

    has_reviewed = False
    bought_products = []

    if current_user.is_authenticated:
        has_reviewed = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None

        # List of product IDs bought by user
        orders = Order.query.filter_by(user_id=current_user.id).all()

        bought_products_set = set()

        for order in orders:
            for item in order.items:
                bought_products_set.add(item.product_id)

        bought_products = list(bought_products_set)

    return render_template(
        "product_reviews.html",
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        logged_in=current_user.is_authenticated,
        current_user=current_user,
        bought_products=bought_products,
        has_reviewed=has_reviewed
    )


@products_bp.route("/product/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id):
    """
    Handle form submission for adding a product review.

    - Ensure user has purchased the product (else flash error).
    - Ensure user has not already reviewed the product.
    - Validate rating value.
    - Create and save a new Review record.
    - Commit to database with exception handling for duplicate reviews.
    - Flash success message and redirect to products page.

    :param product_id: (int) product id.
    """

    # Check if user bought product
    if not user_bought_product(current_user.id, product_id):
        flash("You can only review products you've purchased.", "error")

        return redirect(url_for("products.products"))

    # Check if user already reviewed
    existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_review:
        flash("You have already reviewed this product.", "error")

        return redirect(url_for("products.products"))

    # Get rating and comment from form
    try:
        rating = int(request.form.get("rating", 0))

    except ValueError:
        flash("Invalid rating value.", "error")

        return redirect(url_for("products.products"))

    comment = request.form.get("comment", "")

    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=rating,
        comment=comment
    )

    db.session.add(review)

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        flash("You have already reviewed this product.", "error")

        return redirect(url_for("products.products"))

    flash("Review submitted successfully.", "success")

    return redirect(url_for("products.products"))


@products_bp.route("/product/<int:product_id>/review_form")
def review_form(product_id):
    """
    AJAX endpoint returning the review form HTML fragment.

    - If user not logged in, returns HTML prompting to log in.
    - Checks if user has bought the product.
    - Checks if user has already reviewed.
    - Returns rendered HTML form fragment for submitting a review.

    :param product_id: (int) product id.
    """

    if not current_user.is_authenticated:
        return jsonify(html="<p>Please <a href='/login'>log in</a> to leave a review.</p>")

    product = Products.query.get_or_404(product_id)

    # Check if user bought product
    if not user_bought_product(current_user.id, product_id):
        return jsonify(html="<p>You can only review products you've purchased.</p>")

    # Check if user already reviewed
    existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_review:
        return jsonify(html="<p>You have already reviewed this product.</p>")

    html_form = render_template("review_form_fragment.html", product=product)

    return jsonify(html=html_form)
