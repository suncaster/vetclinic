from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import News, Appointment, Review, DoctorSchedule
from users.models import CustomUser
from .serializers import *


@api_view(['GET', 'POST'])
def news_list(request):
    if request.method == 'GET':
        news = News.objects.filter(is_active=True)
        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.role == 'ADMIN':
            serializer = NewsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'PUT', 'DELETE'])
def news_detail(request, pk):
    try:
        news = News.objects.get(pk=pk)
    except News.DoesNotExist:
        return Response({'error': 'Новость не найдена'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = NewsSerializer(news)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if request.user.is_authenticated and request.user.role == 'ADMIN':
            serializer = NewsSerializer(news, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'DELETE':
        if request.user.is_authenticated and request.user.role == 'ADMIN':
            news.delete()
            return Response({'message': 'Новость удалена'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


# ============ APPOINTMENTS API ============
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    if request.method == 'GET':
        if request.user.role == 'ADMIN':
            appointments = Appointment.objects.all()
        elif request.user.role == 'DOCTOR':
            appointments = Appointment.objects.filter(doctor=request.user)
        else:
            appointments = Appointment.objects.filter(client=request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({'error': 'Запись не найдена'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if request.user.role in ['ADMIN', 'DOCTOR']:
            serializer = AppointmentSerializer(appointment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'DELETE':
        if request.user.role == 'ADMIN' or appointment.client == request.user:
            appointment.delete()
            return Response({'message': 'Запись удалена'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


# ============ REVIEWS API ============
@api_view(['GET', 'POST'])
def review_list(request):
    if request.method == 'GET':
        reviews = Review.objects.filter(status='APPROVED')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.is_authenticated:
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(client=request.user, status='PENDING')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Требуется авторизация'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'DELETE'])
def review_detail(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Отзыв не найден'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if request.user.is_authenticated and (request.user.role == 'ADMIN' or review.client == request.user):
            review.delete()
            return Response({'message': 'Отзыв удалён'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


# ============ SCHEDULE API ============
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def schedule_list(request):
    if request.method == 'GET':
        if request.user.role == 'DOCTOR':
            schedules = DoctorSchedule.objects.filter(doctor=request.user)
        else:
            schedules = DoctorSchedule.objects.filter(is_available=True)
        serializer = DoctorScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.role == 'DOCTOR':
            serializer = DoctorScheduleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(doctor=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Только врач может добавлять расписание'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def schedule_detail(request, pk):
    try:
        schedule = DoctorSchedule.objects.get(pk=pk)
    except DoctorSchedule.DoesNotExist:
        return Response({'error': 'Расписание не найдено'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DoctorScheduleSerializer(schedule)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if schedule.doctor == request.user or request.user.role == 'ADMIN':
            serializer = DoctorScheduleSerializer(schedule, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'DELETE':
        if schedule.doctor == request.user or request.user.role == 'ADMIN':
            schedule.delete()
            return Response({'message': 'Расписание удалено'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


# ============ USERS API ============
@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_list(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAdminUser])
def user_detail(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        user.delete()
        return Response({'message': 'Пользователь удалён'}, status=status.HTTP_204_NO_CONTENT)