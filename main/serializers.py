from rest_framework import serializers
from .models import News, Appointment, Review, DoctorSchedule
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'phone']


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.username')
    doctor_name = serializers.ReadOnlyField(source='doctor.username')

    class Meta:
        model = Appointment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.username')

    class Meta:
        model = Review
        fields = '__all__'


class DoctorScheduleSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.username')

    class Meta:
        model = DoctorSchedule
        fields = '__all__'