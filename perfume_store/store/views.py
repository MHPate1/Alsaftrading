# store/views.py
from django.views.generic import TemplateView
from .supabase_config import supabase
import random
from django.core.paginator import Paginator

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

class LikedView(TemplateView):
    template_name = 'store/liked.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favorites = self.request.GET.get('favorites', '[]')  # Get favorites from query params
        liked_product_ids = eval(favorites)  # Convert string to list
        liked_products = []
        
        # Get all products from all tables
        tables = ['Gemstones', 'Jewellery', 'Perfume', 'Kids', 'Gift sets']
        
        for table in tables:
            try:
                response = supabase.table(table).select("*").execute()
                if response.data:
                    for item in response.data:
                        # Only add product if its ID is in favorites
                        if str(item['id']) in liked_product_ids:
                            liked_products.append({
                                'id': item['id'],
                                'name': item['product'],
                                'price': item['price'],
                                'brand': item['brand'],
                                'image': item['image'],
                                'category': table
                            })
            except Exception as e:
                print(f"Error fetching {table}: {str(e)}")
        
        context['liked_products'] = liked_products
        return context
    

class CartView(TemplateView):
    template_name = 'store/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context