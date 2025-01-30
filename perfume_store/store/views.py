# store/views.py
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .supabase_config import supabase
import random
from django.core.paginator import Paginator
import stripe
import json
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .utils import send_order_confirmation_emails
from django.core.exceptions import ValidationError
from stripe.error import StripeError

stripe.api_key = settings.STRIPE_SECRET_KEY

class HomeView(TemplateView):
    template_name = 'store/home.html'
    
    def get_products(self, table_name, limit=4):
        try:
            response = supabase.table(table_name).select("*").execute()
            products = response.data
            
            if not products:
                print(f"No products found in {table_name}")
                return []
                
            selected_products = random.sample(products, min(limit, len(products)))
            
            return [{
                'id': product['id'],
                'name': product['product'],
                'price': product['price'],
                'brand': product['brand'],
                'image': product['image'],
                'category': table_name
            } for product in selected_products]
        except Exception as e:
            print(f"Error fetching {table_name}: {str(e)}")
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the requested category from URL parameters, default to 'Gemstones'
        category = self.request.GET.get('category', 'Gemstones')
        
        # Get products only for the selected category
        context['products'] = self.get_products(category)
        context['current_category'] = category

        # Get gift sets with same format and limit as products
        try:
            gift_sets_data = supabase.table('Gift sets').select("*").execute()
            if gift_sets_data.data:
                selected_gifts = random.sample(gift_sets_data.data, min(4, len(gift_sets_data.data)))
                context['gift_sets'] = [{
                    'id': gift['id'],
                    'name': gift['product'],  # Assuming the column name is 'product'
                    'price': gift['price'],
                    'brand': gift['brand'],
                    'image': gift['image']
                } for gift in selected_gifts]
            else:
                context['gift_sets'] = []
        except Exception as e:
            print(f"Error fetching gift sets: {str(e)}")
            context['gift_sets'] = []
        
        return context
    
class ShopView(TemplateView):
    template_name = 'store/shop.html'
    products_per_page = 9
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_category = self.request.GET.get('category', 'all')
        
        # Get products from all categories
        products = []
        tables = ['Gemstones', 'Jewellery', 'Perfume', 'Kids', 'Gift sets']
        
        # If 'all' is selected, get from all tables
        if selected_category.lower() == 'all':
            for table in tables:
                try:
                    response = supabase.table(table).select("*").execute()
                    if response.data:
                        for item in response.data:
                            products.append({
                                'id': item['id'],
                                'name': item['product'],
                                'price': item['price'],
                                'image': item['image'],
                                'category': table
                            })
                except Exception as e:
                    print(f"Error fetching {table}: {str(e)}")
        else:
            # Get products from selected category only
            try:
                response = supabase.table(selected_category).select("*").execute()
                if response.data:
                    products = [{
                        'id': item['id'],
                        'name': item['product'],
                        'price': item['price'],
                        'image': item['image'],
                        'category': selected_category
                    } for item in response.data]
            except Exception as e:
                print(f"Error fetching {selected_category}: {str(e)}")

        # Shuffle products
        random.shuffle(products)
        
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(products, self.products_per_page)
        products_page = paginator.get_page(page)
        
        context['products'] = products_page
        context['selected_category'] = selected_category
        return context
    
from django.http import JsonResponse

class CartView(TemplateView):
    template_name = 'store/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context
    
class SingleProductView(TemplateView):
    template_name = 'store/single_product.html'
    
    def get_products(self, table_name, limit=4):
        try:
            response = supabase.table(table_name).select("*").execute()
            products = response.data
            selected_products = random.sample(products, min(limit, len(products)))
            return [{
                'id': product['id'],
                'name': product['product'],
                'price': product['price'],
                'brand': product['brand'],
                'image': product['image'],
                'category': table_name
            } for product in selected_products]
        except Exception as e:
            print(f"Error fetching {table_name}: {str(e)}")
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        category = self.kwargs.get('category')
        
        try:
            response = supabase.table(category).select("*").eq('id', product_id).execute()
            if response.data:
                product = response.data[0]
                context['product'] = {
                    'id': product['id'],
                    'name': product['product'],
                    'price': product['price'],
                    'brand': product['brand'],
                    'image': product['image'],
                    'image2': product.get('image2', product['image']),  # Fallback to main image
                    'image3': product.get('image3', product['image']),  # Fallback to main image
                    'description': product.get('description', 'No description available.'),
                    'category': category
                }
                
                # Get trending products
                context['trending_products'] = self.get_products(category)
                
        except Exception as e:
            print(f"Error fetching product: {str(e)}")
            
        return context
    
import json
    
@method_decorator(csrf_exempt, name='dispatch')
class CheckoutView(View):
    def post(self, request, *args, **kwargs):
        try:
            cart_data = json.loads(request.body)
            cart = cart_data.get('cart', [])
            subtotal = float(cart_data.get('total', 0))
            
            # Calculate shipping
            shipping_cost = 0 if subtotal > 15 else 4.99
            total = subtotal + shipping_cost

            line_items = [
                {
                    'price_data': {
                        'currency': 'gbp',
                        'unit_amount': int(float(item['price']) * 100),
                        'product_data': {
                            'name': item['name'],
                            'images': [item['image']],
                        },
                    },
                    'quantity': item['quantity'] or 1,
                } for item in cart
            ]

            # Add shipping as a line item
            if shipping_cost > 0:
                line_items.append({
                    'price_data': {
                        'currency': 'gbp',
                        'unit_amount': int(shipping_cost * 100),
                        'product_data': {
                            'name': 'Shipping',
                        },
                    },
                    'quantity': 1,
                })

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(reverse('store:success')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('store:cart')),
                shipping_address_collection={
                    'allowed_countries': ['GB'],
                },
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
class StripeWebhookView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            if event.type == 'checkout.session.completed':
                session = event.data.object
                
                # Retrieve session with line items
                session_with_items = stripe.checkout.Session.retrieve(
                    session.id,
                    expand=['line_items']
                )
                
                # Send confirmation emails
                send_order_confirmation_emails(session_with_items)
                
            return HttpResponse(status=200)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return HttpResponse(status=400)
        
class SuccessView(TemplateView):
    template_name = 'store/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can handle post-payment actions here
        return context