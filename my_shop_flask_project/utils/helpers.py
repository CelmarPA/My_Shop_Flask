# utils/helpers.py

from random import sample
from math import ceil
from models.order import Order


def anonymize_name(name):
    """
    Anonymizes a user's name by partially hiding characters in the first name.

    - Selects the first name (before the first space).
    - Hides approximately 30% of the characters with asterisks (*).
    - Characters to hide are chosen randomly.

    :param name: (str) Full name of the user.
    :return: (str) Anonymized version of the first name.
    Example:
        "Caroline Silva" -> "C*r*line"
    """

    first_name = name.split()[0]

    length = len(first_name)
    num_to_hide = ceil(length * 0.3)

    indices = list(range(length))
    hide_indices = sample(indices, num_to_hide)

    result_chars = []
    for i, ch in enumerate(first_name):
        if i in hide_indices:
            result_chars.append('*')

        else:
            result_chars.append(ch)

    return ''.join(result_chars)


def user_bought_product(user_id: int, product_id: int) -> bool:
    """
    Checks whether a given user has purchased a specific product.

    :param user_id: (int) ID of the user.
    :param product_id: (int) ID of the product.

    :return: (bool) True if the user has ordered the product, False otherwise.
    """

    orders = Order.query.filter_by(user_id=user_id).all()

    for order in orders:
        for item in order.items:
            if item.product_id == product_id:
                return True

    return False


def is_profile_complete(user):
    """
    Verifies whether the user's profile is complete.

    Requirements for a complete profile:
        - CPF and RG must be filled.
        - 'user_data' JSON must contain:
            - phone, street, number, city, state, zip_code, country

    :param user: (User) The current user object.

    :return: (bool) True if all required fields are present, False otherwise.
    """

    required_fields = ["phone", "street", "number", "city", "state", "zip_code", "country"]

    data = user.user_data or {}

    missing_fields = [field for field in required_fields if not data.get(field)]

    if not user.cpf:
        missing_fields.append("cpf")

    if not user.rg:
        missing_fields.append("rg")

    if missing_fields:
        print(f"[DEBUG] Incomplete profile fields: {missing_fields}")
        return False

    return True
