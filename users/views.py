# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from main.models import Appointment, Review, DoctorSchedule, News


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('index')
        messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'users/login.html')




from django.db import IntegrityError


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')

        if password != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'users/signup.html')

        # Проверка уникальности username
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'users/signup.html')

        # Проверка уникальности email
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже зарегистрирован')
            return render(request, 'users/signup.html')

        # Проверка уникальности телефона (если указан)
        if phone and CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, 'Пользователь с таким номером телефона уже зарегистрирован')
            return render(request, 'users/signup.html')

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                role='CLIENT'
            )
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('index')
        except IntegrityError:
            messages.error(request, 'Ошибка при регистрации. Возможно, email или телефон уже используются.')
            return render(request, 'users/signup.html')

    return render(request, 'users/signup.html')


def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')


@login_required
def profile(request):
    context = {}

    if request.user.role == 'ADMIN':
        # Админ панель
        context['users'] = CustomUser.objects.all()
        context['news_list'] = News.objects.all()
        context['reviews_pending'] = Review.objects.filter(status='PENDING')
        context['appointments'] = Appointment.objects.all()
        context['template'] = 'users/admin_panel.html'

    elif request.user.role == 'DOCTOR':
        # Кабинет врача
        context['appointments'] = Appointment.objects.filter(doctor=request.user)
        context['schedules'] = DoctorSchedule.objects.filter(doctor=request.user)
        context['template'] = 'users/doctor_panel.html'

    else:
        # Кабинет клиента
        context['appointments'] = Appointment.objects.filter(client=request.user)
        # Проверяем, может ли клиент оставить отзыв (есть завершённые приёмы без отзыва)
        from django.db.models import Q
        context['can_review'] = Appointment.objects.filter(
            client=request.user,
            status='COMPLETED',
            review__isnull=True
        ).exists()
        context['template'] = 'users/client_panel.html'

    return render(request, 'users/profile.html', context)