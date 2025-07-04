from datetime import date
from extensions import db
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.user_data import UserData
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select


current_year = date.today().year

# Create blueprint for authentication-related routes
auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration route.

    - Redirects to home if user already logged in.
    - On POST:
        * Checks if email is already registered, flashes message if so.
        * Creates a new User with hashed password.
        * Commits new user to the database.
        * Redirects to home after registration.
    - On GET:
        * Renders registration template.
    """

    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = db.session.query(User).filter_by(email=form.email.data).first()
        if existing_user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("auth.register"))

        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.")

        return redirect(url_for("auth.login"))

    return render_template("register.html", current_year = current_year, form = form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    User login route.

    - Redirects to home if already logged in.
    - On POST:
        * Uses LoginForm for validation.
        * Retrieves user by email.
        * Checks hashed password.
        * Logs in user if valid.
        * Shows flash message for errors.
    - On GET:
        * Renders login template with form.
    """

    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.execute(select(User).filter_by(email=form.email.data)).scalars().first()

        if not user:
            flash("That email does not exist, please try again.")
            return render_template("login.html", form=form)

        if check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("main.home"))
        else:
            flash("Password incorrect, please try again.")
            return render_template("login.html", form=form)

    return render_template("login.html", form=form, logged_in=current_user.is_authenticated, current_year=current_year)


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Logs out the current authenticated user and redirects to the home page.
    """

    logout_user()

    return redirect(url_for("main.home"))

@auth_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """
    Edit profile route allowing users to update their additional data and documents (CPF, RG).

    Uses WTForms form for address/phone fields.

    POST:
        - Validates form data.
        - Checks if CPF and RG (manually input) are unique across users except current user.
        - Saves CPF and RG only if not already set.
        - Updates user_data JSON column with address and phone.
        - Commits to DB and flashes success message.

    GET:
        - Pre-fills form fields with existing user data.
        - Passes CPF and RG to template separately since they're not part of the WTForms.

    :return: Renders edit_profile.html with form and data
    """

    form = UserData()

    if form.validate_on_submit():
        cpf_input = request.form.get("cpf") or current_user.cpf
        rg_input = request.form.get("rg") or current_user.rg

        # Check if CPF is already registered to a different user
        if cpf_input:
            cpf_exists = db.session.query(User).filter(User.cpf == cpf_input, User.id != current_user.id).first()
            if cpf_exists:
                flash("CPF already registered to another user.", "error")
                return render_template("edit_profile.html", form=form)

        # Check if RG is already registered to a different user
        if rg_input:
            rg_exists = db.session.query(User).filter(User.rg == rg_input, User.id != current_user.id).first()
            if rg_exists:
                flash("RG already registered to another user.", "error")
                return render_template("edit_profile.html", form=form)

        # Save CPF and RG only if not already present on current user
        if not current_user.cpf and cpf_input:
            current_user.cpf = cpf_input

        if not current_user.rg and rg_input:
            current_user.rg = rg_input

        # Update user_data JSON with other form fields
        current_user.user_data = {
            "phone": form.phone.data,
            "street": form.street.data,
            "number": form.number.data,
            "city": form.city.data,
            "state": form.state.data,
            "zip_code": form.zip_code.data,
            "country": form.country.data
        }

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("orders.account"))

    # GET request: pre-fill the form with existing user data if available
    if request.method == "GET":
       if current_user.user_data:
            user_data = current_user.user_data
            form.phone.data = user_data.get("phone", "")
            form.street.data = user_data.get("street", "")
            form.number.data = user_data.get("number", "")
            form.city.data = user_data.get("city", "")
            form.state.data = user_data.get("state", "")
            form.zip_code.data = user_data.get("zip_code", "")
            form.country.data = user_data.get("country", "")

    return render_template("edit_profile.html", form=form)
