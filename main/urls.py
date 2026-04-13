from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('appointment/create/', views.appointment_create, name='appointment_create'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<int:pk>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('appointment/<int:pk>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointment/<int:pk>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('review/create/<int:appointment_id>/', views.create_review, name='create_review'),
    path('review/<int:pk>/moderate/', views.moderate_review, name='moderate_review'),
    path('news/create/', views.create_news, name='create_news'),
    path('news/<int:pk>/edit/', views.edit_news, name='edit_news'),
    path('news/<int:pk>/delete/', views.delete_news, name='delete_news'),
    path('schedule/add/', views.add_schedule, name='add_schedule'),
    path('user/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('api/available-slots/<int:doctor_id>/', views.get_available_slots, name='api_available_slots'),
]