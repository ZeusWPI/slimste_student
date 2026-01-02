from django.db import models
from django.contrib.auth.models import User


class Label(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labels', null=True, blank=True)
    shared_with = models.ManyToManyField(User, related_name='shared_labels', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'owner']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class Card(models.Model):
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=100, default='pi pi-star')
    quick_facts = models.JSONField(default=list, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    labels = models.ManyToManyField(Label, related_name='cards', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

