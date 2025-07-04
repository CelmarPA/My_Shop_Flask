from decimal import Decimal
from extensions import db
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    # These imports are only used for type hints during static analysis.
    # Prevents circular imports at runtime.
    from .order import Review


class Products(db.Model):
    """
    SRepresents a product available in the online store.

    Attributes:
        id (int): Primary key of the product.
        name (str): Name of the product.
        price (Decimal): Product price stored using fixed-point precision (2 decimal places).
        description (str): Description of the product.
        img_url (str): Path or URL to the product's image.
        quantity (int): Available quantity in stock.
        reviews (List[Review]): List of reviews associated with this product.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    img_url: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="product")

    def to_dict(self):
        """
        Converts the product instance into a dictionary.

        Useful for JSON serialization or API responses.

        :return: (dict) A dictionary containing product fields
        """

        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
