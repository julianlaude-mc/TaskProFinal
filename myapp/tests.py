from django.test import TestCase
from django.urls import reverse

from .models import FormTemplate, Message, Notification, Project, User
from .views import _local_assistant_quick_answer
from .notification_utils import normalized_notification_link_for_user


class NotificationRoutingTests(TestCase):
    def make_user(self, role, **extra):
        username = extra.pop('username', f'{role}_{User.objects.count()}')
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='test-password',
            role=role,
            **extra,
        )

    def test_admin_notification_never_routes_to_proponent_area(self):
        admin = self.make_user('admin', is_staff=True, is_superuser=True)

        self.assertEqual(
            normalized_notification_link_for_user(admin, '/proponent/dashboard/'),
            reverse('administrator_dashboard_url'),
        )
        self.assertEqual(
            normalized_notification_link_for_user(admin, '/proponent/tasks/'),
            reverse('administrator_task_list_url'),
        )

    def test_non_admin_links_are_mapped_to_matching_role_section(self):
        staff = self.make_user('dost_staff')
        beneficiary = self.make_user('beneficiary')

        self.assertEqual(
            normalized_notification_link_for_user(staff, '/proponent/projects/'),
            reverse('staff_projects_url'),
        )
        self.assertEqual(
            normalized_notification_link_for_user(beneficiary, '/administrator/proposals/1/'),
            reverse('beneficiary_proposals_url'),
        )

    def test_notification_redirect_marks_read_and_uses_normalized_target(self):
        admin = self.make_user('admin', is_staff=True, is_superuser=True)
        notification = Notification.objects.create(
            receiver=admin,
            message='Task update',
            category='task',
            link='/proponent/tasks/',
        )

        self.client.force_login(admin)
        response = self.client.get(reverse('notification_redirect', args=[notification.id]))
        notification.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('administrator_task_list_url'))
        self.assertEqual(notification.status, 'read')


class CommunicationAndFormsTests(TestCase):
    def make_user(self, role, **extra):
        username = extra.pop('username', f'{role}_{User.objects.count()}')
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='test-password',
            role=role,
            **extra,
        )

    def test_admin_messages_defaults_to_all_conversations(self):
        admin = self.make_user('admin', is_staff=True, is_superuser=True, username='admin_user')
        staff = self.make_user('dost_staff', username='staff_user')
        Message.objects.create(sender=admin, recipient=staff, subject='Sent only', content='Hello')

        self.client.force_login(admin)
        response = self.client.get(reverse('administrator_messages_url'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_box'], 'all')
        self.assertEqual(response.context['all_count'], 1)
        self.assertContains(response, 'Hello')

    def test_missing_form_file_redirects_to_role_forms_page(self):
        admin = self.make_user('admin', is_staff=True, is_superuser=True, username='forms_admin')
        form = FormTemplate.objects.create(
            title='Missing file',
            category='proposal',
            file='form_templates/missing.pdf',
            uploaded_by=admin,
        )

        self.client.force_login(admin)
        response = self.client.get(reverse('form_download_url', args=[form.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('administrator_forms_url'))
        form.refresh_from_db()
        self.assertEqual(form.download_count, 0)

    def test_local_assistant_projects_by_municipality(self):
        Project.objects.create(project_title='A', mun='Naval', total_project_cost=1000)
        Project.objects.create(project_title='B', mun='Naval', total_project_cost=2000)
        Project.objects.create(project_title='C', mun='Biliran', total_project_cost=500)

        answer = _local_assistant_quick_answer('show projects by municipality')

        self.assertIn('Projects by municipality', answer)
        self.assertIn('Naval: 2 project(s)', answer)
        self.assertIn('Biliran: 1 project(s)', answer)
