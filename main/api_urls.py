from django.urls import path
from . import views_api

urlpatterns = [
    path('news/', views_api.news_list, name='api-news-list'),
    path('news/<int:pk>/', views_api.news_detail, name='api-news-detail'),

    path('appointments/', views_api.appointment_list, name='api-appointments-list'),
    path('appointments/<int:pk>/', views_api.appointment_detail, name='api-appointments-detail'),

    path('reviews/', views_api.review_list, name='api-reviews-list'),
    path('reviews/<int:pk>/', views_api.review_detail, name='api-reviews-detail'),

    path('schedules/', views_api.schedule_list, name='api-schedules-list'),
    path('schedules/<int:pk>/', views_api.schedule_detail, name='api-schedules-detail'),

    path('users/', views_api.user_list, name='api-users-list'),
    path('users/<int:pk>/', views_api.user_detail, name='api-users-detail'),
]