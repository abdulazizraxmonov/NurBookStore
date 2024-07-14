import os
import django

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')  # Замените `yourproject` на имя вашего проекта
django.setup()

from shop.models import Check  # Замените `yourapp` на имя вашего приложения

# Удаление всех записей из таблицы Check
Check.objects.all().delete()

print("Все записи из таблицы Check были удалены.")
