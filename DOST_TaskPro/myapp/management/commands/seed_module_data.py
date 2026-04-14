import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from myapp.models import (
    Announcement,
    Budget,
    EquipmentCategory,
    EquipmentItem,
    ExtensionRequest,
    GroupChat,
    GroupChatMember,
    GroupChatMessage,
    Message,
    Notification,
    Project,
    Proposal,
    Task,
    User,
)


class Command(BaseCommand):
    help = "Seed demo data across modules, ensuring at least N records per core model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=25,
            help="Target minimum records per module (default: 25)",
        )

    def handle(self, *args, **options):
        target = max(1, int(options["count"]))
        now = timezone.now()

        admin = self._ensure_admin_user()
        staff_users = self._ensure_users("dost_staff", target)
        proponents = self._ensure_users("proponent", target)
        beneficiaries = self._ensure_users("beneficiary", target)
        everyone = [admin] + staff_users + proponents + beneficiaries

        self._ensure_budgets(target, admin)
        budgets = list(Budget.objects.all())

        self._ensure_proposals(target, budgets, proponents, beneficiaries, staff_users)
        proposals = list(Proposal.objects.all().select_related("proponent", "submitted_by", "beneficiary"))

        self._ensure_projects(target, proposals, budgets, staff_users, now)
        projects = list(Project.objects.all())

        self._ensure_tasks(target, projects, staff_users, now)
        self._ensure_extension_requests(target, proposals, proponents, admin, now)
        self._ensure_messages(target, everyone, now)
        self._ensure_announcements(target, admin, everyone, now)
        self._ensure_notifications(target, everyone, now)
        self._ensure_equipment(target)
        self._ensure_group_chats(target, projects, everyone, now)

        summary = {
            "users": User.objects.count(),
            "budgets": Budget.objects.count(),
            "proposals": Proposal.objects.count(),
            "projects": Project.objects.count(),
            "tasks": Task.objects.count(),
            "extension_requests": ExtensionRequest.objects.count(),
            "messages": Message.objects.count(),
            "announcements": Announcement.objects.count(),
            "notifications": Notification.objects.count(),
            "equipment_categories": EquipmentCategory.objects.count(),
            "equipment_items": EquipmentItem.objects.count(),
            "group_chats": GroupChat.objects.count(),
            "group_messages": GroupChatMessage.objects.count(),
        }

        self.stdout.write(self.style.SUCCESS("Demo module seeding completed."))
        for key, value in summary.items():
            self.stdout.write(f"  {key}: {value}")

    def _ensure_admin_user(self):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@gmail.com",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "status": "active",
            },
        )
        changed = False
        if admin.role != "admin":
            admin.role = "admin"
            changed = True
        if not admin.is_staff:
            admin.is_staff = True
            changed = True
        if not admin.is_superuser:
            admin.is_superuser = True
            changed = True
        if created or not admin.has_usable_password():
            admin.set_password("admin123")
            changed = True
        if changed:
            admin.save()
        return admin

    def _ensure_users(self, role, target):
        users = list(User.objects.filter(role=role)[:target])
        needed = target - len(users)
        if needed <= 0:
            return users

        base = {
            "dost_staff": ("staff", "staff"),
            "proponent": ("proponent", "proponent"),
            "beneficiary": ("beneficiary", "beneficiary"),
        }
        username_prefix, email_prefix = base[role]

        for _ in range(needed):
            while True:
                suffix = random.randint(1000, 999999)
                username = f"{username_prefix}_{suffix}"
                email = f"{email_prefix}_{suffix}@taskpro.local"
                if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                    break

            user = User.objects.create(
                username=username,
                email=email,
                role=role,
                is_staff=(role in {"dost_staff", "admin"}),
                status="active",
                first_name=username_prefix.capitalize(),
                last_name=str(suffix),
            )
            user.set_password("password123")
            user.save(update_fields=["password"])
            users.append(user)

        return users

    def _ensure_budgets(self, target, admin):
        current = Budget.objects.count()
        needed = target - current
        if needed <= 0:
            return

        statuses = ["pending_procurement", "available", "partially_allocated", "fully_allocated", "completed"]
        sources = ["DOST_GIA", "SETUP", "LOCAL_REGIONAL", "OTHER"]
        libs = ["PS", "MOOE", "EO_CO"]
        year = timezone.now().year

        for i in range(needed):
            Budget.objects.create(
                fiscal_year=year + (i % 3),
                fund_source=sources[i % len(sources)],
                lib_category=libs[i % len(libs)],
                total_allocated_items=50 + i,
                total_delivered_items=10 + (i % 10),
                total_equipment_value=Decimal("500000.00") + (Decimal(i) * Decimal("25000.00")),
                delivered_equipment_value=Decimal("100000.00") + (Decimal(i) * Decimal("5000.00")),
                counterpart_contribution="LGU support",
                counterpart_value=Decimal("50000.00") + (Decimal(i) * Decimal("1000.00")),
                status=statuses[i % len(statuses)],
                created_by=admin,
            )

    def _ensure_proposals(self, target, budgets, proponents, beneficiaries, staff_users):
        current = Proposal.objects.count()
        needed = target - current
        if needed <= 0:
            return

        statuses = ["pending", "for_review", "needs_revision", "rejected"]
        municipalities = ["Naval", "Biliran", "Caibiran", "Cabucgayan", "Culaba", "Almeria", "Kawayan", "Maripipi"]

        for i in range(needed):
            proponent = proponents[i % len(proponents)]
            beneficiary = beneficiaries[i % len(beneficiaries)]
            submitted_by = staff_users[i % len(staff_users)] if staff_users else proponent
            municipality = municipalities[i % len(municipalities)]
            Proposal.objects.create(
                title=f"Demo Proposal {timezone.now().strftime('%Y%m%d')}-{i+1}",
                description="Autogenerated demo proposal for module testing.",
                submitted_by=submitted_by,
                status=statuses[i % len(statuses)],
                proposed_amount=Decimal("150000.00") + (Decimal(i) * Decimal("3000.00")),
                approved_amount=None,
                budget=budgets[i % len(budgets)] if budgets else None,
                processed_by=submitted_by,
                beneficiary=beneficiary,
                proponent=proponent,
                beneficiaries=f"Beneficiary Cluster {i+1}",
                location=f"{municipality}, Biliran",
                municipality=municipality,
                province="Biliran",
                latitude=11.50 + (i * 0.005),
                longitude=124.40 + (i * 0.005),
            )

    def _ensure_projects(self, target, proposals, budgets, staff_users, now):
        current = Project.objects.count()
        needed = target - current
        if needed <= 0:
            return

        statuses = ["new", "ongoing", "completed", "terminated"]
        municipalities = ["Naval", "Biliran", "Caibiran", "Cabucgayan", "Culaba", "Almeria", "Kawayan", "Maripipi"]

        free_proposals = [p for p in proposals if not hasattr(p, "project")]

        for i in range(needed):
            proposal = free_proposals[i] if i < len(free_proposals) else None
            municipality = municipalities[i % len(municipalities)]
            status = statuses[i % len(statuses)]
            start = (now - timedelta(days=30 + i)).date()
            end = (now + timedelta(days=90 + i)).date()
            if status == "completed":
                end = (now - timedelta(days=1 + i)).date()

            Project.objects.create(
                no=Project.objects.count() + 1,
                project_code=f"DEMO-{now.strftime('%Y%m%d')}-{Project.objects.count()+1:04d}",
                year=now.year,
                agency_grantee="DOST PSTO Biliran",
                mun=municipality,
                province="Biliran",
                district=f"District {(i % 2) + 1}",
                project_title=f"Demo Project {now.strftime('%Y%m%d')}-{i+1}",
                project_description="Autogenerated demo project for end-to-end testing.",
                beneficiary=f"Community Group {i+1}",
                beneficiary_address=f"{municipality}, Biliran",
                contact_details=f"0917{random.randint(1000000, 9999999)}",
                proponent_details="Demo Proponent",
                no_of_beneficiaries=30 + i,
                program="SETUP",
                status=status,
                remarks="Demo seed data",
                fund_source="DOST_GIA",
                original_project_duration="12 months",
                project_start=start,
                project_end=end,
                date_of_release=start,
                date_of_completion=end if status == "completed" else None,
                type_of_project="Equipment Assistance",
                funds=Decimal("300000.00") + (Decimal(i) * Decimal("7000.00")),
                first_tranche=Decimal("100000.00"),
                second_tranche=Decimal("100000.00"),
                third_tranche=Decimal("100000.00"),
                counterpart_funds=Decimal("50000.00"),
                total_project_cost=Decimal("350000.00") + (Decimal(i) * Decimal("7000.00")),
                total_funds_released=Decimal("150000.00"),
                tafr="Yes",
                par="Pending",
                terminal_report="No",
                invoice_receipt="Pending",
                donated="No",
                male=15 + i,
                female=15 + i,
                total_beneficiaries=30 + (i * 2),
                senior_citizen=2 + (i % 4),
                pwd=1 + (i % 3),
                proposal=proposal,
                budget=budgets[i % len(budgets)] if budgets else None,
                project_leader=staff_users[i % len(staff_users)] if staff_users else None,
                latitude=11.50 + (i * 0.006),
                longitude=124.40 + (i * 0.006),
            )

    def _ensure_tasks(self, target, projects, staff_users, now):
        current = Task.objects.count()
        needed = target - current
        if needed <= 0 or not projects:
            return

        statuses = ["pending", "in_progress", "completed", "delayed", "on_track", "behind_schedule", "at_risk"]
        priorities = ["critical", "high", "medium", "low"]
        categories = ["planning", "development", "testing", "documentation", "review", "deployment", "maintenance", "other"]

        for i in range(needed):
            project = projects[i % len(projects)]
            assigned_to = staff_users[i % len(staff_users)] if staff_users else None
            due_date = (now + timedelta(days=7 + i)).date()
            status = statuses[i % len(statuses)]
            completion_date = None
            if status == "completed":
                completion_date = (now - timedelta(days=1 + (i % 5))).date()

            Task.objects.create(
                project=project,
                title=f"Demo Task {i+1} for {project.project_code or project.id}",
                description="Autogenerated task for workflow testing.",
                assigned_to=assigned_to,
                start_date=(now - timedelta(days=3)).date(),
                due_date=due_date,
                completion_date=completion_date,
                latitude=project.latitude,
                longitude=project.longitude,
                location_name=project.mun,
                status=status,
                priority=priorities[i % len(priorities)],
                category=categories[i % len(categories)],
                progress_percentage=(i * 7) % 101,
                estimated_hours=Decimal("4.00") + Decimal(i % 6),
                actual_hours=Decimal("2.00") + Decimal(i % 5),
            )

    def _ensure_extension_requests(self, target, proposals, proponents, admin, now):
        current = ExtensionRequest.objects.count()
        needed = target - current
        if needed <= 0 or not proposals or not proponents:
            return

        statuses = ["pending", "approved", "rejected"]
        reasons = [
            "Weather delays affected implementation schedule.",
            "Supplier delays for critical equipment.",
            "Additional community validation required.",
            "Technical adjustment and retraining needed.",
        ]

        for i in range(needed):
            proposal = proposals[i % len(proposals)]
            proponent = proposal.proponent if proposal.proponent else proponents[i % len(proponents)]
            status = statuses[i % len(statuses)]
            req = ExtensionRequest.objects.create(
                proposal=proposal,
                proponent=proponent,
                reason=reasons[i % len(reasons)],
                requested_extension_days=7 + (i % 45),
                status=status,
                remarks="Auto-seeded for testing.",
                approved_days=(7 + (i % 30)) if status == "approved" else None,
                approved_by=admin if status in {"approved", "rejected"} else None,
                date_approved=(now - timedelta(days=i % 10)) if status in {"approved", "rejected"} else None,
            )
            req.date_submitted = now - timedelta(days=i)
            req.save(update_fields=["date_submitted"])

    def _ensure_messages(self, target, users, now):
        current = Message.objects.count()
        needed = target - current
        if needed <= 0 or len(users) < 2:
            return

        for i in range(needed):
            sender = users[i % len(users)]
            recipient = users[(i + 1) % len(users)]
            msg = Message.objects.create(
                sender=sender,
                recipient=recipient,
                subject=f"Demo Message {i+1}",
                content="Autogenerated direct message for module testing.",
                message_type="direct",
                is_read=(i % 3 == 0),
                is_archived=False,
            )
            msg.created_at = now - timedelta(minutes=i)
            msg.save(update_fields=["created_at"])

    def _ensure_announcements(self, target, admin, users, now):
        current = Announcement.objects.count()
        needed = target - current
        if needed <= 0:
            return

        priorities = ["low", "normal", "high", "urgent"]
        roles_pool = [[], ["dost_staff"], ["proponent"], ["beneficiary"], ["dost_staff", "proponent"]]

        for i in range(needed):
            ann = Announcement.objects.create(
                title=f"Demo Announcement {now.strftime('%Y%m%d')}-{i+1}",
                content="Autogenerated announcement for notifications and dashboard testing.",
                priority=priorities[i % len(priorities)],
                created_by=admin,
                is_active=True,
                expires_at=now + timedelta(days=30 + i),
                target_roles=roles_pool[i % len(roles_pool)],
            )
            if i % 4 == 0 and users:
                ann.target_users.add(users[i % len(users)])

    def _ensure_notifications(self, target, users, now):
        current = Notification.objects.count()
        needed = target - current
        if needed <= 0 or len(users) < 2:
            return

        categories = ["general", "task", "project", "chat", "announcement", "budget", "proposal"]
        for i in range(needed):
            sender = users[i % len(users)]
            receiver = users[(i + 2) % len(users)]
            Notification.objects.create(
                sender=sender,
                receiver=receiver,
                message=f"Demo notification {i+1}",
                category=categories[i % len(categories)],
                link="/",
                status="read" if i % 3 == 0 else "unread",
                timestamp=now - timedelta(hours=i),
            )

    def _ensure_equipment(self, target):
        category_names = [
            "Agricultural Equipment",
            "ICT Equipment",
            "Food Processing Equipment",
            "Renewable Energy Equipment",
            "Laboratory Equipment",
        ]

        categories = []
        for name in category_names:
            category, _ = EquipmentCategory.objects.get_or_create(name=name, defaults={"description": f"{name} category"})
            categories.append(category)

        current = EquipmentItem.objects.count()
        needed = target - current
        if needed <= 0:
            return

        units = ["pieces", "sets", "units", "kg", "liters", "meters", "boxes", "packs"]
        base_name = timezone.now().strftime("%Y%m%d")

        for i in range(needed):
            category = categories[i % len(categories)]
            name = f"Demo Item {base_name}-{i+1}"
            EquipmentItem.objects.get_or_create(
                name=name,
                category=category,
                defaults={
                    "description": "Autogenerated equipment item.",
                    "unit": units[i % len(units)],
                    "estimated_unit_cost": Decimal("1000.00") + (Decimal(i) * Decimal("250.00")),
                    "specifications": "Standard test specification",
                },
            )

    def _ensure_group_chats(self, target, projects, users, now):
        if not projects or not users:
            return

        current_chats = GroupChat.objects.count()
        needed_chats = target - current_chats
        chats = list(GroupChat.objects.all())

        for i in range(max(0, needed_chats)):
            creator = users[i % len(users)]
            project = projects[i % len(projects)]
            chat = GroupChat.objects.create(
                name=f"Demo Group Chat {now.strftime('%Y%m%d')}-{i+1}",
                description="Autogenerated group chat for communication module testing.",
                project=project,
                created_by=creator,
                is_active=True,
            )
            chats.append(chat)

            GroupChatMember.objects.get_or_create(group_chat=chat, user=creator, defaults={"role": "admin", "is_active": True})
            peer = users[(i + 1) % len(users)]
            GroupChatMember.objects.get_or_create(group_chat=chat, user=peer, defaults={"role": "member", "is_active": True})

        current_group_messages = GroupChatMessage.objects.count()
        needed_group_messages = target - current_group_messages
        if needed_group_messages <= 0 or not chats:
            return

        for i in range(needed_group_messages):
            chat = chats[i % len(chats)]
            members = list(chat.members.select_related("user"))
            if not members:
                continue
            sender = members[i % len(members)].user
            msg = GroupChatMessage.objects.create(
                group_chat=chat,
                sender=sender,
                content=f"Demo group message {i+1}",
                is_edited=False,
            )
            msg.created_at = now - timedelta(minutes=i)
            msg.save(update_fields=["created_at"])