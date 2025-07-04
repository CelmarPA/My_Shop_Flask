from config import Config
from datetime import datetime
from extensions import db
from flask import Blueprint, session, redirect, url_for, flash, request, render_template, jsonify
from flask_login import current_user, login_required
from models.product import Products
from models.order import Order, OrderItem
import stripe
from utils.helpers import is_profile_complete
from utils.email import send_order_confirmation_email

# Set the Stripe secret key for API calls
stripe.api_key = Config.STRIPE_SECRET_KEY

# Create a Flask Blueprint for cart-related routes
cart_bp = Blueprint("cart", __name__)


def initialize_cart():
    """
    Ensure the 'cart' key exists in the session.
    If not present, initialize it as an empty dictionary.
    """

    if "cart" not in session:
        session["cart"] = {}


@cart_bp.route("/cart", methods=["GET","POST"])
def cart():
    """
    Display cart contents:
    - Lists products with name, price, quantity
    - Shows total price
    - Passes Stripe public key for frontend payment integration
    - Checks if profile is complete if user logged in
    """

    initialize_cart()
    cart = session["cart"]

    cart_items = []
    total = 0

    # Iterate through items in the cart to build list and calculate total
    for product_id, item in cart.items():
        price = float(item["price"])
        quantity = int(item["quantity"])
        subtotal = price * quantity
        total += subtotal
        cart_items.append({
            "id": product_id,
            "name": item["name"],
            "price": price,
            "quantity": quantity
        })

    user_data = current_user.user_data if current_user.is_authenticated else None
    logged_in = current_user.is_authenticated

    profile_complete = False
    if logged_in:
        profile_complete = is_profile_complete(current_user)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        logged_in=current_user.is_authenticated,
        profile_complete=is_profile_complete(current_user) if current_user.is_authenticated else False,
        stripe_public_key=Config.STRIPE_PUBLIC_KEY
    )


@cart_bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    """
    Add a product to the cart.
    If product is already in cart, increment its quantity.
    Update the session and flash a success message.
    Redirect either to cart page or products listing depending on form data.

    :param product_id: (int) product id
    """

    initialize_cart()

    # Retrieve product from database or raise 404 if not found
    product = db.get_or_404(Products, product_id)
    product_id_str = str(product_id)    # Use string keys for session dict

    cart = session["cart"]

    if product_id_str in cart:
        cart[product_id_str]["quantity"] += 1
    else:
        cart[product_id_str] = {
            "name": product.name,
            "price": product.price,
            "quantity": 1
        }

    session.modified = True      # Mark session as modified so Flask saves it

    flash(f"Added {product.name} to cart.", "success")

    # Redirect to cart page if 'redirect_to_cart' is '1', else to products page
    if request.form.get("redirect_to_cart") == "1":
        return redirect(url_for("cart.cart"))

    return redirect(url_for("products.products"))


@cart_bp.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    """
    Remove one unit of a product from the cart.
    If quantity goes below 1, remove the product completely.
    Flash appropriate message and redirect to the cart.

    :param product_id: (int) product id
    """

    initialize_cart()

    product_id_str = str(product_id)
    cart = session["cart"]

    if product_id_str in cart:
        if cart[product_id_str]["quantity"] > 1:
            cart[product_id_str]["quantity"] -= 1
            flash("One unit removed from cart.", "info")

        else:
            del cart[product_id_str]
            flash("Item removed from cart.", "info")

        session.modified = True

    return redirect(url_for("cart.cart"))


@cart_bp.route("/delete_item/<int:product_id>", methods=["POST"])
def delete_item(product_id):
    """
    Remove a product entirely from the cart regardless of quantity.
    Flash warning message and redirect to cart.

    :param product_id: (int) product id
    """

    initialize_cart()
    cart = session["cart"]

    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

        session.modified = True
        flash("Item completely removed from cart.", "warning")

    return redirect(url_for("cart.cart"))


@cart_bp.route("/update_quantity/<int:product_id>", methods = ["POST"])
def update_quantity(product_id):
    """
    Update the quantity of a product in the cart.
    If new quantity is less than 1, remove the item.
    Handle invalid input gracefully.

    :param product_id: (int) product id
    """

    initialize_cart()
    cart = session["cart"]

    product_id_str = str(product_id)

    try:
        new_quantity = int(request.form.get("quantity", 1))

    except ValueError:
        flash("Invalid quantity.", "error")
        return redirect(url_for('cart.cart'))

    if new_quantity < 1:
        del cart[product_id_str]
        flash("Item removed from cart.", "warning")

    else:
        if product_id_str in cart:
            cart[product_id_str]["quantity"] = new_quantity
            flash("Quantity updated.", "success")

    session.modified = True

    return redirect(url_for("cart.cart"))


@cart_bp.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    """
    Create a Stripe Checkout session.
    - Verify user profile completeness.
    - Verify cart is not empty.
    - Prepare line items for Stripe API.

    :return: Return the session ID as JSON to frontend.
    """

    if not is_profile_complete(current_user):
        # Return error JSON for frontend handling
        return jsonify({"error": "Profile incomplete. Please complete your profile to proceed."}), 400

    cart = session.get("cart", {})

    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    line_items = []

    for item in cart.values():
        try:
            # Stripe requires amount in cents as integer
            unit_amount = int(float(item["price"]) * 100)
            quantity = int(item["quantity"])
        except (ValueError, TypeError):
            continue

        if quantity < 1:
            continue

        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item["name"]
                },
                "unit_amount": unit_amount
            },
            "quantity": quantity
        })

    if not line_items:
        return jsonify({"error": "No valid items in cart."}), 400
    print("Creating Stripe session with line_items:", line_items)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=url_for("cart.success", _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for("cart.cancel", _external=True)
        )
        # Return the Stripe session ID for frontend to initiate checkout
        return jsonify({"id": checkout_session.id})

    except Exception as e:
        return jsonify(error=str(e)), 403

@cart_bp.route("/success")
@login_required
def success():
    """
    Success page after payment.
    - Create order and order items from session cart.
    - Send order confirmation email.
    - Clear the cart from session.
    - Render the success template.
    """

    cart = session.get('cart', {})

    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for('products.products'))

    # Calculate total order price
    total = 0
    for item in cart.values():
        total += float(item['price']) * item['quantity']

    # Create a new order record
    new_order = Order(user_id = current_user.id, total=total)
    db.session.add(new_order)
    db.session.commit()

    # Add order items linked to this order
    for product_id, item in cart.items():
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=int(product_id),  # agora está correto
            quantity=item['quantity'],
            price=float(item['price'])  # converter para float se estiver como string
        )
        db.session.add(order_item)

    db.session.commit()

    # Clear the cart session data
    session["cart"] = {}

    flash("Order completed successfully!")

    # Send confirmation email (can be async if desired)
    send_order_confirmation_email(current_user, new_order)

    return render_template("success.html", order=new_order)


@cart_bp.route("/cancel")
def cancel():
    """
    Rendered when user cancels Stripe checkout.
    """

    return render_template("cancel.html")
