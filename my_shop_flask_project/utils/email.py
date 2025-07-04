from flask_mail import Message


def send_order_confirmation_email(user, order):
    """
    Sends an order confirmation email to the user after a successful purchase.

    :param user: (User) The user who placed the order.
    :param order: (Order) The order instance containing items and total.

    The email includes:
        - Order ID and date
        - Order status
        - List of items purchased with quantities and prices
        - Total amount
    """

    # Import mail instance from app (assuming it's initialized in your app factory)
    from app import mail

    # Build a human-readable list of purchased items
    items_text = "\n".join([
        f"- {item.quantity} x {item.product.name} (${item.price:.2f})"
        for item in order.items
    ])

    # Create the email message
    msg = Message(
        subject="Your Order Confirmation",
        recipients=[user.email],
        body=f"""
            Hi {user.name},

            Thanks for your purchase! 🎉

            Order ID: #{order.id}
            Date: {order.date.strftime('%d/%m/%Y %H:%M')}
            Status: {order.status}

            Items:
            {items_text}

            Total: ${order.total:.2f}

            We'll notify you when your order is shipped.

            Best regards,
            My Shop Team
        """
    )

    # Send the email
    mail.send(msg)
