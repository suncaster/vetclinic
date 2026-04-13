# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('CLIENT', 'Клиент'),
        ('DOCTOR', 'Врач'),
        ('ADMIN', 'Администратор'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True, unique=True, verbose_name="Телефон")
    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def clean(self):
        # Проверка на уникальность email при создании
        if CustomUser.objects.filter(email=self.email).exclude(id=self.id).exists():
            raise ValidationError({'email': 'Пользователь с таким email уже существует'})
        if self.phone and CustomUser.objects.filter(phone=self.phone).exclude(id=self.id).exists():
            raise ValidationError({'phone': 'Пользователь с таким номером телефона уже существует'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'