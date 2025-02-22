# Generated by Django 5.1.5 on 2025-01-20 11:15

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapingJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=500)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScrapedContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html_content', models.TextField()),
                ('scraped_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('url', models.URLField(max_length=500)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='scraper.scrapingjob')),
            ],
        ),
    ]
