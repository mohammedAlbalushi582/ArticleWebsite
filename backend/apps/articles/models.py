from django.conf import settings
from django.db import models


class Article(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    is_public = models.BooleanField(default=False, db_index=True)
    source_url = models.URLField(max_length=2000, blank=True, null=True)
    title = models.CharField(max_length=500)
    raw_text = models.TextField()
    summary = models.TextField()
    key_points = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
