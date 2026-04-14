from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from myapp.models import Budget, Project, Proposal, Task, User


class Command(BaseCommand):
    help = "Seed demo data for staff/proponent/beneficiary dashboards."

    PROPOSAL_COUNT = 40
    APPROVED_PROJECT_TARGET = 20
    TASKS_PER_PROJECT = 5

    def handle(self, *args, **options):
        users = self._get_or_create_demo_users()
        budget = self._get_or_create_demo_budget()
        proposals = self._create_demo_proposals(users, budget)
        projects = self._create_demo_projects(proposals, budget)
        tasks = self._create_demo_tasks(projects, users["staff"])

        self.stdout.write(self.style.SUCCESS(
            "Seeded demo dashboard data. "
            f"Proposals: {len(proposals)}, Projects: {len(projects)}, Tasks: {len(tasks)}."
        ))

    def _get_or_create_demo_users(self):
        staff = self._get_or_create_user(
            username="staff_demo",
            email="staff_demo@example.com",
            role="dost_staff",
            first_name="Staff",
            last_name="Demo",
            is_staff=True,
        )
        proponent = self._get_or_create_user(
            username="proponent_demo",
            email="proponent_demo@example.com",
            role="proponent",
            first_name="Proponent",
            last_name="Demo",
            is_staff=False,
        )
        beneficiary = self._get_or_create_user(
            username="beneficiary_demo",
            email="beneficiary_demo@example.com",
            role="beneficiary",
            first_name="Beneficiary",
            last_name="Demo",
            is_staff=False,
        )
        return {"staff": staff, "proponent": proponent, "beneficiary": beneficiary}

    def _get_or_create_user(self, username, email, role, first_name, last_name, is_staff):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": role,
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": is_staff,
            },
        )
        user.email = email
        user.role = role
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = is_staff
        if created or not user.has_usable_password():
            user.set_password("password123")
        user.save()
        return user

    def _get_or_create_demo_budget(self):
        budget = Budget.objects.filter(status__in=["active", "available", "partially_allocated"]).first()
        if budget:
            return budget
        return Budget.objects.create(
            fiscal_year=timezone.now().year,
            fund_source="DOST_GIA",
            lib_category="MOOE",
            total_equipment_value=Decimal("1500000.00"),
            delivered_equipment_value=Decimal("350000.00"),
            status="available",
        )

    def _create_demo_proposals(self, users, budget):
        proponent = users["proponent"]
        beneficiary = users["beneficiary"]

        proposals = []
        project_titles = [
            "Biliran Seaweed Value Chain Support",
            "Naval Coconut Processing Hub",
            "Culaba Food Innovation Center",
            "Maripipi Fisheries Cold Storage",
            "Kawayan Agri-Mechanization Upgrade",
            "Caibiran Community Weaving Studio",
            "Cabucgayan Rice Milling Enhancement",
            "Almeria Solar Dryer Expansion",
            "Biliran MSME Packaging Facility",
            "Naval ICT Skills Lab",
            "Culaba Coffee Roasting Facility",
            "Maripipi Sea Cucumber Hatchery",
            "Kawayan Livelihood Training Center",
            "Caibiran Bamboo Craft Development",
            "Cabucgayan Fish Processing Line",
            "Almeria Cassava Processing Plant",
            "Biliran Organic Fertilizer Hub",
            "Naval Smart Irrigation Pilot",
            "Culaba Aqua Feed Production",
            "Maripipi Boat Repair Workshop",
            "Kawayan Honey Processing Unit",
            "Caibiran Dairy Value Chain",
            "Cabucgayan Coco Sugar Facility",
            "Almeria Textile Finishing Lab",
            "Biliran Community Innovation Center",
            "Naval Fisheries Training Academy",
            "Culaba Shared Service Facility",
            "Maripipi Seedling Nursery",
            "Kawayan Post-Harvest Facility",
            "Caibiran Coastal Monitoring Center",
            "Cabucgayan S&T Learning Hub",
            "Almeria Sustainable Energy Demo",
            "Biliran Tech Transfer Clinic",
            "Naval Water Quality Lab",
            "Culaba Market Access Program",
            "Maripipi Women Enterprise Center",
        ]
        status_cycle = [
            "pending",
            "for_review",
            "approved",
            "rejected",
            "needs_revision",
            "approved",
            "approved",
            "for_review",
        ]
        municipality_cycle = [
            "Naval",
            "Caibiran",
            "Biliran",
            "Culaba",
            "Kawayan",
            "Maripipi",
            "Cabucgayan",
            "Almeria",
        ]
        programs = ["SETUP", "GIA", "CEST", "STARBOOKS", "TAPI"]
        project_types = ["Equipment Assistance", "Training", "Facility Upgrade", "Research", "ICT Support"]
        beneficiaries = [
            "Farmers Cooperative",
            "Women Entrepreneurs",
            "Fisherfolk Association",
            "Youth Tech Hub",
            "MSME Cluster",
        ]

        for idx in range(1, self.PROPOSAL_COUNT + 1):
            status = "approved" if idx <= self.APPROVED_PROJECT_TARGET else status_cycle[(idx - 1) % len(status_cycle)]
            municipality = municipality_cycle[(idx - 1) % len(municipality_cycle)]
            title = f"{project_titles[(idx - 1) % len(project_titles)]} Proposal"
            proposal, _ = Proposal.objects.get_or_create(
                title=title,
                proponent=proponent,
                defaults={
                    "description": f"Project proposal for {project_titles[(idx - 1) % len(project_titles)]}.",
                    "submitted_by": proponent,
                    "status": status,
                    "proposed_amount": Decimal("150000.00") + (idx * Decimal("20000.00")),
                    "approved_amount": Decimal("120000.00") + (idx * Decimal("15000.00")),
                    "budget": budget,
                    "beneficiary": beneficiary,
                    "municipality": municipality,
                    "province": "Biliran",
                    "latitude": 11.45 + (idx * 0.015),
                    "longitude": 124.35 + (idx * 0.015),
                    "program": programs[(idx - 1) % len(programs)],
                    "type_of_project": project_types[(idx - 1) % len(project_types)],
                    "beneficiaries": beneficiaries[(idx - 1) % len(beneficiaries)],
                },
            )
            if proposal.status != status:
                proposal.status = status
                proposal.save(update_fields=["status"])
            proposals.append(proposal)
        return proposals

    def _create_demo_projects(self, proposals, budget):
        projects = []
        project_titles = [
            "Biliran Seaweed Value Chain Support",
            "Naval Coconut Processing Hub",
            "Culaba Food Innovation Center",
            "Maripipi Fisheries Cold Storage",
            "Kawayan Agri-Mechanization Upgrade",
            "Caibiran Community Weaving Studio",
            "Cabucgayan Rice Milling Enhancement",
            "Almeria Solar Dryer Expansion",
            "Biliran MSME Packaging Facility",
            "Naval ICT Skills Lab",
            "Culaba Coffee Roasting Facility",
            "Maripipi Sea Cucumber Hatchery",
            "Kawayan Livelihood Training Center",
            "Caibiran Bamboo Craft Development",
            "Cabucgayan Fish Processing Line",
            "Almeria Cassava Processing Plant",
            "Biliran Organic Fertilizer Hub",
            "Naval Smart Irrigation Pilot",
            "Culaba Aqua Feed Production",
            "Maripipi Boat Repair Workshop",
            "Kawayan Honey Processing Unit",
            "Caibiran Dairy Value Chain",
            "Cabucgayan Coco Sugar Facility",
            "Almeria Textile Finishing Lab",
            "Biliran Community Innovation Center",
            "Naval Fisheries Training Academy",
            "Culaba Shared Service Facility",
            "Maripipi Seedling Nursery",
            "Kawayan Post-Harvest Facility",
            "Caibiran Coastal Monitoring Center",
            "Cabucgayan S&T Learning Hub",
            "Almeria Sustainable Energy Demo",
            "Biliran Tech Transfer Clinic",
            "Naval Water Quality Lab",
            "Culaba Market Access Program",
            "Maripipi Women Enterprise Center",
        ]
        status_cycle = ["ongoing", "completed", "terminated", "ongoing", "new"]
        programs = ["SETUP", "GIA", "CEST", "STARBOOKS", "TAPI"]
        project_types = ["Equipment Assistance", "Training", "Facility Upgrade", "Research", "ICT Support"]
        fund_sources = ["DOST_GIA", "DOST_SETUP", "Provincial S&T Fund", "Regional Grant"]
        districts = ["1st District", "2nd District"]
        remarks = ["On track", "Needs monitoring", "Delayed due to procurement", "Awaiting reports"]
        liquidation_statuses = ["pending", "partial", "approved"]
        yes_no_pending = ["Yes", "No", "Pending"]
        donation_statuses = ["Pending", "Completed", "In Review"]

        approved = [p for p in proposals if p.status == "approved"]
        for idx, proposal in enumerate(approved, start=1):
            if Project.objects.filter(proposal=proposal).exists():
                projects.append(Project.objects.get(proposal=proposal))
                continue

            status = status_cycle[(idx - 1) % len(status_cycle)]
            project_end = timezone.now().date() + timezone.timedelta(days=120)
            if status == "completed":
                project_end = timezone.now().date() - timezone.timedelta(days=10)

            total_beneficiaries = 40 + (idx * 5)
            male = int(total_beneficiaries * 0.45)
            female = total_beneficiaries - male

            title = project_titles[(idx - 1) % len(project_titles)]
            project = Project.objects.create(
                no=idx,
                project_code=f"BLR-{timezone.now().year}-{idx:03d}",
                year=timezone.now().year,
                project_title=title,
                project_description=f"Implementation of {title} to improve local capacity.",
                proposal=proposal,
                budget=budget,
                project_start=timezone.now().date() - timezone.timedelta(days=30),
                project_end=project_end,
                date_of_release=timezone.now().date() - timezone.timedelta(days=20),
                date_of_completion=project_end if status == "completed" else None,
                original_project_duration="12 months",
                extension_date="6 months" if status == "terminated" else "",
                status=status,
                agency_grantee="DOST PSTO Biliran",
                program=programs[(idx - 1) % len(programs)],
                type_of_project=project_types[(idx - 1) % len(project_types)],
                fund_source=fund_sources[(idx - 1) % len(fund_sources)],
                remarks=remarks[(idx - 1) % len(remarks)],
                district=districts[(idx - 1) % len(districts)],
                funds=Decimal("200000.00") + (idx * Decimal("25000.00")),
                total_project_cost=Decimal("250000.00") + (idx * Decimal("30000.00")),
                counterpart_funds=Decimal("25000.00") + (idx * Decimal("2000.00")),
                internally_managed_fund=Decimal("15000.00") + (idx * Decimal("1500.00")),
                total_funds_released=Decimal("100000.00") + (idx * Decimal("12000.00")),
                first_tranche=Decimal("50000.00") + (idx * Decimal("5000.00")),
                second_tranche=Decimal("30000.00") + (idx * Decimal("4000.00")),
                third_tranche=Decimal("20000.00") + (idx * Decimal("3000.00")),
                availed_technologies="Equipment package",
                interventions="Training and mentoring",
                beneficiary=proposal.beneficiaries or "Community Group",
                beneficiary_address=f"{proposal.municipality}, Biliran",
                contact_details=f"0917{random.randint(1000000, 9999999)}",
                proponent_details=f"{proposal.submitted_by.get_full_name()}"
                if proposal.submitted_by else "Proponent Demo",
                no_of_beneficiaries=total_beneficiaries,
                male=male,
                female=female,
                total_beneficiaries=total_beneficiaries,
                senior_citizen=int(total_beneficiaries * 0.08),
                pwd=int(total_beneficiaries * 0.05),
                check_ada_no=f"ADA-{timezone.now().year}-{idx:04d}",
                status_of_liquidation=liquidation_statuses[(idx - 1) % len(liquidation_statuses)],
                date_of_liquidation=timezone.now().date() if status == "completed" else None,
                amount_liquidated=Decimal("80000.00") + (idx * Decimal("6000.00")),
                tafr=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                par=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                terminal_report=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                invoice_receipt=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                list_of_eqpt="Equipment A, Equipment B",
                donated=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                date_of_donation=timezone.now().date() if idx % 3 == 0 else None,
                donation_status=donation_statuses[(idx - 1) % len(donation_statuses)],
                pme_visit=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                womens_group=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                date_of_inspection_tagging=timezone.now().date() if idx % 4 == 0 else None,
                acknowledgment_receipt_by_grantee=yes_no_pending[(idx - 1) % len(yes_no_pending)],
                mun=proposal.municipality or "Naval",
                province="Biliran",
                latitude=proposal.latitude,
                longitude=proposal.longitude,
            )
            projects.append(project)
        return projects

    def _create_demo_tasks(self, projects, staff_user):
        tasks = []
        status_cycle = ["pending", "in_progress", "completed", "delayed"]
        priorities = ["low", "medium", "high"]
        categories = ["review", "reporting", "site_visit", "documentation"]
        for project_idx, project in enumerate(projects, start=1):
            for task_idx in range(1, self.TASKS_PER_PROJECT + 1):
                status = status_cycle[(task_idx - 1) % len(status_cycle)]
                title = f"Demo Task {project_idx}-{task_idx}"
                task, _ = Task.objects.get_or_create(
                    project=project,
                    title=title,
                    defaults={
                        "description": f"{title} for {project.project_title}",
                        "assigned_to": staff_user,
                        "due_date": timezone.now().date() + timezone.timedelta(days=7 + task_idx),
                        "status": status,
                        "priority": priorities[(task_idx - 1) % len(priorities)],
                        "category": categories[(task_idx - 1) % len(categories)],
                    },
                )
                if task.assigned_to != staff_user or task.status != status:
                    task.assigned_to = staff_user
                    task.status = status
                    task.save(update_fields=["assigned_to", "status"])
                tasks.append(task)
        return tasks
