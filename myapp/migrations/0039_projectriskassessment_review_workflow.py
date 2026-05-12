# Generated manually for the forecast review workflow.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0038_delete_reportingcache_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectriskassessment',
            name='review_status',
            field=models.CharField(
                choices=[
                    ('open', 'Open'),
                    ('acknowledged', 'Acknowledged'),
                    ('in_review', 'In Review'),
                    ('resolved', 'Resolved'),
                ],
                default='open',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='projectriskassessment',
            name='acknowledged_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='acknowledged_risk_assessments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='projectriskassessment',
            name='acknowledged_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectriskassessment',
            name='assigned_reviewer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_risk_assessments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='projectriskassessment',
            name='follow_up_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectriskassessment',
            name='resolved_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='resolved_risk_assessments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='projectriskassessment',
            name='resolved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectriskassessment',
            name='review_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='projectriskassessment',
            index=models.Index(fields=['review_status', 'follow_up_date'], name='idx_risk_review_due'),
        ),
    ]
