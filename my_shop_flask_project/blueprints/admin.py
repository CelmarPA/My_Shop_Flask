from flask import Blueprint, render_template, request, redirect, url_for, flash
from forms.add_product_form import AddProductForm
from forms.edit_product_form import EditProductForm
from models.order import Order
from models.product import Products
from extensions import db
from utils.validators import admin_required


# Create a Blueprint for admin routes, prefixing all URLs with /admin
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/orders", methods=["GET", "POST"])
@admin_required
def admin_orders():
    """
    Admin view for listing and managing all orders.
    GET: Displays orders grouped by status.
    POST: Updates the status of a specific order.

    Access restricted to admin users via @admin_required decorator
    """

    # Query all orders, ordered by most recent date first
    orders = Order.query.order_by(Order.date.desc()).all()

    if request.method == "POST":
        # Extract order_id and new status from submitted form
        order_id = request.form.get("order_id")
        new_status = request.form.get("status")

        # Find the order by ID
        order = Order.query.get(order_id)

        if order:
            # Update order status and save to DB
            order.status = new_status
            db.session.commit()
            flash(f"Order #{order.id} status updated to {new_status}.", "success")
        else:
            flash("Order not found.", "danger")

        # Redirect back to orders page after POST
        return redirect(url_for("admin.admin_orders"))

    # Group orders by status for display
    orders_by_status = {}

    for order in orders:
        status = order.status.capitalize() if order.status else "Processing"

        if status not in orders_by_status:
            orders_by_status[status] = []

        orders_by_status[status].append(order)

    # Define the list of statuses to show in the UI, in desired order
    statuses = ['Processing', 'Shipped', 'Delivered']

    return render_template('admin_orders.html', orders_by_status=orders_by_status, statuses=statuses)


@admin_bp.route("/orders/<int:order_id>")
@admin_required
def order_detail(order_id):
    """
    Displays detailed information about a specific order.
    The order and its related user are passed to the template.

    :param order_id: (int) the order id
    """
    # Retrieve the order by ID or return 404 if not found
    order = db.get_or_404(Order, order_id)

    # Get the user who placed the order
    user = order.user

    return render_template("order_detail.html", order=order, user=user)


@admin_bp.route("/admin/products/add", methods=["GET", "POST"])
@admin_required
def add_product():
    """
    View to add a new product to the store.
    Uses AddProductForm to validate inputs.
    On successful submission, saves the product to the database.
    """

    form = AddProductForm()

    if form.validate_on_submit():
        # Create a new product instance with data from the form
        new_product = Products(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            img_url=form.img_url.data,
            quantity=form.quantity.data
        )

        # Add and commit the new product to the DB
        db.session.add(new_product)
        db.session.commit()

        flash(f"Product '{new_product.name}' added successfully!", "success")

        # Redirect to the same page (could redirect elsewhere if desired)
        return redirect(url_for("admin.add_product"))

    # Render the form template for GET or if validation fails
    return render_template("add_product.html", form=form)


@admin_bp.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    """
    Edit an existing product identified by product_id.
    Pre-fills the form with existing product data.
    On POST, validates and updates the product in the database.
    :param product_id: (int) product id
    """

    # Get product or 404 if not found
    product = Products.query.get_or_404(product_id)

    # Populate form with product data
    form = EditProductForm(obj=product)

    if form.validate_on_submit():
        # Update product fields with form data
        product.name = form.name.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.img_url = form.img_url.data
        product.description = form.description.data

        # Commit changes to the database
        db.session.commit()

        flash(f"Product '{product.name}' updated successfully!", "success")

        # Redirect to the product management page after editing
        return redirect(url_for("admin.manage_products"))

    else:
        # If form submission was POST but validation failed, print errors
        if request.method == "POST":
            print("Form did not validate:")
            print(form.errors)

    # Render edit product template with form and current product inf
    return render_template("edit_product.html", form=form, product=product)


@admin_bp.route("/manage_products")
@admin_required
def manage_products():
    """
    View to display and manage all products.
    Lists all products for the admin with options to edit or delete.
    """

    products = Products.query.all()
    return render_template("manage_products.html", products=products)


@admin_bp.route("/delete_product/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    """
    Deletes a product by its ID.
    Only accessible via POST to prevent accidental deletions.

    :param product_id: (int) product id
    """

    # Get product or 404 if not found
    product = Products.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    flash(f"Product '{product.name}' deleted.", "danger")

    # Redirect back to the manage products page
    return redirect(url_for("admin.manage_products"))
