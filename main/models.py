from django.db import models
from django.utils import timezone
from users.models import CustomUser


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает'),
        ('CONFIRMED', 'Подтверждён'),
        ('COMPLETED', 'Проведён'),
        ('CANCELLED', 'Отменён'),
        ('RESCHEDULED', 'Перенесён'),
    ]

    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments',
                               limit_choices_to={'role': 'DOCTOR'})
    pet_name = models.CharField(max_length=100, verbose_name="Кличка питомца")
    pet_type = models.CharField(max_length=50, verbose_name="Вид животного")
    appointment_date = models.DateTimeField(verbose_name="Дата и время приёма")
    symptoms = models.TextField(blank=True, verbose_name="Симптомы")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Заметки врача")

    def __str__(self):
        return f"{self.client.username} - {self.doctor.username} - {self.appointment_date}"

    class Meta:
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        ordering = ['-appointment_date']


class Review(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'На модерации'),
        ('APPROVED', 'Одобрен'),
        ('REJECTED', 'Отклонён'),
    ]

    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.rating}★"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']


class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='schedules',
                               limit_choices_to={'role': 'DOCTOR'})
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Начало")
    end_time = models.TimeField(verbose_name="Конец")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")

    def __str__(self):
        return f"{self.doctor.username} - {self.date} {self.start_time}-{self.end_time}"

    class Meta:
        verbose_name = 'Расписание врача'
        verbose_name_plural = 'Расписания врачей'
        unique_together = ['doctor', 'date', 'start_time']