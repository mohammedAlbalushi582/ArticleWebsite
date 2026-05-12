from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "is_public", "source_url", "created_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("title",)
