# models.py
from django.db import models
from django.utils import timezone

class Person(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='profiles')
    source = models.CharField(max_length=200)  # e.g., "LinkedIn", "Twitter", "Company Website"
    url = models.URLField()
    title = models.CharField(max_length=500)
    snippet = models.TextField()
    search_query = models.CharField(max_length=500)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.name} - {self.source}"

class SearchHistory(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    query = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    results_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Search histories"