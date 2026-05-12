import os
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from myapp.models import (
    User, Budget, Proposal, Project, Task, Message, GroupChat, 
    GroupChatMember, Announcement, ProjectEquipment, EquipmentCategory,
    EquipmentItem, TrancheRelease, ExtensionRequest
)

print("🔄 Starting dummy data injection...\n")

# ==================== CREATE USERS ====================
print("📝 Creating users...")
users_data = {
    'staff_users': [
        {'username': 'staff1', 'email': 'staff1@dost.gov.ph', 'first_name': 'Maria', 'last_name': 'Santos', 'role': 'dost_staff'},
        {'username': 'staff2', 'email': 'staff2@dost.gov.ph', 'first_name': 'Juan', 'last_name': 'Cruz', 'role': 'dost_staff'},
    ],
    'proponent_users': [
        {'username': 'proponent1', 'email': 'proponent1@example.com', 'first_name': 'Carlos', 'last_name': 'Reyes', 'role': 'proponent'},
        {'username': 'proponent2', 'email': 'proponent2@example.com', 'first_name': 'Ana', 'last_name': 'Gomez', 'role': 'proponent'},
        {'username': 'proponent3', 'email': 'proponent3@example.com', 'first_name': 'Pedro', 'last_name': 'Flores', 'role': 'proponent'},
    ],
    'beneficiary_users': [
        {'username': 'beneficiary1', 'email': 'beneficiary1@example.com', 'first_name': 'Rosa', 'last_name': 'Lopez', 'role': 'beneficiary'},
        {'username': 'beneficiary2', 'email': 'beneficiary2@example.com', 'first_name': 'Luis', 'last_name': 'Garcia', 'role': 'beneficiary'},
        {'username': 'beneficiary3', 'email': 'beneficiary3@example.com', 'first_name': 'Elena', 'last_name': 'Martinez', 'role': 'beneficiary'},
    ]
}

created_users = {}
all_users_list = []

for role_key, users in users_data.items():
    for user_data in users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'status': 'active',
            }
        )
        if created:
            user.set_password('test123')
            user.save()
        created_users[user_data['username']] = user
        all_users_list.append(user)
        print(f"  ✓ {user_data['username']} ({user_data['role']})")

# ==================== CREATE BUDGETS ====================
print("\n💰 Creating budgets...")
admin = User.objects.filter(role='admin').first()
budgets = []
for i in range(1, 4):
    budget, created = Budget.objects.get_or_create(
        fiscal_year=2025 + i,
        defaults={
            'fund_source': random.choice(['DOST_GIA', 'SETUP', 'LOCAL_REGIONAL']),
            'lib_category': random.choice(['PS', 'MOOE', 'EO_CO']),
            'total_allocated_items': random.randint(10, 50),
            'total_delivered_items': random.randint(0, 10),
            'total_equipment_value': Decimal(str(random.uniform(100000, 500000))).quantize(Decimal('0.01')),
            'delivered_equipment_value': Decimal(str(random.uniform(0, 100000))).quantize(Decimal('0.01')),
            'status': random.choice(['pending_procurement', 'available', 'partially_allocated', 'fully_allocated']),
            'created_by': admin,
        }
    )
    budgets.append(budget)
    if created:
        print(f"  ✓ Budget FY{budget.fiscal_year} - {budget.fund_source}")

# ==================== CREATE PROPOSALS ====================
print("\n📄 Creating proposals...")
proposal_titles = [
    "Agricultural Technology Transfer",
    "Aquaculture Development Program",
    "IT Skills Training Initiative",
    "Renewable Energy Installation",
    "Coconut Processing Equipment",
    "Livestock Management System",
]

proposals = []
for i, title in enumerate(proposal_titles):
    proposal, created = Proposal.objects.get_or_create(
        title=title,
        defaults={
            'description': f"Proposal for {title} targeting development in Biliran Province.",
            'submitted_by': created_users.get('proponent1'),
            'proponent': created_users.get('proponent1'),
            'status': random.choice(['pending', 'for_review', 'approved', 'rejected']),
            'proposed_amount': Decimal(str(random.uniform(50000, 300000))).quantize(Decimal('0.01')),
            'approved_amount': Decimal(str(random.uniform(40000, 250000))).quantize(Decimal('0.01')),
            'budget': budgets[i % len(budgets)],
            'beneficiaries': f"Beneficiary Name {i+1}",
            'location': 'Biliran Province',
            'municipality': random.choice(['Naval', 'Caibiran', 'Maripipi']),
            'province': 'Biliran',
            'latitude': 11.5 + random.uniform(-0.5, 0.5),
            'longitude': 124.5 + random.uniform(-0.5, 0.5),
        }
    )
    proposals.append(proposal)
    if created:
        print(f"  ✓ {title}")

# ==================== CREATE PROJECTS ====================
print("\n🏗️  Creating projects...")
projects = []
for i in range(1, 6):
    project, created = Project.objects.get_or_create(
        project_code=f"DOST-2025-{i:03d}",
        defaults={
            'project_title': f"Development Project {i}",
            'project_description': f"Comprehensive development project for technology transfer in Biliran",
            'beneficiary': f"Community {i}",
            'beneficiary_address': f"Brgy. San {i}, Naval, Biliran",
            'no_of_beneficiaries': random.randint(5, 50),
            'status': random.choice(['active', 'completed', 'on-hold']),
            'year': 2025,
            'fund_source': 'DOST',
            'project_start': timezone.now().date(),
            'project_end': timezone.now().date() + timedelta(days=365),
            'funds': Decimal(str(random.uniform(100000, 500000))).quantize(Decimal('0.01')),
            'proposal': proposals[i-1] if i <= len(proposals) else None,
            'budget': budgets[i % len(budgets)],
            'project_leader': created_users.get('staff1'),
            'male': random.randint(5, 25),
            'female': random.randint(5, 25),
            'total_beneficiaries': random.randint(10, 50),
        }
    )
    projects.append(project)
    if created:
        print(f"  ✓ {project.project_code}: {project.project_title}")

# ==================== CREATE TASKS ====================
print("\n📋 Creating tasks...")
task_names = [
    "Equipment Procurement",
    "Site Preparation",
    "Training Coordination",
    "Documentation",
    "Field Visit",
]

for project in projects[:3]:
    for i, task_name in enumerate(task_names):
        task, created = Task.objects.get_or_create(
            project=project,
            title=task_name,
            defaults={
                'description': f"{task_name} for {project.project_title}",
                'assigned_to': created_users.get('staff1'),
                'status': random.choice(['pending', 'in_progress', 'completed']),
                'priority': random.choice(['low', 'medium', 'high']),
                'due_date': timezone.now().date() + timedelta(days=random.randint(7, 60)),
                'category': 'general',
            }
        )
        if created:
            print(f"  ✓ Task: {task_name} for {project.project_code}")

# ==================== CREATE EQUIPMENT CATEGORIES ====================
print("\n🔧 Creating equipment categories and items...")
equipment_categories = [
    ('Agricultural Equipment', 'Farming and cultivation tools'),
    ('IT Equipment', 'Computers and digital devices'),
    ('Processing Equipment', 'Industrial processing machinery'),
    ('Energy Equipment', 'Power generation systems'),
]

for cat_name, cat_desc in equipment_categories:
    category, created = EquipmentCategory.objects.get_or_create(
        name=cat_name,
        defaults={'description': cat_desc}
    )
    if created:
        print(f"  ✓ Category: {cat_name}")
    
    # Create equipment items for category
    items = [
        ('Tractor 60hp', 'Heavy equipment for agricultural use'),
        ('Irrigation Pump', 'Water pump system for irrigation'),
        ('Desktop Computer', 'High-performance desktop workstation'),
        ('Laptop', 'Mobile computing device'),
        ('Rice Mill', 'Industrial rice processing equipment'),
        ('Solar Panel', 'Photovoltaic power generation unit'),
    ]
    
    for item_name, item_desc in items:
        item, created = EquipmentItem.objects.get_or_create(
            name=item_name,
            category=category,
            defaults={
                'description': item_desc,
                'unit': 'pieces',
                'estimated_unit_cost': Decimal(str(random.uniform(5000, 200000))).quantize(Decimal('0.01')),
                'specifications': f'Item specifications for {item_name}',
            }
        )
        if created:
            print(f"    ✓ Item: {item_name}")

# ==================== CREATE ANNOUNCEMENTS ====================
print("\n📢 Creating announcements...")
announcements = [
    "System Maintenance scheduled for next Sunday",
    "New Equipment arrived for distribution",
    "Reminder: Project reports due this week",
    "Training session scheduled for beneficiaries",
]

for announcement_text in announcements:
    announcement, created = Announcement.objects.get_or_create(
        title=announcement_text[:100],
        defaults={
            'content': announcement_text,
            'created_by': admin,
            'priority': random.choice(['low', 'normal', 'high', 'urgent']),
            'is_active': True,
        }
    )
    if created:
        print(f"  ✓ {announcement_text[:50]}...")

# ==================== CREATE MESSAGES ====================
print("\n💬 Creating messages...")
for i in range(3):
    sender = created_users.get('staff1')
    recipient = created_users.get('proponent1')
    message, created = Message.objects.get_or_create(
        sender=sender,
        recipient=recipient,
        subject=f"Project Update {i+1}",
        defaults={
            'content': f"This is message {i+1} regarding project progress and next steps.",
            'is_read': False,
            'created_at': timezone.now() - timedelta(days=i),
        }
    )
    if created:
        print(f"  ✓ Message from {sender.username} to {recipient.username}")

print("\n" + "="*50)
print("✅ Dummy data injection completed successfully!")
print("="*50)
print("\n📊 Summary:")
print(f"  • Users created: {User.objects.count()}")
print(f"  • Budgets created: {Budget.objects.count()}")
print(f"  • Proposals created: {Proposal.objects.count()}")
print(f"  • Projects created: {Project.objects.count()}")
print(f"  • Tasks created: {Task.objects.count()}")
print(f"  • Equipment Categories: {EquipmentCategory.objects.count()}")
print(f"  • Equipment Items: {EquipmentItem.objects.count()}")
print(f"  • Announcements: {Announcement.objects.count()}")
print(f"  • Messages: {Message.objects.count()}")
