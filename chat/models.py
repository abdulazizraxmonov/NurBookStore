from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)  # Изображение сообщения
    replied_to = models.ForeignKey(User, related_name='replies', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.content}'
