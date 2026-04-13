import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vetclinic.settings')
django.setup()

from users.models import CustomUser

if not CustomUser.objects.filter(username='admin').exists():
    CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Admin created: admin / admin123")
else:
    print("Admin already exists")