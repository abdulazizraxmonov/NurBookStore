import os
import django
from django.core.management.base import BaseCommand
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from shop.models import Book, Purchase, Author, Category, Check, UserFavorites, FAQ, About
from telebot.types import Message
from uuid import uuid4
import re

# Установка настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

# Указание токена вашего бота
TOKEN = '7432959634:AAGGmWyjXYLaXfrVLvg3orQDNkMPKS2oNPM'
ADMIN_CHAT_ID = '661899402'  # Замените на ID чата админа
TELEGRAM_CHANNEL_ID = 'TELEGRAM_CHANNEL_ID'

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Глобальная переменная для хранения данных пользователей
user_data = {}

def list_books(message=None, page=1, page_size=5, chat_id=None, message_id=None):
    try:
        offset = (page - 1) * page_size
        books = Book.objects.all()[offset:offset + page_size]

        if books:
            book_buttons = []
            for book in books:
                button_text = f"{book.title} - {book.price} sum"
                if book.discount_price:
                    button_text += f" (Chegirma: {book.discount_price} sum)"
                button = InlineKeyboardButton(button_text, callback_data=f'show_book_{book.id}')
                book_buttons.append([button])

            pagination_keyboard = []
            if page > 1:
                pagination_keyboard.append(InlineKeyboardButton("⬅️", callback_data=f'books_prev_page_{page-1}'))
            if len(books) == page_size:
                pagination_keyboard.append(InlineKeyboardButton("➡️", callback_data=f'books_next_page_{page+1}'))

            if pagination_keyboard:
                book_buttons.append(pagination_keyboard)

            reply_markup = InlineKeyboardMarkup(book_buttons)

            if chat_id and message_id:
                try:
                    bot.edit_message_text('Kitobni tanlang:', chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
                except telebot.apihelper.ApiTelegramException as e:
                    bot.send_message(chat_id, 'Kitobni tanlang:', reply_markup=reply_markup)
            else:
                bot.send_message(message.chat.id, 'Kitobni tanlang:', reply_markup=reply_markup)
        else:
            error_msg = 'Kitob mavjud emas.'
            if chat_id and message_id:
                try:
                    bot.edit_message_text(error_msg, chat_id=chat_id, message_id=message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    bot.send_message(chat_id, error_msg)
            else:
                bot.send_message(message.chat.id, error_msg)

    except Exception as e:
        error_msg = f"Error listing books: {e}"
        if chat_id and message_id:
            bot.send_message(chat_id, error_msg)
        else:
            bot.send_message(message.chat.id, error_msg)

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

def show_book_details(callback_query):
    book_id = int(callback_query.data.split('_')[-1])
    chat_id = callback_query.message.chat.id
    try:
        book = Book.objects.get(id=book_id)
        final_price = book.get_final_price()
        price_text = f"<s>{book.price} sum</s> {book.discount_price} sum" if book.discount_price else f"{book.price} sum"
        message_text = f"{book.title}\nNarxi: {price_text}\n\nKitob haqida: {book.description}"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Savatga qoshish🛒", callback_data=f'add_to_cart_{book.id}'))
        keyboard.add(InlineKeyboardButton("Yoqtirishlar bolimiga qoshish❤️", callback_data=f'add_to_favorites_{book.id}'))
        keyboard.add(InlineKeyboardButton("⬅️Orqaga qaytish", callback_data='back_to_list'))

        if book.cover_image:
            cover_image_path = book.cover_image.path
            with open(cover_image_path, 'rb') as cover_image_file:
                bot.send_photo(chat_id, cover_image_file, caption=message_text, reply_markup=keyboard, parse_mode='HTML')
        else:
            bot.send_message(chat_id, message_text, reply_markup=keyboard, parse_mode='HTML')
    except ObjectDoesNotExist:
        bot.send_message(chat_id, 'Kitob topilmadi.')
    except Exception as e:
        logger.error(f"Error showing book details: {e}")
        bot.send_message(chat_id, f"Error showing book details: {e}")

def add_to_favorites(callback_query):
    book_id = int(callback_query.data.split('_')[-1])
    chat_id = callback_query.message.chat.id
    try:
        book = Book.objects.get(id=book_id)
        telegram_user, created = TelegramUser.objects.get_or_create(user_id=chat_id)
        user_favorites, created = UserFavorites.objects.get_or_create(user=telegram_user)
        user_favorites.books.add(book)
        bot.answer_callback_query(callback_query.id, f"'{book.title}' yoqtirgan kitoblarim ga qo'shildi!❤️")
    except ObjectDoesNotExist:
        bot.send_message(chat_id, 'Kitob topilmadi.')
    except Exception as e:
        logger.error(f"qosishda hatlik yuz berdi: {e}")
        bot.send_message(chat_id, f"qosishda hatlik yuz berdi: {e}")

@bot.message_handler(func=lambda message: message.text == "Men yoqtirgan kitoblar❤️")
def show_favorites(message):
    chat_id = message.chat.id
    try:
        telegram_user = TelegramUser.objects.get(user_id=chat_id)
        user_favorites = UserFavorites.objects.get(user=telegram_user)
        if user_favorites.books.exists():
            keyboard = InlineKeyboardMarkup()
            for book in user_favorites.books.all():
                keyboard.add(InlineKeyboardButton(book.title, callback_data=f'show_book_{book.id}'))
            bot.send_message(chat_id, "Siz yoqtirgan kitoblar❤️:", reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "Sizni yoqitrgan kitob mavjud emas.")
    except (TelegramUser.DoesNotExist, UserFavorites.DoesNotExist):
        bot.send_message(chat_id, "Sizni yoqitrgan kitob mavjud emas.")
    except Exception as e:
        logger.error(f"Eror: {e}")
        bot.send_message(chat_id, f"Eror: {e}")

@bot.message_handler(func=lambda message: message.text == "FAQ⁉️")
def show_faq(message):
    chat_id = message.chat.id
    try:
        faqs = FAQ.objects.all()
        if faqs.exists():
            keyboard = InlineKeyboardMarkup()
            for faq in faqs:
                keyboard.add(InlineKeyboardButton(faq.question, callback_data=f'show_faq_{faq.id}'))
            bot.send_message(chat_id, "Tez-tez soraladigan sovollar royhati:", reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "bosh ekan.")
    except Exception as e:
        logger.error(f"Faq da hatolik yuz berdi: {e}")
        bot.send_message(chat_id, f"Faq da hatolik yuz berdi: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('show_faq_'))
def handle_show_faq(callback_query):
    faq_id = int(callback_query.data.split('_')[-1])
    chat_id = callback_query.message.chat.id
    try:
        faq = FAQ.objects.get(id=faq_id)
        bot.send_message(chat_id, faq.answer)
    except ObjectDoesNotExist:
        bot.send_message(chat_id, "Sovol topilmadi.")
    except Exception as e:
        logger.error(f"Sovolni korsatishda hatolik: {e}")
        bot.send_message(chat_id, f"Sovolni korsatishda hatolik: {e}")

@bot.message_handler(func=lambda message: message.text == "Biz haqimizda☺️")
def show_about(message):
    chat_id = message.chat.id
    try:
        about = About.objects.first()
        if about:
            bot.send_message(chat_id, about.description)
        else:
            bot.send_message(chat_id, "Описание о боте отсутствует.")
    except Exception as e:
        logger.error(f"Ошибка при показе информации о боте: {e}")
        bot.send_message(chat_id, f"Ошибка при показе информации о боте: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('show_book_'))
def handle_show_book(callback_query):
    show_book_details(callback_query)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_favorites_'))
def handle_add_to_favorites(callback_query):
    add_to_favorites(callback_query)

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_list')
def back_to_list(callback_query):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    list_books(chat_id=chat_id, message_id=message_id)

from decimal import Decimal

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))
def add_to_cart(callback_query):
    book_id = int(callback_query.data.split('_')[-1])
    chat_id = callback_query.message.chat.id

    if chat_id not in user_data:
        user_data[chat_id] = {'cart': {}, 'message_id': None, 'promo_code': None, 'discount': None}

    if book_id not in user_data[chat_id]['cart']:
        user_data[chat_id]['cart'][book_id] = 1
    else:
        user_data[chat_id]['cart'][book_id] += 1

    bot.answer_callback_query(callback_query.id, text= f"✅Kitob savatga qoshildi! Soni: {user_data[chat_id]['cart'][book_id]} ta.")

from shop.models import Book, PromoCode

user_data = {}

@bot.message_handler(func=lambda message: message.text == "Savat🛒")
def handle_view_cart(message):
    view_cart(message)

def view_cart(message):
    chat_id = message.chat.id

    if chat_id in user_data and 'cart' in user_data[chat_id]:
        cart = user_data[chat_id]['cart']
        if cart:
            message_text = "Sizni savatingiz:\n"
            total_amount = Decimal(0)
            for book_id, quantity in cart.items():
                book = Book.objects.get(id=book_id)
                final_price = Decimal(book.get_final_price())
                total_price = final_price * quantity
                total_amount += total_price
                message_text += f"{book.title} - {quantity} ta. - {total_price} sum\n"
            
            # Apply discount if available
            discount = user_data[chat_id].get('discount', Decimal(0))
            if discount:
                total_amount = total_amount * (Decimal(1) - discount / Decimal(100))
            
            message_text += f"\nUmumiy narxi: {total_amount} sum"
            user_data[chat_id]['total_amount'] = total_amount  # Устанавливаем total_amount для пользователя
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Sotib olish🛒", callback_data='checkout'))
            keyboard.add(InlineKeyboardButton("Есть промокод?", callback_data='enter_promo'))
            bot.send_message(chat_id, message_text, reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "Sizni savatingiz bosh.")
    else:
        bot.send_message(chat_id, "Sizni savatingiz bosh.")

@bot.callback_query_handler(func=lambda call: call.data == 'enter_promo')
def enter_promo_code(callback_query):
    chat_id = callback_query.message.chat.id
    bot.send_message(chat_id, "Пожалуйста, введите ваш промокод:")
    bot.register_next_step_handler(callback_query.message, apply_promo_code)

def apply_promo_code(message):
    chat_id = message.chat.id

    if not message.text:
        bot.send_message(chat_id, "Пожалуйста, введите текстовый промокод.")
        bot.register_next_step_handler(message, apply_promo_code)
        return

    promo_code = message.text.strip()

    try:
        promo = PromoCode.objects.get(code=promo_code)
        
        if promo.is_valid():
            discount = Decimal(promo.discount_percentage)
            user_data[chat_id]['promo_code'] = promo_code
            user_data[chat_id]['discount'] = discount

            view_cart(message)  # Обновить корзину с новой суммой после применения промокода

            # Увеличиваем количество использований промокода
            promo.usage_count += 1
            promo.save()

            bot.send_message(chat_id, f"Промокод принят! Скидка {discount}%.")
        else:
            bot.send_message(chat_id, "Этот промокод больше не действует.")
            bot.register_next_step_handler(message, apply_promo_code)
    except PromoCode.DoesNotExist:
        bot.send_message(chat_id, "Неверный промокод. Пожалуйста, попробуйте снова.")
        bot.register_next_step_handler(message, apply_promo_code)
        

import re
from telebot.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

cities = ["Ташкент", "Самарканд", "Бухара", "Наманган", "Андижан"]  

@bot.callback_query_handler(func=lambda call: call.data == 'checkout')
def checkout(callback_query):
    chat_id = callback_query.message.chat.id
    bot.send_message(chat_id, "FiO kiriting:")
    bot.register_next_step_handler(callback_query.message, get_name)

def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    keyboard = InlineKeyboardMarkup()
    for city in cities:
        keyboard.add(InlineKeyboardButton(city, callback_data=f'city_{city}'))
    bot.send_message(chat_id, "Shaharni tanlang:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def select_city(callback_query):
    chat_id = callback_query.message.chat.id
    city = callback_query.data.split('_')[1]
    user_data[chat_id]['city'] = city
    bot.send_message(chat_id, "Telefon raqamingizni kiriting (Faqat o'zbekcha nomer bo'lsin):")
    bot.register_next_step_handler(callback_query.message, get_phone)

def get_phone(message):
    chat_id = message.chat.id
    phone = message.text
    if re.match(r"^\+998\d{9}$", phone):
        user_data[chat_id]['phone'] = phone
        bot.send_message(chat_id, "Manzilingizni to'liq holda kiriting:")
        bot.register_next_step_handler(message, get_address)
    else:
        bot.send_message(chat_id, "Faqat uzb nomeri qabul qilinadi:")
        bot.register_next_step_handler(message, get_phone)

def get_address(message):
    chat_id = message.chat.id
    user_data[chat_id]['address'] = message.text
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("UzCard", callback_data='pay_uzcard'))
    keyboard.add(InlineKeyboardButton("Humo", callback_data='pay_humo'))
    bot.send_message(chat_id, "Tolov turini tanlang:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ['pay_uzcard', 'pay_humo'])
def select_payment_method(callback_query):
    chat_id = callback_query.message.chat.id
    payment_method = 'UzCard' if callback_query.data == 'pay_uzcard' else 'Humo'
    user_data[chat_id]['payment_method'] = payment_method

    cart = user_data[chat_id]['cart']
    total_amount = sum(Decimal(Book.objects.get(id=book_id).get_final_price()) * quantity for book_id, quantity in cart.items())

    # Применение скидки, если есть промокод
    if 'discount' in user_data[chat_id]:
        discount = user_data[chat_id]['discount']
        total_amount = total_amount * (Decimal(1) - discount / Decimal(100))

    user_data[chat_id]['total_amount'] = total_amount

    card_number = "8600 1234 5678 9012" if payment_method == 'UzCard' else "9860 1234 5678 9012"
    message_text = f"Ummumiy summa: {total_amount} сўм\nKarta: {card_number}"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Tolov qildim✅", callback_data='confirm_payment'))
    bot.send_message(chat_id, message_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_payment')
def confirm_payment(callback_query):
    chat_id = callback_query.message.chat.id
    bot.send_message(chat_id, "Chek ni skrenshot yoki chekni o'zini yuboring (fayl yoki rasm):")
    bot.register_next_step_handler(callback_query.message, handle_payment_proof)

def handle_payment_proof(message):
    chat_id = message.chat.id
    if message.photo or message.document:
        user_data[chat_id]['payment_proof'] = message.photo[-1].file_id if message.photo else message.document.file_id
        bot.send_message(chat_id, "Tasdiqlanishini kuting🕛.")

        # Сохранение информации о покупке
        cart = user_data[chat_id]['cart']
        books = "\n".join([f"{Book.objects.get(id=book_id).title} - {quantity} ta." for book_id, quantity in cart.items()])
        check = Check(
            user_id=chat_id,
            name=user_data[chat_id]['name'],
            city=user_data[chat_id]['city'],
            phone=user_data[chat_id]['phone'],
            address=user_data[chat_id]['address'],
            payment_method=user_data[chat_id]['payment_method'],
            total_amount=user_data[chat_id]['total_amount'],
            books=books,
            payment_proof=user_data[chat_id]['payment_proof'],
            promo_code=user_data[chat_id].get('promo_code')  # Сохранение промокода, если применен
        )
        check.save()

        # Отправка чека админу
        if message.photo:
            bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id,
                           caption=f"Yangi buyurtma keldi:\nFIO: {user_data[chat_id]['name']}\nShahar: {user_data[chat_id]['city']}\nTelefon raqam: {user_data[chat_id]['phone']}\nManzil: {user_data[chat_id]['address']}\nTolov turi: {user_data[chat_id]['payment_method']}\nTolov summasi: {user_data[chat_id]['total_amount']} сўм\nBuyurtma qilingan kitoblar:\n{books}",
                           reply_markup=generate_admin_keyboard(check.id))
        else:
            bot.send_document(ADMIN_CHAT_ID, message.document.file_id,
                              caption=f"Yangi buyurtma keldi:\nFIO: {user_data[chat_id]['name']}\nShahar: {user_data[chat_id]['city']}\nTelefon raqam: {user_data[chat_id]['phone']}\nManzil: {user_data[chat_id]['address']}\nTolov turi: {user_data[chat_id]['payment_method']}\nTolov summasi: {user_data[chat_id]['total_amount']} сўм\nBuyurtma qilingan kitoblar:\n{books}",
                              reply_markup=generate_admin_keyboard(check.id))
        
        if chat_id in user_data:
            user_data[chat_id]['cart'] = {}
            user_data[chat_id]['promo_code'] = None
            user_data[chat_id]['discount'] = None

    else:
        bot.send_message(chat_id, "Chekni yuboring rasm yoki fayl formatda:")
        bot.register_next_step_handler(message, handle_payment_proof)


def generate_admin_keyboard(check_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Tasdiqlash✅", callback_data=f'confirm_{check_id}'))
    keyboard.add(InlineKeyboardButton("Tolov qilmagan⛔", callback_data=f'reject_{check_id}'))
    return keyboard


import logging
CHANNEL_ID = -1002240322001  # Замените на ваш ID канала

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def admin_confirm(callback_query):
    check_id = int(callback_query.data.split('_')[-1])
    try:
        check = Check.objects.get(id=check_id)
    except Check.DoesNotExist:
        logging.error(f"Check with id {check_id} does not exist.")
        return
    
    check.status = 'confirmed'
    check.save()

    # Notify user
    bot.send_message(check.user_id, "Sizning buyurtmangiz qabul qilindi, biz tez orada siz bilan bog'lanamiz.✅")
    bot.send_message(callback_query.message.chat.id, "Foydalanuvchiga bildirishnoma yuborildi.")
    logging.info(f"Order {check_id} confirmed and user notified.")

    # Format message text
    books = check.books.replace('\n', '\n- ')
    message_text = (
            f"🛒TASDIQLANGAN BUYURTMA✅:\n"
            f"────────────────────\n"
            f"•Ismi: {check.name}\n"
            f"•Shahar: {check.city}\n"
            f"•Telefon: {check.phone}\n"
            f"•Addres: {check.address}\n"
            f"•Tolov turi : {check.payment_method}\n"
            f"•Buyurtma narxi: {check.total_amount} сўм\n"
            f"•Yetkazish kerak bolgan kitoblar:\n- {books}"
    )

    # Send the message to the channel
    bot.send_message(CHANNEL_ID, message_text)



@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def admin_reject(callback_query):
    check_id = int(callback_query.data.split('_')[-1])
    check = Check.objects.get(id=check_id)
    check.status = 'rejected'
    check.save()
    bot.send_message(check.user_id, "Siz to'lamagansiz, shuning uchun buyurtmangiz qabul qilinmadi.")
    bot.send_message(callback_query.message.chat.id, "Foydalanuvchiga yuborildi.")



def list_categories(message, page=1, page_size=5, chat_id=None, message_id=None):
    offset = (page - 1) * page_size
    categories = Category.objects.all()[offset:offset + page_size]
    
    if categories:
        category_buttons = []
        for category in categories:
            button = InlineKeyboardButton(category.name, callback_data=f'show_category_{category.id}')
            category_buttons.append([button])

        pagination_keyboard = []
        if page > 1:
            pagination_keyboard.append(InlineKeyboardButton("⬅️", callback_data=f'categories_prev_page_{page-1}'))
        if len(categories) == page_size:
            pagination_keyboard.append(InlineKeyboardButton("➡️", callback_data=f'categories_next_page_{page+1}'))

        if pagination_keyboard:
            category_buttons.append(pagination_keyboard)

        reply_markup = InlineKeyboardMarkup(category_buttons)

        if chat_id and message_id:
            bot.edit_message_text('Kategoriyani tanlang:', chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        else:
            bot.send_message(message.chat.id, 'Kategoriyani tanlang:', reply_markup=reply_markup)
    else:
        bot.send_message(message.chat.id, 'Kategoriya mavjud emas')


def list_books_by_category(callback_query, page=1, page_size=5):
    category_id = int(callback_query.data.split('_')[-1])
    offset = (page - 1) * page_size
    books = Book.objects.filter(category_id=category_id)[offset:offset + page_size]
    
    if books:
        book_buttons = []
        for book in books:
            if book.discount_price:
                button_text = f"{book.title} - {book.price} sum (Chegirma: {book.discount_price} sum)"
            else:
                button_text = f"{book.title} - {book.price} sum"
            button = InlineKeyboardButton(button_text, callback_data=f'show_book_{book.id}')
            book_buttons.append([button])

        pagination_keyboard = []
        if page > 1:
            pagination_keyboard.append(InlineKeyboardButton("⬅️", callback_data=f'books_prev_page_{category_id}_{page-1}'))
        if len(books) == page_size:
            pagination_keyboard.append(InlineKeyboardButton("➡️", callback_data=f'books_next_page_{category_id}_{page+1}'))

        if pagination_keyboard:
            book_buttons.append(pagination_keyboard)

        reply_markup = InlineKeyboardMarkup(book_buttons)
        bot.send_message(callback_query.message.chat.id, 'Ushbu kategoryada kitob mavjud emas:', reply_markup=reply_markup)
    else:
        bot.send_message(callback_query.message.chat.id, 'Ushbu kategoryada kitob mavjud emas.')



@bot.callback_query_handler(func=lambda call: call.data.startswith('books_prev_page_') or call.data.startswith('books_next_page_'))
def handle_books_pagination(call):
    data = call.data.split('_')
    direction = data[0]
    page = int(data[-1])
    if direction == 'books':
        list_books(call.message, page=page, chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('categories_prev_page_') or call.data.startswith('categories_next_page_'))
def handle_categories_pagination(call):
    data = call.data.split('_')
    direction = data[0]
    page = int(data[-1])
    if direction == 'categories':
        list_categories(call.message, page=page, chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('books_prev_page_') or call.data.startswith('books_next_page_'))
def handle_books_by_category_pagination(call):
    data = call.data.split('_')
    category_id = int(data[2])
    direction = data[0]
    page = int(data[-1])
    if direction == 'books':
        list_books_by_category(call, category_id=category_id, page=page)





# Команда /categories
@bot.message_handler(commands=['categories'])
def categories(message):
    list_categories(message)


# Команда /books
@bot.message_handler(commands=['books'])
def books(message):
    list_books(message)



# Функция для выбора количества книг
def choose_quantity(callback_query):
    try:
        book_id = int(callback_query.data.split('_')[-1])
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id
        user_data[chat_id] = {'book_id': book_id, 'quantity': 1, 'message_id': message_id}
        update_quantity_message(chat_id)
    except Exception as e:
        error_msg = f"Error in choose_quantity: {e}"
        bot.send_message(callback_query.message.chat.id, error_msg)

# Функция для обновления сообщения о количестве книг
def update_quantity_message(chat_id):
    quantity = user_data[chat_id]['quantity']
    message_id = user_data[chat_id]['message_id']
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("-", callback_data='decrease_quantity'),
                 InlineKeyboardButton("+", callback_data='increase_quantity'))
    keyboard.add(InlineKeyboardButton("Купить", callback_data='confirm_purchase'))
    try:
        bot.edit_message_text(f"Выберите количество: {quantity}", chat_id, message_id, reply_markup=keyboard)
    except Exception as e:
        error_msg = f"Error updating quantity message: {e}"
        bot.send_message(chat_id, error_msg)

# Функции для изменения количества книг
def increase_quantity(chat_id):
    user_data[chat_id]['quantity'] += 1
    update_quantity_message(chat_id)

def decrease_quantity(chat_id):
    if user_data[chat_id]['quantity'] > 1:
        user_data[chat_id]['quantity'] -= 1
    update_quantity_message(chat_id)

# # Функция подтверждения покупки
# def confirm_purchase(callback_query):
#     chat_id = callback_query.message.chat.id
#     try:
#         if chat_id in user_data:
#             bot.send_message(chat_id, 'Введите ваше имя:')
#             bot.register_next_step_handler(callback_query.message, get_name)
#         else:
#             bot.send_message(chat_id, 'Произошла ошибка при покупке книги. Попробуйте снова.')
#     except Exception as e:
#         error_msg = f"Error confirming purchase: {e}"
#         bot.send_message(chat_id, error_msg)

# # Функция для получения имени пользователя
# def get_name(message):
#     chat_id = message.chat.id
#     user_data[chat_id]['name'] = message.text
#     bot.send_message(chat_id, 'Введите ваш номер телефона:')
#     bot.register_next_step_handler(message, get_phone)

# # Функция для получения номера телефона пользователя
# def get_phone(message):
#     chat_id = message.chat.id
#     user_data[chat_id]['phone'] = message.text
#     bot.send_message(chat_id, 'Введите ваш полный адрес:')
#     bot.register_next_step_handler(message, get_address)

# # Функция для получения адреса пользователя и выбора метода оплаты
# def get_address(message):
#     chat_id = message.chat.id
#     user_data[chat_id]['address'] = message.text
#     choose_payment_method(chat_id)

# # Функция для выбора метода оплаты
# def choose_payment_method(chat_id):
#     try:
#         book = Book.objects.get(id=user_data[chat_id]['book_id'])
#         quantity = user_data[chat_id]['quantity']
#         final_price = book.get_final_price()
#         total_amount = final_price * quantity
#         user_data[chat_id]['total_amount'] = total_amount

#         keyboard = InlineKeyboardMarkup()
#         keyboard.add(InlineKeyboardButton("UZCARD", callback_data='payment_uzcard'),
#                      InlineKeyboardButton("HUMO", callback_data='payment_humo'))

#         bot.send_message(chat_id, f'Выберите способ оплаты:\nОбщая сумма: {total_amount} сўм', reply_markup=keyboard)
#     except Exception as e:
#         error_msg = f"Error choosing payment method: {e}"
#         bot.send_message(chat_id, error_msg)

# def process_payment_method(callback_query):
#     chat_id = callback_query.message.chat.id
#     payment_method = callback_query.data.split('_')[1]

#     # Ensure chat_id exists in user_data
#     if chat_id in user_data:
#         user_data[chat_id]['payment_method'] = payment_method
#     else:
#         # Handle case where chat_id is not found in user_data
#         bot.send_message(chat_id, "Произошла ошибка. Пожалуйста, повторите попытку позже.")
#         return

#     if payment_method == 'uzcard':
#         card_info = 'Номер карты для UZCARD: 8600 1234 5678 9012'
#     elif payment_method == 'humo':
#         card_info = 'Номер карты для HUMO: 9860 1234 5678 9012'
#     else:
#         card_info = 'Информация о карте для выбранного метода оплаты будет доступна позже.'

#     keyboard = InlineKeyboardMarkup()
#     keyboard.add(InlineKeyboardButton("Я оплатил", callback_data='confirm_payment'))

#     bot.send_message(chat_id, card_info, reply_markup=keyboard)


# # Функция для подтверждения оплаты
# def confirm_payment(callback_query):
#     chat_id = callback_query.message.chat.id
#     bot.send_message(chat_id, 'Пожалуйста, отправьте чек или скриншот оплаты.')
#     bot.register_next_step_handler(callback_query.message, handle_payment_receipt)

# def handle_payment_receipt(message: Message):
#     chat_id = message.chat.id

#     if chat_id not in user_data:
#         user_data[chat_id] = {}

#     if message.content_type in ['photo', 'document']:
#         if message.photo:
#             file_id = message.photo[-1].file_id
#             file_type = 'photo'
#         elif message.document:
#             file_id = message.document.file_id
#             file_type = 'document'

#         user_data[chat_id]['payment_receipt'] = {'file_id': file_id, 'file_type': file_type}
#         bot.send_message(chat_id, 'Пожалуйста, подождите, пока администратор проверяет вашу оплату.')
#         send_order_to_admin(chat_id)
#     else:
#         bot.send_message(chat_id, 'Пожалуйста, отправьте чек или скриншот оплаты.')
#         bot.register_next_step_handler(message, handle_payment_receipt)


# # Функция для обработки кнопок "ДА" и "НЕТ"
# def process_order_confirmation(callback_query):
#     chat_id = callback_query.message.chat.id
#     message_id = callback_query.message.message_id
#     data = callback_query.data

#     if data == 'confirm_order':
#         # Сохранение чека в базу данных
#         send_order_to_admin(chat_id)
#     elif data == 'deny_order':
#         bot.send_message(chat_id, 'Ваш заказ отклонен. Пожалуйста, свяжитесь с поддержкой.')

#     # Удаление данных пользователя после обработки заказа
#     if chat_id in user_data:
#         del user_data[chat_id]


# def send_order_to_admin(chat_id):
#     purchase_info = user_data.get(chat_id)
#     if not purchase_info or 'book_id' not in purchase_info:
#         bot.send_message(chat_id, 'Ошибка при отправке заказа. Пожалуйста, попробуйте снова или свяжитесь с поддержкой.')
#         return

#     try:
#         book = Book.objects.get(id=purchase_info['book_id'])
#     except Book.DoesNotExist:
#         bot.send_message(chat_id, 'Выбранная книга не найдена. Пожалуйста, выберите другую книгу или свяжитесь с поддержкой.')
#         return

#     final_price = book.get_final_price()
#     total_amount = final_price * purchase_info.get('quantity', 0)

#     # Отправка сообщения администратору с кнопками "ДА" и "НЕТ"
#     keyboard = InlineKeyboardMarkup()
#     keyboard.add(InlineKeyboardButton("ДА", callback_data=f'confirm_order_{chat_id}'))
#     keyboard.add(InlineKeyboardButton("НЕТ", callback_data=f'deny_order_{chat_id}'))

#     admin_message = (
#         f"Новая покупка:\n\n"
#         f"Книга: {book.title}\n"
#         f"Цена за штуку: {final_price} сўм\n"
#         f"Количество: {purchase_info.get('quantity', 0)}\n"
#         f"Общая сумма: {total_amount} сўм\n"
#         f"Имя: {purchase_info.get('name', 'Не указано')}\n"
#         f"Телефон: {purchase_info.get('phone', 'Не указано')}\n"
#         f"Адрес: {purchase_info.get('address', 'Не указано')}\n"
#         f"Метод оплаты: {purchase_info.get('payment_method', 'Не указано')}\n"
#         f"Чек или скриншот оплаты: Да\n"
#     )

#     try:
#         message = bot.send_message(ADMIN_CHAT_ID, admin_message, reply_markup=keyboard)

#         # Отправляем фотографию или документ (если есть чек)
#         receipt = purchase_info.get('payment_receipt')
#         if receipt and receipt.get('file_type') == 'photo':
#             bot.send_photo(ADMIN_CHAT_ID, receipt['file_id'])
#         elif receipt and receipt.get('file_type') == 'document':
#             bot.send_document(ADMIN_CHAT_ID, receipt['file_id'])

#         bot.send_message(chat_id, 'Ваш заказ отправлен администратору. Ожидайте подтверждения.')
#     except Exception as e:
#         error_msg = f"Ошибка при отправке заказа администратору: {e}"
#         bot.send_message(chat_id, error_msg)


# def process_admin_confirmation(callback_query):
#     try:
#         data = callback_query.data
#         if data.startswith('confirm_order_'):
#             parts = data.split('_')
#             if len(parts) > 1:
#                 chat_id = int(parts[-1])
#                 purchase_info = user_data.get(chat_id)
#                 if purchase_info:
#                     # Получение информации о покупке
#                     book_id = purchase_info.get('book_id')
#                     quantity = purchase_info.get('quantity')
#                     name = purchase_info.get('name', 'Не указано')
#                     phone = purchase_info.get('phone', 'Не указано')
#                     address = purchase_info.get('address', 'Не указано')
#                     payment_method = purchase_info.get('payment_method', 'Не указано')
#                     payment_receipt = purchase_info.get('payment_receipt', {})

#                     try:
#                         book = Book.objects.get(id=book_id)
#                         final_price = book.get_final_price()
#                         total_amount = final_price * quantity
                        
#                         # Создание записи покупки в базе данных
#                         purchase = Purchase(
#                             book=book,
#                             quantity=quantity,
#                             total_amount=total_amount,
#                             name=name,
#                             phone=phone,
#                             address=address,
#                             payment_method=payment_method,
#                             payment_receipt=payment_receipt
#                         )
#                         purchase.save()

#                         # Отправка подтверждения покупателю
#                         bot.send_message(chat_id, 'Ваш заказ подтвержден! Спасибо за покупку.')

#                         # Удаление данных о заказе из временного хранилища
#                         del user_data[chat_id]

#                         # Удаление инлайн кнопок из сообщения администратора
#                         bot.edit_message_reply_markup(ADMIN_CHAT_ID, callback_query.message.message_id)

#                     except Book.DoesNotExist:
#                         bot.send_message(chat_id, 'Выбранная книга не найдена. Пожалуйста, выберите другую книгу или свяжитесь с поддержкой.')

#                 else:
#                     bot.send_message(chat_id, 'Данные о покупке не найдены. Пожалуйста, попробуйте снова или свяжитесь с поддержкой.')

#             else:
#                 print(f"Invalid callback data format: {data}")
#         elif data.startswith('deny_order_'):
#             parts = data.split('_')
#             if len(parts) > 1:
#                 chat_id = int(parts[-1])
#                 purchase_info = user_data.get(chat_id)
#                 if purchase_info:
#                     bot.send_message(chat_id, 'Ваш заказ не был оплачен. Пожалуйста, оплатите заказ для его подтверждения.')
#                     # Удаление инлайн кнопок из сообщения администратора
#                     bot.edit_message_reply_markup(ADMIN_CHAT_ID, callback_query.message.message_id)
#                 else:
#                     bot.send_message(chat_id, 'Данные о покупке не найдены. Пожалуйста, попробуйте снова или свяжитесь с поддержкой.')
#             else:
#                 print(f"Invalid callback data format: {data}")
#         else:
#             print(f"Unhandled callback data: {data}")
#     except Exception as e:
#         print(f"Error processing admin confirmation: {e}")



import time
from telebot import types
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.utils import timezone
from django.core.management.base import BaseCommand
from shop.models import TelegramUser
from datetime import datetime, timedelta
from django.db.models import Sum

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Save user information in the database
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    user, created = TelegramUser.objects.get_or_create(
        user_id=user_id,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
        }
    )

    if created:
        print(f"New user {username} ({user_id}) added.")
    else:
        print(f"User {username} ({user_id}) already exists.")

    # Create the main menu keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menyu_button = types.KeyboardButton("Kitoblar menyu📖")
    savat = types.KeyboardButton("Savat🛒")
    bonus = types.KeyboardButton("Sovga yutib olish🎁")
    favorite = types.KeyboardButton("Men yoqtirgan kitoblar❤️")
    faq = types.KeyboardButton("FAQ⁉️")
    about = types.KeyboardButton("Biz haqimizda☺️")
    keyboard.row(menyu_button, savat)
    keyboard.row(bonus)
    keyboard.row(favorite)
    keyboard.row(faq, about)

    # Send the welcome message with the main menu
    bot.send_message(message.chat.id, "😍Asalomu aleykum Nur dokoniga hush kelibsiz\nSiz izlagan kitoblar sizni kutib qoldi", reply_markup=keyboard)

# Обработка нажатия кнопки "menyu😍"
@bot.message_handler(func=lambda message: message.text == "Kitoblar menyu📖")
def handle_menu_button(message):
    keyboard = types.InlineKeyboardMarkup()
    show_books_button = types.InlineKeyboardButton("📚Kitoblar", callback_data='show_books')
    show_categories_button = types.InlineKeyboardButton("📁Kategoriya", callback_data='show_categories')
    search_button = types.InlineKeyboardButton("🔎Qidiruv", callback_data='search_options')
    keyboard.row(show_books_button, show_categories_button)
    keyboard.row(search_button)
    bot.send_message(message.chat.id, "😍Asalomu aleykum Nur dokoniga hush kelibsiz\nSiz izlagan kitoblar sizni kutib qoldi", reply_markup=keyboard)

# Обработка callback'а для кнопки "Qidiruv", чтобы показать опции поиска по названию или автору
@bot.callback_query_handler(func=lambda call: call.data == 'search_options')
def show_search_options(callback_query):
    keyboard = types.InlineKeyboardMarkup()
    search_by_inline_button = types.InlineKeyboardButton("🔎inline qidiruv", switch_inline_query_current_chat='')
    search_by_title_button = types.InlineKeyboardButton("🔎Nomi orqali izlash", callback_data='search_by_title')
    search_by_author_button = types.InlineKeyboardButton("🔎Mualif orqali izlash", callback_data='search_by_author')
    keyboard.row(search_by_inline_button)
    keyboard.row(search_by_title_button, search_by_author_button)
    bot.send_message(callback_query.message.chat.id, "Qidiruv turini tanlang:\n🔎inline qidiruv orqali tez va oson izlagan kitobingizni topishingiz munkun\n🔎Nomi orqali izlash orali kitobni nomi orqali qidirshingiz munkun\n🔎Mualif orqali izlash orqali kitobni mualifi orqali qidirshingiz munkun", reply_markup=keyboard)

# Implement the search by title functionality
@bot.callback_query_handler(func=lambda call: call.data == 'search_by_title')
def prompt_for_title_search(callback_query):
    bot.send_message(callback_query.message.chat.id, "Kitob nomini kiriting:")
    bot.register_next_step_handler(callback_query.message, search_books_by_title)

def search_books_by_title(message):
    title = message.text
    books = Book.objects.filter(title__icontains=title)
    if books.exists():
        book_buttons = [[InlineKeyboardButton(f"{book.title} - {book.price} sum (Chegirma: {book.discount_price} sum)", callback_data=f'show_book_{book.id}')] for book in books]
        reply_markup = InlineKeyboardMarkup(book_buttons)
        bot.send_message(message.chat.id, "Qidiruv natijasi:", reply_markup=reply_markup)
    else:
        bot.send_message(message.chat.id, "Uzur topolmadim😐.")

# Implement the search by author name functionality
@bot.callback_query_handler(func=lambda call: call.data == 'search_by_author')
def prompt_for_author_search(callback_query):
    bot.send_message(callback_query.message.chat.id, "Mualif ismini kiriting:")
    bot.register_next_step_handler(callback_query.message, search_books_by_author)

def search_books_by_author(message):
    author_name = message.text
    authors = Author.objects.filter(name__icontains=author_name)
    if authors.exists():
        book_buttons = []
        for author in authors:
            books = author.book_set.all()
            for book in books:
                button_text = f"{book.title} - {book.price} sum (Chegirma: {book.discount_price} sum)"
                book_buttons.append([InlineKeyboardButton(button_text, callback_data=f'show_book_{book.id}')])
        reply_markup = InlineKeyboardMarkup(book_buttons)
        bot.send_message(message.chat.id, "Qidiruv natijasi:", reply_markup=reply_markup)
    else:
        bot.send_message(message.chat.id, "Uzur topolmadim😐.")


@bot.inline_handler(lambda query: len(query.query) > 0)
def handle_inline_query(query):
    try:
        books = Book.objects.filter(title__icontains=query.query).order_by('id')[:5]  # Замените на ваше условие поиска

        results = []
        for book in books:
            description = f"{book.title} - {book.price} sum (Chegirma: {book.discount_price} sum)"  # Замените на ваше форматирование описания книги

            result = InlineQueryResultArticle(
                id=str(book.id),
                title=book.title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=f"{book.title}\n\n{description}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Tanlash", callback_data=f'choose_book_{book.id}')],
                ])
            )
            results.append(result)

        bot.answer_inline_query(query.id, results, cache_time=1)

    except Exception as e:
        print(f"Error handling inline query: {e}")

# Обработчик callback-запросов при выборе книги
@bot.callback_query_handler(lambda call: call.data.startswith('choose_book_'))
def handle_choose_book(call):
    book_id = int(call.data.split('_')[-1])
    try:
        book = Book.objects.get(id=book_id)
        if book:
            final_price = book.get_final_price()  # Замените на ваш метод для получения окончательной цены книги
            message_text = f"{book.title}\nNarx: {final_price} сўм\n\nKtiob haqida: {book.description}"  # Замените на ваше форматирование текста сообщения
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Savatga qoshish🛒", callback_data=f'add_to_cart_{book.id}')],
            ])
            if call.message:
                bot.send_message(call.message.chat.id, message_text, reply_markup=keyboard, parse_mode='HTML')  # Замените на вашу предпочитаемую разметку
            else:
                bot.send_message(call.from_user.id, message_text, reply_markup=keyboard, parse_mode='HTML')  # Если сообщение callback'а не существует, отправляем пользователю напрямую
        else:
            bot.send_message(call.from_user.id, 'Uzur topolmadim😐.')  # Если книга не найдена, сообщаем пользователю об этом

    except Book.DoesNotExist:
        bot.send_message(call.from_user.id, 'Uzur topolmadim😐.')  # Если книга не найдена, сообщаем пользователю об этом
    except Exception as e:
        print(f"Error handling choose book: {e}")


# ------------------------BARABAN---------------------------------------#

from shop.models import Gift, UserGift
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo



# Обработчик для добавления подарков админом
@bot.message_handler(commands=['add_gift'])
def handle_add_gift(message):
    if str(message.chat.id) == ADMIN_CHAT_ID:
        try:
            # Пример: /add_gift Название подарка|Описание подарка
            gift_details = message.text.split(' ', 1)[1]
            name, description = gift_details.split('|')
            gift = Gift.objects.create(name=name.strip(), description=description.strip())
            bot.send_message(message.chat.id, f"Подарок '{gift.name}' успешно добавлен.")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при добавлении подарка: {e}")
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")


roulette_enabled = False
# Обработчик для вращения рулетки
@bot.message_handler(func=lambda message: message.text == "Sovga yutib olish🎁")
def handle_spin_wheel(message):
    chat_id = message.chat.id
    today = datetime.now().date()

    if not roulette_enabled:
        bot.send_message(chat_id, "Uzur bu bolim tamirda tez orada ishga tushadi🛠️.")
        return

    # Проверяем, крутил ли пользователь рулетку сегодня
    last_spin = UserGift.objects.filter(user_id=chat_id).order_by('-date_won').first()
    if last_spin and last_spin.date_won == today:
        bot.send_message(chat_id, "Siz bugun birmarta sovga oldingiz. Ertaga urunib koring😐")
        return

    try:
        active_gifts = Gift.objects.filter(is_active=True)
        if active_gifts:
            gift = random.choice(active_gifts)
            UserGift.objects.create(user_id=chat_id, gift=gift)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Sovgani olish🎁", callback_data=f'claim_gift_{gift.id}'))
            bot.send_message(chat_id, f"Вы выиграли подарок: {gift.name}\nОписание: {gift.description}", reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "Uzur sovga mavjud emas.")
    except Exception as e:
        bot.send_message(chat_id, f"Hatolik yuz berdi: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('claim_gift_'))
def claim_gift(callback_query):
    gift_id = int(callback_query.data.split('_')[-1])
    chat_id = callback_query.message.chat.id
    try:
        gift = Gift.objects.get(id=gift_id)
        gift.is_active = False  # Деактивируем подарок после его получения
        gift.save()  # Сохраняем изменения

        if gift.type == 'promo_code':
            # Отправить только промокод
            bot.send_message(chat_id, f"Поздравляем! Вы получили промокод: {gift.name}\nИспользуйте его при следующей покупке.")
        
        elif gift.type == 'free_book':
            # Запросить данные для отправки книги
            bot.send_message(chat_id, "Поздравляем! Вы получили бесплатную книгу.")
            bot.send_message(chat_id, "Пожалуйста, введите ваше имя:")
            bot.register_next_step_handler(callback_query.message, process_name_for_free_book, gift)
        
        else:
            bot.send_message(chat_id, "Подарок неизвестного типа.")
    
    except Gift.DoesNotExist:
        bot.send_message(chat_id, "Подарок не найден.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при получении подарка: {e}")

def process_name_for_free_book(message, gift):
    chat_id = message.chat.id
    name = message.text.strip()

    # Здесь можно добавить логику для получения телефона, адреса и отправки администратору
    # Например:
    # bot.send_message(chat_id, "Пожалуйста, введите ваш номер телефона:")
    # bot.register_next_step_handler(message, process_phone_for_free_book, gift, name)

    bot.send_message(chat_id, f"Спасибо, {name}! Ваша бесплатная книга будет отправлена.")


# Обработчик для просмотра выигранных подарков
@bot.message_handler(commands=['my_gifts'])
def handle_my_gifts(message):
    chat_id = message.chat.id
    user_gifts = UserGift.objects.filter(user_id=chat_id)
    if user_gifts:
        message_text = "Siz yutib olgan sovgalar:\n"
        for user_gift in user_gifts:
            message_text += f"{user_gift.gift.name} - {user_gift.date_won}\n"
        bot.send_message(chat_id, message_text)
    else:
        bot.send_message(chat_id, "Siz hali sovga yutib olmagansiz.")

# Обработчик для ввода промокода
@bot.message_handler(commands=['enter_promo'])
def handle_enter_promo(message):
    chat_id = message.chat.id
    try:
        # Пример: /enter_promo PROMOCODE123
        if len(message.text.split()) < 2:
            raise ValueError("Промокод не указан.")
        
        promo_code = message.text.split(' ', 1)[1].strip()
        # Логика проверки и применения промокода
        # Например, можно установить скидку для пользователя
        discount = 0.2  # 20% скидка
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['promo_code'] = promo_code
        user_data[chat_id]['discount'] = discount
        bot.send_message(chat_id, f"Промокод '{promo_code}' успешно применен. Ваша скидка: {discount * 100}%.")
    except ValueError as ve:
        bot.send_message(chat_id, f"Ошибка: {ve}")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка при применении промокода: {e}")






#--------------------------ADMIN PANEL----------------------------------#


@bot.message_handler(commands=['admin'])
def handle_start(message):
    # Create the main menu keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    pochta = types.KeyboardButton("Habarlar bolimi✉️")
    statistika = types.KeyboardButton("Statistika📊")
    cheks = types.KeyboardButton("Cheklar bolimi📒")
    #about = types.KeyboardButton("ьвывщсы")
    keyboard.row(pochta, statistika)
    keyboard.row(cheks)

    # Send the welcome message with the main menu
    bot.send_message(message.chat.id, "Salom admin", reply_markup=keyboard)

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Словарь для хранения данных, специфичных для пользователя
user_data = {}

@bot.message_handler(commands=['cheks'])
def handle_checks_command(message):
    chat_id = message.chat.id
    
    # Получаем все уникальные города из базы данных чеков
    cities = Check.objects.values_list('city', flat=True).distinct()
    
    # Создаем клавиатуру с кнопками для выбора городов
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for city in cities:
        keyboard.add(KeyboardButton(city))
    
    bot.send_message(chat_id, "Выберите город для просмотра чеков:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text in [city for city in Check.objects.values_list('city', flat=True).distinct()])
def handle_selected_city(message):
    chat_id = message.chat.id
    selected_city = message.text
    
    # Сохраняем выбранный город и инициализируем первую страницу для пользователя
    user_data[chat_id] = {
        'selected_city': selected_city,
        'current_page': 1,
        'page_size': 5  # Количество чеков на странице
    }
    
    send_checks_page(chat_id)

def send_checks_page(chat_id):
    selected_city = user_data[chat_id]['selected_city']
    current_page = user_data[chat_id]['current_page']
    page_size = user_data[chat_id]['page_size']
    
    # Получаем все чеки для выбранного города с статусом "confirmed"
    checks = list(Check.objects.filter(city=selected_city, status='confirmed'))
    total_checks = len(checks)
    total_pages = (total_checks + page_size - 1) // page_size  # Количество страниц
    
    if checks:
        start_index = (current_page - 1) * page_size
        end_index = start_index + page_size
        checks_page = checks[start_index:end_index]
        
        response = f"Чеки для города {selected_city} со статусом 'confirmed' (Страница {current_page}/{total_pages}):\n"
        for check in checks_page:
            response += (
                f"ID: {check.id}\n"
                f"Имя: {check.name}\n"
                f"Телефон: {check.phone}\n"
                f"Адрес: {check.address}\n"
                f"Сумма: {check.total_amount} сум\n\n"
            )
        
        # Клавиатура для навигации
        keyboard = InlineKeyboardMarkup(row_width=3)
        if current_page > 1:
            keyboard.add(InlineKeyboardButton("<<", callback_data=f'prev_page'))
        if current_page < total_pages:
            keyboard.add(InlineKeyboardButton(">>", callback_data=f'next_page'))
        
        bot.send_message(chat_id, response, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, f"Для города {selected_city} чеки со статусом 'confirmed' не найдены.")

@bot.callback_query_handler(func=lambda call: call.data in ['prev_page', 'next_page'])
def handle_pagination(call):
    chat_id = call.message.chat.id
    
    if call.data == 'prev_page':
        user_data[chat_id]['current_page'] -= 1
    elif call.data == 'next_page':
        user_data[chat_id]['current_page'] += 1
    
    send_checks_page(chat_id)
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: message.text == "Habarlar bolimi✉️")
def handle_send(message):
    msg = bot.send_message(message.chat.id, "Iltimos, yuboriladigan kontentni kiriting (matn, фото, видео, аудио, музыка):")
    bot.register_next_step_handler(msg, prompt_for_inline_button)

def prompt_for_inline_button(message):
    content = message
    msg = bot.send_message(message.chat.id, "Tugma qoshaymi? (да/нет)")
    bot.register_next_step_handler(msg, lambda msg: handle_inline_button_response(msg, content))

def handle_inline_button_response(message, content):
    if message.text.lower() == 'да':
        msg = bot.send_message(message.chat.id, "Tugma uchun text yuboring:")
        bot.register_next_step_handler(msg, lambda msg: get_button_text(msg, content))
    else:
        broadcast_message(content)

def get_button_text(message, content):
    button_text = message.text
    msg = bot.send_message(message.chat.id, "Link yuboring:")
    bot.register_next_step_handler(msg, lambda msg: get_button_url(msg, content, button_text))

def get_button_url(message, content, button_text):
    button_url = message.text
    inline_button = InlineKeyboardButton(text=button_text, url=button_url)
    inline_keyboard = InlineKeyboardMarkup().add(inline_button)
    broadcast_message(content, inline_keyboard)

def broadcast_message(message, reply_markup=None):
    users = TelegramUser.objects.all()
    content_type = message.content_type
    batch_size = 100  # Размер пакета для отправки
    delay = 0.1  # Задержка между пакетами

    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        for user in batch:
            try:
                if content_type == 'text':
                    bot.send_message(user.user_id, message.text, reply_markup=reply_markup)
                elif content_type == 'photo':
                    bot.send_photo(user.user_id, message.photo[-1].file_id, caption=message.caption, reply_markup=reply_markup)
                elif content_type == 'video':
                    bot.send_video(user.user_id, message.video.file_id, caption=message.caption, reply_markup=reply_markup)
                elif content_type == 'audio':
                    bot.send_audio(user.user_id, message.audio.file_id, caption=message.caption, reply_markup=reply_markup)
                elif content_type == 'document':
                    bot.send_document(user.user_id, message.document.file_id, caption=message.caption, reply_markup=reply_markup)
                else:
                    bot.send_message(message.chat.id, "Тип контента не поддерживается для рассылки.")
            except Exception as e:
                print(f"Error sending message to {user.user_id}: {e}")
        time.sleep(delay)

@bot.message_handler(func=lambda message: message.text == "Statistika📊")
def handle_stats(message):
    total_users = TelegramUser.objects.count()
    active_users_last_day = TelegramUser.objects.filter(last_active__gte=datetime.now()-timedelta(days=1)).count()
    active_users_last_week = TelegramUser.objects.filter(last_active__gte=datetime.now()-timedelta(days=7)).count()

    stats_message = (
        f"📊 Statistila:\n"
        f"Ummumiy foydlanuvchilar: {total_users}\n"
        f"Ohirgi kundagi faol foydalanuvchilar: {active_users_last_day}\n"
        f"Ushbu hafata davomidagi faol foydalanuvchilar: {active_users_last_week}\n"
    )

    bot.send_message(message.chat.id, stats_message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user, created = TelegramUser.objects.get_or_create(user_id=message.from_user.id)
    user.first_name = message.from_user.first_name
    user.last_name = message.from_user.last_name
    user.username = message.from_user.username
    user.last_active = timezone.now()
    user.messages_sent += 1
    user.save()
    # Остальная логика обработки сообщения...





@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(callback_query):
    try:
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        
        if data == 'show_books':
            list_books(callback_query.message)
        elif data == 'show_categories':
            list_categories(callback_query.message)
        elif data.startswith('show_category'):
            list_books_by_category(callback_query)
        elif data.startswith('show_book'):
            show_book_details(callback_query)
        elif data.startswith('choose_quantity'):
            choose_quantity(callback_query)
        elif data.startswith('increase_quantity'):
            increase_quantity(chat_id)
        elif data.startswith('decrease_quantity'):
            decrease_quantity(chat_id)
        # elif data == 'confirm_purchase':
        #     confirm_purchase(callback_query)
        # elif data in ['payment_uzcard', 'payment_humo']:
        #     process_payment_method(callback_query)
        # elif data == 'confirm_payment':
        #     confirm_payment(callback_query)
        # elif data.startswith('confirm_order') or data.startswith('deny_order'):
        #     process_admin_confirmation(callback_query)
        elif data.startswith('next_page'):
            page = int(data.split('_')[-1])
            list_books(callback_query.message, page=page)
        elif data.startswith('prev_page'):
            page = int(data.split('_')[-1])
            list_books(callback_query.message, page=page)
        elif data.startswith('next_cat_page'):
            page = int(data.split('_')[-1])
            list_categories(callback_query.message, page=page)
        elif data.startswith('prev_cat_page'):
            page = int(data.split('_')[-1])
            list_categories(callback_query.message, page=page)
    except Exception as e:
        print(f"Error handling callback: {e}")


class Command(BaseCommand):
    help = 'Run the telegram bot'

    def handle(self, *args, **kwargs):
        bot.polling()

def main():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()