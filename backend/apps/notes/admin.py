from django.contrib import admin

from .models import Highlight


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("text", "color", "article", "user", "session_key", "created_at")
    list_filter = ("color",)
