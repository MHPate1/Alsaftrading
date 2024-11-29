from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('perfume', 'Perfume'),
        ('gemstone', 'Gemstone'),
        ('jewellery', 'Jewellery'),
        ('gift_set', 'Gift Set'),
    ]
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('F', 'Women'),
        ('U', 'Unisex'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    image = models.ImageField(upload_to='products/')
    is_trending = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Review(models.Model):
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} - {self.rating} stars"
