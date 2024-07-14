from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review, Order, OrderStatus, UserProfile, Category, Author, Favorite, About
from .forms import ReviewForm, OrderForm, UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Book, Category, Author
from django.db.models import Count

def index(request):
    featured_books = Book.objects.filter(featured=True)
    popular_books = Book.objects.annotate(review_count=Count('reviews')).order_by('-review_count')[:5]
    all_books = Book.objects.all()
    about = About.objects.first()
    category_id = request.GET.get('category')
    author_id = request.GET.get('author')
    filtered_books = all_books
    if category_id:
        filtered_books = filtered_books.filter(category_id=category_id)
    elif author_id:
        filtered_books = filtered_books.filter(author_id=author_id)
    categories = Category.objects.all()
    authors = Author.objects.all()

    # Создаем объект Paginator для отфильтрованных книг
    paginator = Paginator(filtered_books, 10)  # По 10 книг на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_books': featured_books,
        'popular_books': popular_books,
        'filtered_books': page_obj,  # Передаем объект страницы в контекст
        'categories': categories,
        'authors': authors,
        'about': about,
    }

    # Проверка на мобильное устройство
    user_agent = request.META['HTTP_USER_AGENT']
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        return render(request, 'index.html', context)
    else:
        return render(request, 'index.html', context)



# views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import Book, Category, Author

def book_list(request):
    all_books = Book.objects.all()

    # Apply filtering
    category_id = request.GET.get('category')
    author_id = request.GET.get('author')
    filtered_books = all_books
    if category_id:
        filtered_books = filtered_books.filter(category_id=category_id)
    if author_id:
        filtered_books = filtered_books.filter(author_id=author_id)

    # Apply sorting
    sort_criteria = request.GET.get('sort')
    if sort_criteria == 'newest':
        filtered_books = filtered_books.order_by('-id')
    elif sort_criteria == 'cheaper':
        filtered_books = filtered_books.order_by('price')
    elif sort_criteria == 'expensive':
        filtered_books = filtered_books.order_by('-price')
    elif sort_criteria == 'reviews':
        filtered_books = filtered_books.order_by('-reviews')
    else:
        filtered_books = filtered_books.order_by('title')

    paginator = Paginator(filtered_books, 5)
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    categories = Category.objects.all()
    authors = Author.objects.all()

    context = {'books': books, 'categories': categories, 'authors': authors}

    user_agent = request.META['HTTP_USER_AGENT']
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        return render(request, 'MobileTemplates/mobile_book_list.html', context)
    else:
        return render(request, 'book_list.html', context)



from django.db.models import Avg

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = Review.objects.filter(book=book)
    user_review = Review.objects.filter(book=book, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=user_review)  # Передаем instance=user_review, чтобы обновить существующий отзыв
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            # Обновление рейтинга книги после добавления нового отзыва
            book_rating = reviews.aggregate(Avg('stars'))
            book.rating = book_rating['stars__avg'] if book_rating['stars__avg'] is not None else 0
            book.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = ReviewForm(instance=user_review)

    return render(request, 'book_detail.html', {'book': book, 'reviews': reviews, 'form': form})

from django.shortcuts import render
from .models import Book

def book_search(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    return render(request, 'book_search.html', {'books': books})

# views.py
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Book

def book_search_ajax(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    html = render_to_string('search_results_partial.html', {'books': books})
    return JsonResponse({'html': html})

def category_books(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    books = Book.objects.filter(category=category)
    context = {
        'category': category,
        'books': books,
    }
    return render(request, 'category_books.html', context)

def author_books(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    books = Book.objects.filter(author=author)
    context = {
        'author': author,
        'books': books,
    }
    return render(request, 'author_books.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Book, Order, OrderStatus, PaymentSystem
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def order_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    payment_systems = PaymentSystem.objects.all()
    try:
        order_status = OrderStatus.objects.get(status='Yetkazilmoqda')
    except OrderStatus.DoesNotExist:
        order_status = OrderStatus.objects.create(status='Yetkazilmoqda')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        selected_payment_system_id = request.POST.get('payment_system')
        if form.is_valid() and selected_payment_system_id:
            quantity = form.cleaned_data['quantity']
            order = form.save(commit=False)
            order.user = request.user
            order.book = book
            order.status = order_status
            order.order_time = timezone.now()
            order.quantity = quantity
            order.payment_system = get_object_or_404(PaymentSystem, id=selected_payment_system_id)
            
            # Calculate total amount with discount if applicable
            if book.discount_price:
                total_amount = book.discount_price * quantity
            else:
                total_amount = book.price * quantity
            
            order.save()
            
            return redirect('payment_page', order_id=order.pk)
    else:
        form = OrderForm()
    
    return render(request, 'order_book.html', {
        'book': book,
        'form': form,
        'payment_systems': payment_systems,
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, PaymentSystem
from django.contrib.auth.decorators import login_required

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment_system = order.payment_system
    
    # Calculate total amount based on order details
    if order.book.discount_price:
        total_amount = order.book.discount_price * order.quantity
    else:
        total_amount = order.book.price * order.quantity
    
    if request.method == 'POST':
        # Handle payment confirmation logic here
        send_payment_confirmation(order, payment_system)
        return redirect('payment_confirmation', order_id=order.pk)
    
    return render(request, 'payment_page.html', {'order': order, 'payment_system': payment_system, 'total_amount': total_amount})

def send_payment_confirmation(order, payment_system):
    telegram_bot_token = settings.TELEGRAM_BOT_TOKEN
    telegram_chat_id = settings.TELEGRAM_CHAT_ID
    total_amount = order.book.discount_price * order.quantity if order.book.discount_price else order.book.price * order.quantity
    message_text = (
        f"Yangi zakaz keldi raqami: {order.id}\n"
        f"Zakaz beruvchi nomi: {order.user}\n"
        f"Zakaz qilinga kitob: {order.book.title}\n"
        f"Miqdri: {order.quantity}\n"
        f"Manzili: {order.address}\n"
        f"Telefon raqami: {order.phone_number}\n"
        f"Tolov turi: {payment_system.name}\n"
        f"Shu kartaga toladi: {payment_system.number}\n"
        f"Umumiy to'lov summasi: ${total_amount}"
    )
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {
        "chat_id": telegram_chat_id,
        "text": message_text
    }
    requests.post(url, data=data)


@login_required
def payment_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment_confirmation.html', {'order': order})


@login_required
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_status.html', {'order': order})

@login_required
def all_orders(request):
    all_orders_list = Order.objects.filter(user=request.user).order_by('-order_time')
    paginator = Paginator(all_orders_list, 1)  # Показывать по 10 заказов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_orders.html', {'page_obj': page_obj})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile = UserProfile(user=user)  # Removed balance=0
            user_profile.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')


from django.shortcuts import get_object_or_404, redirect
from .models import Favorite

@login_required
def add_to_favorite(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    # Проверяем, существует ли книга в избранном пользователя
    if not Favorite.objects.filter(user=request.user, book=book).exists():
        # Если книги еще нет в избранном пользователя, создаем новую запись
        Favorite.objects.create(user=request.user, book=book)

    return redirect('index')  # или перенаправьте на другую страницу

@login_required
def remove_from_favorite(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    Favorite.objects.filter(user=request.user, book=book).delete()
    return redirect('favorite_books')  # или куда-то еще

@login_required
def favorite_books(request):
    favorite_books = Favorite.objects.filter(user=request.user)
    context = {
        'favorite_books': favorite_books
    }
    return render(request, 'favorite_books.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum  # Импортируем Sum из django.db.models
from .models import Order, UserProfile

@login_required
def profile(request):
    user = request.user
    total_spent = Order.objects.filter(user=user, status__status='Yatkazildi').aggregate(total_spent=Sum('book__price'))['total_spent'] or 0
    return render(request, 'profile.html', {'user': user, 'total_spent': total_spent})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import UserProfile  # Import the UserProfile model

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)  # Get or create the user's profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'edit_profile.html', {'form': form})



# views.py
import csv
import requests
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.contrib import messages
from .forms import CSVUploadForm
from .models import Book, Author, Category

def bulk_upload_books(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    author, created = Author.objects.get_or_create(name=row['Author'])
                    category, created = Category.objects.get_or_create(name=row['Category'])

                    book = Book(
                        title=row['Title'],
                        description=row['Description'],
                        author=author,
                        category=category,
                        price=row['Price'],
                        discount_price=row.get('Discount Price'),
                        featured=row.get('Featured', False),
                        popular=row.get('Popular', False),
                    )
                    
                    # Загрузка изображения по URL
                    cover_image_url = row.get('Cover Image')
                    if cover_image_url:
                        response = requests.get(cover_image_url)
                        if response.status_code == 200:
                            file_name = cover_image_url.split("/")[-1]
                            book.cover_image.save(file_name, ContentFile(response.content), save=False)
                    
                    book.save()
                messages.success(request, 'Books uploaded successfully!')
            except Exception as e:
                messages.error(request, f"Error uploading books: {e}")
        else:
            messages.error(request, "Invalid form")
    else:
        form = CSVUploadForm()
    return render(request, 'bulk_upload.html', {'form': form})


from django.shortcuts import render
from django.db.models import Count, Avg, Sum
from django.contrib.auth.models import User
from .models import Book, Author, Category, Order, UserProfile, Review, OrderStatus
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def combined_stats_view(request):
    # Book statistics
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()
    avg_rating = Review.objects.aggregate(Avg('stars'))['stars__avg']
    total_reviews = Review.objects.count()
    avg_price = Book.objects.aggregate(Avg('price'))['price__avg']

    # Calculate total sales for 'Yatkazildi' status
    accepted_status = OrderStatus.objects.get(status='Yatkazildi')
    total_sales = Order.objects.filter(status=accepted_status).aggregate(total_sales=Sum('book__price'))['total_sales']

    # Top selling books, authors, categories
    top_selling_books = Book.objects.annotate(total_sold=Count('order')).order_by('-total_sold')[:5]
    top_authors = Author.objects.annotate(total_books=Count('book')).order_by('-total_books')[:5]
    top_categories = Category.objects.annotate(total_books=Count('book')).order_by('-total_books')[:5]

    # User spending
    filter_by = request.GET.get('filter_by')
    search_query = request.GET.get('search_query', '')

    user_spending = User.objects.annotate(total_spent=Sum('order__book__price'))

    if filter_by == 'highest':
        user_spending = user_spending.order_by('-total_spent')
    elif filter_by == 'lowest':
        user_spending = user_spending.order_by('total_spent')

    if search_query:
        user_spending = user_spending.filter(username__icontains=search_query)

    context = {
        'total_books': total_books,
        'total_authors': total_authors,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'avg_price': avg_price,
        'total_sales': total_sales if total_sales else 0,  # Ensure total_sales is not None
        'top_selling_books': top_selling_books,
        'top_authors': top_authors,
        'top_categories': top_categories,
        'user_spending': user_spending,
        'filter_by': filter_by,
        'search_query': search_query,
    }

    return render(request, 'combined_stats.html', context)


def about(request):
    about = About.objects.first()  # Получаем первый объект About, если он есть
     # Получаем список всех навыков
    return render(request, 'about.html', {'about': about})

from django.shortcuts import render

def spin_wheel(request):
    return render(request, 'spin_wheel.html')
