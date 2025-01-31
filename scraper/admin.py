from django.contrib import admin
from .models import ScrapingJob, ScrapedContent, WebsiteEndpoint

@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ('url', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('url', 'error_message')
    readonly_fields = ('created_at', 'completed_at')
    ordering = ('-created_at',)

@admin.register(ScrapedContent)
class ScrapedContentAdmin(admin.ModelAdmin):
    list_display = ('url', 'job', 'scraped_at')
    list_filter = ('scraped_at', 'job__status')
    search_fields = ('url', 'html_content', 'job__url')
    readonly_fields = ('scraped_at',)
    ordering = ('-scraped_at',)

@admin.register(WebsiteEndpoint)
class WebsiteEndpointAdmin(admin.ModelAdmin):
    list_display = ('endpoint_name', 'url', 'path', 'job', 'discovered_at')
    list_filter = ('discovered_at', 'job__status')
    search_fields = ('endpoint_name', 'url', 'path', 'job__url')
    readonly_fields = ('discovered_at',)
    ordering = ('-discovered_at',)
