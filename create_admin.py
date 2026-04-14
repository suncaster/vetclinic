import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vetclinic.settings')
django.setup()

from users.models import CustomUser

if not CustomUser.objects.filter(username='admin').exists():
    CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Admin created: admin / admin")
else:
    print("Admin already exists")