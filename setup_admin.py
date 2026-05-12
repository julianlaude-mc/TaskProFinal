import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete any existing user with admin@gmail.com email
User.objects.filter(email='admin@gmail.com').delete()

# Create new admin user
User.objects.create_superuser('admin', 'admin123', email='admin@gmail.com')
print("✓ Admin user created successfully!")

print("Username: admin")
print("Email: admin@gmail.com")
print("Password: admin123")
