from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class UserData(FlaskForm):
    """
    Form for user profile data (address and contact info).

    Fields:
    - phone: User's phone number (required)
    - street: Street address (required)
    - number: House/building number (required)
    - city: City name (required)
    - state: State or region (required)
    - zip_code: Postal/zip code (required)
    - country: Country name (required)
    """

    phone = StringField(label="Phone Number", validators=[DataRequired()])
    street = StringField(label="Street Address", validators=[DataRequired()])
    number = StringField(label="Number", validators=[DataRequired()])
    city = StringField(label="City", validators=[DataRequired()])
    state = StringField(label="State", validators=[DataRequired()])
    zip_code = StringField(label="Zip Code", validators=[DataRequired()])
    country = StringField(label="Country", validators=[DataRequired()])
