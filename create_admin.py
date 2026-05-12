import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin user already exists
if User.objects.filter(username='admin').exists():
    print("Admin user already exists. Deleting and recreating...")
    User.objects.filter(username='admin').delete()

# Create superuser
User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123')
print("✓ Superuser created successfully!")
print("Username: admin")
print("Email: admin@gmail.com")
print("Password: admin123")
