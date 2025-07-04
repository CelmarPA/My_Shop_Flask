# utils/validators.py

from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps
from wtforms.validators import ValidationError


def admin_required(f):
    """
    Route decorator that restricts access to administrators only.

    This implementation assumes the admin user has an ID of 1.
    If a non-admin user attempts to access the decorated route,
    they are redirected to the home page and shown an error message.

    :param f: (function) The route function to decorate.

    :return:  (function) The decorated route or a redirect response if unauthorized.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if current user is admin (id == 1)
        if current_user.id != 1:
            flash("Access denied: admin only.", "error")
            return redirect(url_for("main.home"))

        # Proceed to the decorated route function if admin
        return f(*args, **kwargs)

    return decorated_function


def validate_cpf_unique(form, field):
    """
    WTForms validator to ensure that the provided CPF is unique.

    Raises a ValidationError if the CPF is already registered in the system.

    :param form: (FlaskForm) The form being validated.
    :param field: (Field) The field containing the CPF value.

    :raises ValidationError: If the CPF is already used by another user.:
    """

    from models.user import User

    user = User.query.filter_by(cpf=field.data).first()

    if user:
        raise ValidationError("CPF already registered.")

def validate_rg_unique(form, field):
    """
    WTForms validator to ensure that the provided RG is unique.

    Raises a ValidationError if the RG is already registered in the system.

    Raises:
        ValidationError: If the RG is already used by another user.

    :param form: (FlaskForm) The form being validated.
    :param field: (Field) The field containing the RG value.

    :raises ValidationError: If the RG is already used by another user.
    """

    from models.user import User

    user = User.query.filter_by(rg=field.data).first()

    if user:
        raise ValidationError("RG already registered.")
