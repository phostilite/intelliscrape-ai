from django.db import models
from django.utils import timezone

class ScrapingJob(models.Model):
    url = models.URLField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed')
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.url} - {self.status}"

class ScrapedContent(models.Model):
    job = models.ForeignKey(ScrapingJob, on_delete=models.CASCADE, related_name='contents')
    html_content = models.TextField(help_text="Preview of the HTML content")
    html_file_path = models.CharField(max_length=255, help_text="Path to the stored HTML file")
    scraped_at = models.DateTimeField(default=timezone.now)
    url = models.URLField(max_length=500)

    def __str__(self):
        return f"Content from {self.url}"

class WebsiteEndpoint(models.Model):
    job = models.ForeignKey(ScrapingJob, on_delete=models.CASCADE, related_name='endpoints')
    url = models.URLField(max_length=500)
    endpoint_name = models.CharField(max_length=255)
    path = models.CharField(max_length=500)
    discovered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['job', 'url']

    def __str__(self):
        return f"{self.endpoint_name} ({self.url})"