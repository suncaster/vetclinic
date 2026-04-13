from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import News, Appointment, Review, DoctorSchedule
from users.models import CustomUser
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import DoctorSchedule, Appointment

def index(request):
    news_list = News.objects.filter(is_active=True)[:6]
    return render(request, 'main/index.html', {'news_list': news_list})

def get_available_slots(request, doctor_id):

    # Получаем врача
    doctor = get_object_or_404(CustomUser, id=doctor_id, role='DOCTOR')

    # Начало и конец периода (30 дней)
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=30)

    # Получаем все свободные окна врача
    free_slots = DoctorSchedule.objects.filter(
        doctor=doctor,
        date__gte=start_date,
        date__lte=end_date,
        is_available=True
    ).order_by('date', 'start_time')

    # Получаем уже занятые записи на эти даты и время
    appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date__gte=start_date,
        appointment_date__date__lte=end_date,
        status__in=['PENDING', 'CONFIRMED']
    ).values_list('appointment_date', flat=True)

    # Формируем список занятых слотов
    busy_slots = set()
    for app in appointments:
        busy_slots.add(app.strftime('%Y-%m-%d %H:%M'))

    # Формируем список свободных слотов
    available_slots = []
    for slot in free_slots:
        slot_datetime = datetime.combine(slot.date, slot.start_time)
        slot_str = slot_datetime.strftime('%Y-%m-%d %H:%M')

        # Проверяем, не занят ли слот
        if slot_str not in busy_slots and slot_datetime > datetime.now():
            available_slots.append({
                'value': slot_datetime.isoformat(),
                'label': slot.date.strftime('%d.%m.%Y') + ' ' + slot.start_time.strftime('%H:%M')
            })

    return JsonResponse(available_slots, safe=False)


@login_required
def appointment_create(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        appointment_date = request.POST.get('appointment_date')  # теперь приходит из select
        pet_name = request.POST.get('pet_name')
        pet_type = request.POST.get('pet_type')
        symptoms = request.POST.get('symptoms')

        doctor = get_object_or_404(CustomUser, id=doctor_id, role='DOCTOR')

        # Проверяем, что выбранный слот действительно свободен
        slot_datetime = datetime.fromisoformat(appointment_date)

        # Проверка: существует ли такое свободное окно
        slot_exists = DoctorSchedule.objects.filter(
            doctor=doctor,
            date=slot_datetime.date(),
            start_time=slot_datetime.time(),
            is_available=True
        ).exists()

        # Проверка: не занят ли уже этот слот
        slot_busy = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=slot_datetime,
            status__in=['PENDING', 'CONFIRMED']
        ).exists()

        if not slot_exists or slot_busy:
            messages.error(request, 'Выбранное время уже недоступно. Пожалуйста, выберите другое.')
            doctors = CustomUser.objects.filter(role='DOCTOR')
            return render(request, 'main/appointment_form.html', {'doctors': doctors})

        # Проверка, что дата в будущем
        if slot_datetime <= datetime.now():
            messages.error(request, 'Нельзя записаться на прошедшее время')
            doctors = CustomUser.objects.filter(role='DOCTOR')
            return render(request, 'main/appointment_form.html', {'doctors': doctors})

        appointment = Appointment.objects.create(
            client=request.user,
            doctor=doctor,
            pet_name=pet_name,
            pet_type=pet_type,
            appointment_date=slot_datetime,
            symptoms=symptoms
        )
        messages.success(request, 'Запись успешно создана!')
        return redirect('my_appointments')

    doctors = CustomUser.objects.filter(role='DOCTOR')
    return render(request, 'main/appointment_form.html', {'doctors': doctors})

@login_required
def my_appointments(request):
    if request.user.role == 'DOCTOR':
        appointments = Appointment.objects.filter(doctor=request.user)
    else:
        appointments = Appointment.objects.filter(client=request.user)
    return render(request, 'main/appointments.html', {'appointments': appointments})


@login_required
def cancel_appointment(request, pk):
    """Отмена записи на приём"""
    appointment = get_object_or_404(Appointment, pk=pk)

    # Проверяем права: только клиент может отменить свою запись
    if appointment.client != request.user:
        messages.error(request, 'Вы можете отменить только свои записи')
        return redirect('my_appointments')

    # Проверяем, что запись ещё не прошла и не отменена
    if appointment.status == 'CANCELLED':
        messages.warning(request, 'Эта запись уже отменена')
    elif appointment.status == 'COMPLETED':
        messages.error(request, 'Нельзя отменить уже проведённый приём')
    else:
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, 'Запись успешно отменена')

    return redirect('my_appointments')


@login_required
def reschedule_appointment(request, pk):
    """Перенос записи на приём (для врача)"""
    appointment = get_object_or_404(Appointment, pk=pk)

    # Проверяем права: только врач может перенести запись
    if request.user.role != 'DOCTOR' or appointment.doctor != request.user:
        messages.error(request, 'Только врач может переносить записи')
        return redirect('my_appointments')

    if request.method == 'POST':
        new_date = request.POST.get('new_date')
        if new_date:
            appointment.appointment_date = new_date
            appointment.status = 'RESCHEDULED'
            appointment.save()
            messages.success(request, f'Запись перенесена на {new_date}')
        else:
            messages.error(request, 'Укажите новую дату и время')
        return redirect('my_appointments')

    return render(request, 'main/reschedule.html', {'appointment': appointment})


def reviews_list(request):
    """Список одобренных отзывов"""
    approved_reviews = Review.objects.filter(status='APPROVED')
    return render(request, 'main/reviews.html', {'reviews': approved_reviews})


@login_required
def create_review(request, appointment_id):
    """Создание отзыва (только клиент с завершённым приёмом)"""
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)

    # Проверяем, что приём завершён
    if appointment.status != 'COMPLETED':
        messages.error(request, 'Отзыв можно оставить только после проведённого приёма')
        return redirect('my_appointments')

    # Проверяем, не оставлял ли уже отзыв
    if hasattr(appointment, 'review'):
        messages.error(request, 'Вы уже оставили отзыв на этот приём')
        return redirect('my_appointments')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            messages.error(request, 'Заполните все поля')
            return render(request, 'main/review_form.html', {'appointment': appointment})

        Review.objects.create(
            client=request.user,
            appointment=appointment,
            rating=int(rating),
            comment=comment,
            status='PENDING'
        )
        messages.success(request, 'Спасибо за отзыв! Он отправлен на модерацию.')
        return redirect('my_appointments')

    return render(request, 'main/review_form.html', {'appointment': appointment})


@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def moderate_review(request, pk):
    """Модерация отзыва (только админ)"""
    review = get_object_or_404(Review, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            review.status = 'APPROVED'
            messages.success(request, 'Отзыв одобрен и опубликован')
        elif action == 'reject':
            review.status = 'REJECTED'
            messages.success(request, 'Отзыв отклонён')
        review.save()

    return redirect('profile')


@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def create_news(request):
    """Создание новости (только админ)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        if not title or not content:
            messages.error(request, 'Заполните заголовок и содержание')
            return render(request, 'main/news_form.html')

        news = News.objects.create(
            title=title,
            content=content,
            image=image,
            is_active=True
        )
        messages.success(request, f'Новость "{title}" создана')
        return redirect('index')

    return render(request, 'main/news_form.html')


@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def edit_news(request, pk):
    """Редактирование новости (только админ)"""
    news = get_object_or_404(News, pk=pk)

    if request.method == 'POST':
        news.title = request.POST.get('title')
        news.content = request.POST.get('content')
        if request.FILES.get('image'):
            news.image = request.FILES.get('image')
        news.is_active = request.POST.get('is_active') == 'on'
        news.save()
        messages.success(request, 'Новость обновлена')
        return redirect('index')

    return render(request, 'main/news_form.html', {'news': news})


@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def delete_news(request, pk):
    """Удаление новости (только админ)"""
    news = get_object_or_404(News, pk=pk)
    title = news.title
    news.delete()
    messages.success(request, f'Новость "{title}" удалена')
    return redirect('index')


@login_required
def add_schedule(request):
    """Добавление свободного окна в расписание (только врач)"""
    if request.user.role != 'DOCTOR':
        messages.error(request, 'Только врачи могут добавлять расписание')
        return redirect('index')

    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not date or not start_time or not end_time:
            messages.error(request, 'Заполните все поля')
            return render(request, 'main/schedule_form.html')

        # Проверяем, не существует ли уже такое окно
        existing = DoctorSchedule.objects.filter(
            doctor=request.user,
            date=date,
            start_time=start_time
        ).first()

        if existing:
            messages.error(request, 'Это время уже добавлено в расписание')
        else:
            DoctorSchedule.objects.create(
                doctor=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                is_available=True
            )
            messages.success(request, f'Время {start_time}-{end_time} добавлено в расписание на {date}')

        return redirect('profile')

    return render(request, 'main/schedule_form.html')


@login_required
@user_passes_test(lambda u: u.role == 'ADMIN')
def delete_user(request, pk):
    """Удаление пользователя (только админ)"""
    user_to_delete = get_object_or_404(CustomUser, pk=pk)

    if user_to_delete == request.user:
        messages.error(request, 'Нельзя удалить самого себя')
    elif user_to_delete.role == 'ADMIN':
        messages.error(request, 'Нельзя удалить другого администратора')
    else:
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'Пользователь "{username}" удалён')

    return redirect('profile')


@login_required
def complete_appointment(request, pk):
    """Отметить приём как проведённый (только врач)"""
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user)

    if appointment.status == 'COMPLETED':
        messages.warning(request, 'Этот приём уже отмечен как проведённый')
    else:
        appointment.status = 'COMPLETED'
        appointment.save()
        messages.success(request, f'Приём с {appointment.client.username} отмечен как проведённый')

    return redirect('my_appointments')


@login_required
def update_appointment_status(request, pk):
    """Обновление статуса приёма (только врач)"""
    appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in ['CONFIRMED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED']:
            appointment.status = new_status
            if notes:
                appointment.notes = notes
            appointment.save()
            messages.success(request, f'Статус приёма изменён на {appointment.get_status_display()}')
        else:
            messages.error(request, 'Неверный статус')

    return redirect('my_appointments')

