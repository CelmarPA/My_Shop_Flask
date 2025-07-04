from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegisterForm(FlaskForm):
    """
    User registration form.

    Fields:
    - name: User's full name (required, 2 to 150 characters)
    - email: User's email address (required, must be valid email format)
    - password: Password (required, minimum 6 characters)
    - confirm_password: Must match the password field (required)
    - submit: Submit button to register
    """
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
