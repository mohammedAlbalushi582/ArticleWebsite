from django.contrib import admin

from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("role", "content_preview", "article", "created_at")
    list_filter = ("role",)

    @admin.display(description="Content")
    def content_preview(self, obj):
        return obj.content[:80]
