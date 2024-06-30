from django.contrib import admin
from .models import Category, Author, Book, Review, Order, OrderStatus, UserProfile, PaymentSystem, About

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price')
    list_filter = ('category', 'author')
    search_fields = ('title', 'author__name')
    # prepopulated_fields = {'slug': ('title',)}  # Убедитесь, что поле slug существует в модели Book, если нет - удалите эту строку

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book')
    search_fields = ('user__username', 'book__title')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'status', 'order_time', 'quantity', 'address', 'phone_number', 'payment_system')
    list_filter = ('status', 'order_time', 'payment_system')
    search_fields = ('user__username', 'book__title', 'address', 'phone_number')

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('status',)
    search_fields = ('status',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number', 'address')

@admin.register(PaymentSystem)
class PaymentSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'photo')
    search_fields = ('name', 'number')


admin.site.register(About)