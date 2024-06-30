from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/', views.book_list, name='book_list'),
    path('order/<int:pk>/', views.order_book, name='order_book'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('order/<int:pk>/status/', views.order_status, name='order_status'),
    path('orders/', views.all_orders, name='all_orders'),
    path('add_to_favorite/<int:book_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('remove_from_favorite/<int:book_id>/', views.remove_from_favorite, name='remove_from_favorite'),
    path('favorite_books/', views.favorite_books, name='favorite_books'),
    path('search/', views.book_search, name='book_search'),
    path('search/ajax/', views.book_search_ajax, name='book_search_ajax'),
    path('category/<int:category_id>/', views.category_books, name='category_books'),
    path('author/<int:author_id>/', views.author_books, name='author_books'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile/', views.profile, name='profile'),
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('payment_confirmation/<int:order_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('add/', views.bulk_upload_books, name='bulk_upload_books'),
    path('stats/', views.combined_stats_view, name='combined_stats'),
    path('about/', views.about, name='about'),

]