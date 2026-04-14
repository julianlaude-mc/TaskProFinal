import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Update admin user role
user = User.objects.get(username='admin')
user.role = 'admin'
user.save()
print(f"✓ Admin user role updated successfully!")
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Role: {user.role}")
