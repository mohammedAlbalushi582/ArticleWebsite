from django.conf import settings
from django.db import models

from apps.articles.models import Article


class Highlight(models.Model):
    COLOR_CHOICES = [
        ("yellow", "Yellow"),
        ("green", "Green"),
        ("blue", "Blue"),
        ("pink", "Pink"),
    ]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="highlights")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="highlights",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    text = models.TextField()
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default="yellow")
    note = models.TextField(blank=True, default="")
    source = models.CharField(max_length=20, default="summary")  # summary, key_points, original
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Highlight: {self.text[:50]}"
