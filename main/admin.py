from django.contrib import admin
from .models import News, Appointment, Review, DoctorSchedule

admin.site.register(News)
admin.site.register(Appointment)
admin.site.register(Review)
admin.site.register(DoctorSchedule)