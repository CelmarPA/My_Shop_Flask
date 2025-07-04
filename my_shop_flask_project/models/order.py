from datetime import datetime, timezone
from extensions import db
from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    # These imports are only used for type hints during static analysis (e.g., with tools like mypy or IDEs).
    # They are not executed at runtime to avoid circular import issues.
    from .user import User
    from .product import Products


class Order(db.Model):
    """
    Represents a customer order in the system.

    Attributes:
        id (int): Primary key of the order.
        date (datetime): Date and time the order was placed (UTC).
        total (float): Total monetary value of the order.
        status (str): Current status of the order (e.g., 'Processing', 'Shipped', 'Delivered').
        user_id (int): Foreign key referencing the user who placed the order.
        user (User): Relationship to the User object.
        items (List[OrderItem]): List of OrderItem objects associated with this order.
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    total: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="Processing", nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates = "orders")

    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")


class OrderItem(db.Model):

    """
    Represents an individual item in a customer order.

    Attributes:
        id (int): Primary key of the order item.
        order_id (int): Foreign key referencing the parent order.
        product_id (int): Foreign key referencing the product purchased.
        quantity (int): Quantity of the product ordered.
        price (float): Price of the product at the time of the order.
        order (Order): Relationship to the parent Order object.
        product (Products): Relationship to the purchased Product.
    """

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")

    product: Mapped["Products"] = relationship("Products")


class Review(db.Model):
    """
    Represents a user-submitted review for a product.

    Attributes:
        id (int): Primary key of the review.
        rating (int): Rating given to the product (e.g., 1 to 5).
        comment (str): Optional text comment left by the user.
        date (datetime): Timestamp when the review was submitted (UTC).
        user_id (int): Foreign key referencing the user who wrote the review.
        product_id (int): Foreign key referencing the reviewed product.
        user (User): Relationship to the User who submitted the review.
        product (Products): Relationship to the reviewed Product.

    Constraints:
        A user can only submit one review per product (enforced via unique constraint on user_id + product_id).
    """

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    product: Mapped["Products"] = relationship("Products", back_populates="reviews")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='uix_user_product'),
    )
