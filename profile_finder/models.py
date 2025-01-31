# models.py
from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator

class Person(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Source(models.Model):
    name = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ['-priority', 'name']

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
    confidence_score = models.FloatField(default=1.0)
    name_match_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    description_match_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    content_relevance_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    overall_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    class Meta:
        ordering = ['-overall_score', '-last_updated']

    def __str__(self):
        return f"{self.person.name} - {self.source}"

class SearchHistory(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    query = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    results_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Search histories"