from extensions import db
from flask_login import UserMixin
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .order import Order, Review


class User(UserMixin, db.Model):
    """
    Represents a user of the system.

    Inherits from Flask-Login's UserMixin to enable authentication features.

    Attributes:
        id (int): Primary key.
        name (str): Full name of the user.
        email (str): Unique email address for login.
        cpf (str, optional): Brazilian CPF document number. Must be unique if present.
        rg (str, optional): Brazilian RG document number. Must be unique if present.
        user_data (dict, optional): JSON field for storing additional info such as address, phone, etc.
        password (str): Hashed password for authentication.
        orders (List[Order]): List of orders placed by this user.
        reviews (List[Review]): List of product reviews submitted by this user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    cpf: Mapped[str] = mapped_column(unique=True, nullable=True)
    rg: Mapped[str] = mapped_column(unique=True, nullable=True)
    user_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    password: Mapped[str] = mapped_column(nullable=False)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates = "user")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="user")
