# forms/admin_forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    """
    Form used by admins to add new products to the store.

    Fields:
    - name: Product name (required)
    - price: Product price as string (required, consider validating format separately)
    - description: Product description (required)
    - img_url: URL or filename for product image (required)
    - quantity: Initial stock quantity (required integer)
    - submit: Submit button
    """

    name = StringField(label="Name", validators=[DataRequired()])
    price = StringField(label="Price", validators=[DataRequired()])
    description = StringField(label="Description", validators=[DataRequired()])
    img_url = StringField(label="Image URL", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Add Product")
