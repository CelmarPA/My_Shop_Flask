from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    """
    Form for user login.

    Fields:
    - email: User email address (required, must be valid email format)
    - password: User password (required)
    - submit: Submit button to log in
    """

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
