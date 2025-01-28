# store/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def send_order_confirmation_emails(session_data):
    customer_email = session_data.customer_details.email
    order_items = session_data.line_items.data if hasattr(session_data, 'line_items') else []
    
    # Calculate subtotal and shipping
    subtotal = sum(item.amount_total / 100 for item in order_items if 'Shipping' not in item.description)
    shipping_cost = 4.99 if subtotal < 15 else 0
    
    # Retrieve line items with expanded price data
    expanded_items = []
    for item in order_items:
        if 'Shipping' not in item.description:
            try:
                # Get price details including image
                price = stripe.Price.retrieve(
                    item.price.id,
                    expand=['product']
                )
                expanded_items.append({
                    'description': item.description,
                    'quantity': item.quantity,
                    'amount_total': item.amount_total / 100,
                    'image': price.product.images[0] if price.product.images else None
                })
            except Exception as e:
                print(f"Error retrieving price details: {str(e)}")
                expanded_items.append({
                    'description': item.description,
                    'quantity': item.quantity,
                    'amount_total': item.amount_total / 100,
                    'image': None
                })

    order_details = {
        'customer_name': session_data.customer_details.name,
        'shipping_address': session_data.shipping_details.address,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total_amount': subtotal + shipping_cost,
        'order_id': session_data.id,
        'items': expanded_items
    }

    # Customer email
    customer_subject = 'Your Gift Outlet Order Confirmation'
    customer_message = render_to_string('store/emails/customer_order_confirmation.html', {
        'order': order_details,
        'is_customer': True
    })

    send_mail(
        customer_subject,
        '',  # Plain text version
        settings.DEFAULT_FROM_EMAIL,
        [customer_email],
        html_message=customer_message,
        fail_silently=False,
    )

    # Business email
    business_subject = f'New Order Received - #{session_data.id}'
    business_message = render_to_string('store/emails/business_order_notification.html', {
        'order': order_details,
        'is_customer': False
    })

    send_mail(
        business_subject,
        '',  # Plain text version
        settings.DEFAULT_FROM_EMAIL,
        [settings.BUSINESS_EMAIL],
        html_message=business_message,
        fail_silently=False,
    )