# Database Optimization Migration File
# This should be run as: python manage.py migrate
# Django automatically creates these indexes from model Meta.indexes

# Add the following to myapp/models.py in each model's Meta class:

"""
# Example for User model Meta class:
class Meta:
    verbose_name = "User"
    verbose_name_plural = "Users"
    indexes = [
        models.Index(fields=['email'], name='user_email_idx'),
        models.Index(fields=['role'], name='user_role_idx'),
        models.Index(fields=['status'], name='user_status_idx'),
        models.Index(fields=['date_created'], name='user_datecreated_idx'),
    ]

# Example for Project model Meta class:
class Meta:
    verbose_name = "Project"
    verbose_name_plural = "Projects"
    indexes = [
        models.Index(fields=['project_code'], name='project_code_idx'),
        models.Index(fields=['status'], name='project_status_idx'),
        models.Index(fields=['project_leader'], name='project_leader_idx'),
        models.Index(fields=['date_created'], name='project_datecreated_idx'),
        models.Index(fields=['year', 'status'], name='project_year_status_idx'),
    ]

# Example for Budget model Meta class:
class Meta:
    verbose_name = "Budget"
    verbose_name_plural = "Budgets"
    indexes = [
        models.Index(fields=['fiscal_year'], name='budget_fiscalyear_idx'),
        models.Index(fields=['status'], name='budget_status_idx'),
        models.Index(fields=['fund_source'], name='budget_fundsource_idx'),
    ]

# Example for Task model Meta class:
class Meta:
    verbose_name = "Task"
    verbose_name_plural = "Tasks"
    indexes = [
        models.Index(fields=['project'], name='task_project_idx'),
        models.Index(fields=['status'], name='task_status_idx'),
        models.Index(fields=['assigned_to'], name='task_assignedto_idx'),
        models.Index(fields=['due_date'], name='task_duedate_idx'),
        models.Index(fields=['priority'], name='task_priority_idx'),
    ]

# Example for Proposal model Meta class:
class Meta:
    verbose_name = "Proposal"
    verbose_name_plural = "Proposals"
    indexes = [
        models.Index(fields=['status'], name='proposal_status_idx'),
        models.Index(fields=['submitted_by'], name='proposal_submittedby_idx'),
        models.Index(fields=['submission_date'], name='proposal_submissiondate_idx'),
    ]

# Example for Message model Meta class:
class Meta:
    verbose_name = "Message"
    verbose_name_plural = "Messages"
    indexes = [
        models.Index(fields=['sender'], name='message_sender_idx'),
        models.Index(fields=['recipient'], name='message_recipient_idx'),
        models.Index(fields=['is_read'], name='message_isread_idx'),
        models.Index(fields=['created_at'], name='message_createdat_idx'),
    ]
"""

# DATABASE CONNECTION POOLING CONFIGURATION
# Add to myproject/settings.py for PostgreSQL:

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dost_taskpro',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        
        # Connection Pooling Settings
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed'
        },
        'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction
    }
}

# Alternative: Use pgBouncer for connection pooling
# Install: pip install pgbouncer
# Configure pgbouncer.ini:
# [databases]
# mydb = host=localhost port=5432 dbname=dost_taskpro
#
# [pgbouncer]
# pool_mode = transaction
# max_client_conn = 1000
# default_pool_size = 25
"""

# ==================== QUERY OPTIMIZATION GUIDE ====================

"""
BEST PRACTICES FOR DATABASE OPTIMIZATION:

1. USE .only() and .defer() TO FETCH SPECIFIC COLUMNS:
   # Bad: Fetches all columns
   users = User.objects.all()
   
   # Good: Fetch only needed columns
   users = User.objects.only('id', 'username', 'email')
   
2. USE SELECT_RELATED FOR FOREIGN KEYS:
   # Bad: N+1 problem
   projects = Project.objects.all()
   for project in projects:
       print(project.project_leader.username)  # Extra query per project
   
   # Good: Single query with joins
   projects = Project.objects.select_related('project_leader')
   
3. USE PREFETCH_RELATED FOR REVERSE FOREIGN KEYS & MANY-TO-MANY:
   # Bad: N+1 problem
   budgets = Budget.objects.all()
   for budget in budgets:
       proposals = budget.proposals.all()  # Extra query per budget
   
   # Good: Optimized with prefetch
   from django.db.models import Prefetch
   budgets = Budget.objects.prefetch_related('proposals')
   
4. USE AGGREGATION TO AVOID LOOP-BASED CALCULATIONS:
   # Bad: Python-level calculation
   total = sum(project.budget for project in Project.objects.all())
   
   # Good: Database-level aggregation
   from django.db.models import Sum
   total = Project.objects.aggregate(Sum('budget'))['budget__sum']
   
5. USE ANNOTATIONS FOR COMPUTED FIELDS:
   # Good: Add computed fields without extra queries
   from django.db.models import Count
   projects = Project.objects.annotate(
       task_count=Count('task'),
       budget_total=Sum('budget')
   )
   
6. BATCH INSERT/UPDATE FOR BULK OPERATIONS:
   # Bad: N queries for N objects
   for data in large_list:
       User.objects.create(**data)
   
   # Good: Single bulk operation
   users = [User(**data) for data in large_list]
   User.objects.bulk_create(users, batch_size=1000)
   
7. USE FILTER WITH DATABASE OPERATIONS:
   # Bad: Fetch all then filter in Python
   active_users = [u for u in User.objects.all() if u.status == 'active']
   
   # Good: Filter in database
   active_users = User.objects.filter(status='active')
"""
