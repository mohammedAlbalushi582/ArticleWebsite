from rest_framework import serializers

from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("id", "role", "content", "created_at")
        read_only_fields = ("id", "role", "created_at")


class ChatSendSerializer(serializers.Serializer):
    message = serializers.CharField(min_length=1, max_length=5000)
