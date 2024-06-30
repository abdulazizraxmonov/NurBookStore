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
        self.book.save()  # Call save() method of the related book instance to update average rating

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.book.save()  # Call save() method of the related book instance to update average rating

class OrderStatus(models.Model):
    PROCESSING = 'Yetkazilmoqda'
    ACCEPTED = 'Yatkazildi'
    NOT_PAID = 'Tolov qilinmagan'  # Новый статус "Не оплачено"

    STATUS_CHOICES = [
        (PROCESSING, 'Yetkazilmoqda'),
        (ACCEPTED, 'Yatkazildi'),
        (NOT_PAID, 'Tolov qilinmagan'),  # Добавляем новый статус
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