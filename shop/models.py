from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# models.py
from django.db import models
from django.db import models
from django.db.models import Avg

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)


    def __str__(self):
        return self.title

    def average_rating(self):
        avg_rating = self.reviews.aggregate(Avg('stars'))['stars__avg']
        return avg_rating if avg_rating is not None else 0
    
    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    stars = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def save(self, *args, **kwargs):
        if not (1 <= self.stars <= 5):
            raise ValueError('Stars rating must be between 1 and 5')

        super().save(*args, **kwargs)
        self.book.save()  

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.book.save()  

class OrderStatus(models.Model):
    PROCESSING = 'Yetkazilmoqda'
    ACCEPTED = 'Yatkazildi'
    NOT_PAID = 'Tolov qilinmagan'  

    STATUS_CHOICES = [
        (PROCESSING, 'Yetkazilmoqda'),
        (ACCEPTED, 'Yatkazildi'),
        (NOT_PAID, 'Tolov qilinmagan'),  
    ]

    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return self.get_status_display()


class PaymentSystem(models.Model):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=889)
    photo = models.ImageField(upload_to='payment_systems/', blank=True, null=True)  # Поле для фото

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)  
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, default=1)
    address = models.CharField(max_length=255)
    phone_number = PhoneNumberField()
    order_time = models.DateTimeField(auto_now_add=True)
    payment_system = models.ForeignKey(PaymentSystem, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.status.status}"



from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')


class About(models.Model):
    description = models.TextField()

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question


#Telegram bot zakazlarni cheki uchun
    
class Purchase(models.Model):  
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=50)
    payment_receipt = models.CharField(max_length=255, blank=True, null=True)
    order_time = models.DateTimeField(auto_now_add=True)  # Добавляем поле для времени заказа

    def __str__(self):
        return f"Purchase for {self.book.title} by {self.name}"
    

from django.db import models
import re

# Модель Check
class Check(models.Model):
    user_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_proof = models.ImageField(upload_to='payment_proofs/')
    status = models.CharField(max_length=20, default='pending')
    books = models.TextField()  
    city = models.CharField(max_length=100)
    promo_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Check {self.id} - {self.user_id}"


class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    messages_sent = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} ({self.user_id})"


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    usage_limit = models.PositiveIntegerField(default=1)  # Максимальное количество использований
    usage_count = models.PositiveIntegerField(default=0)  # Текущее количество использований

    def __str__(self):
        return self.code

    def is_valid(self):
        return self.usage_count < self.usage_limit

from django.db import models

class Gift(models.Model):
    GIFT_TYPES = [
        ('promo_code', 'Промокод'),
        ('free_book', 'Бесплатная книга'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='gifts/', null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Активен ли подарок
    type = models.CharField(max_length=20, choices=GIFT_TYPES)

    def __str__(self):
        return self.name

class UserGift(models.Model):
    user_id = models.IntegerField()
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)
    date_won = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.gift.name}"

class UserFavorites(models.Model):
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, related_name='favorite_books')

    def __str__(self):
        return f"Favorites of {self.user.username}"