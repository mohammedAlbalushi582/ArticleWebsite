from rest_framework import serializers

from .models import Highlight


class HighlightSerializer(serializers.ModelSerializer):
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = Highlight
        fields = ("id", "article", "text", "color", "note", "source", "is_own", "created_at")
        read_only_fields = ("id", "is_own", "created_at")

    def get_is_own(self, obj):
        request = self.context.get("request")
        if not request:
            return True
        if request.user and request.user.is_authenticated:
            return obj.user_id == request.user.id
        session_key = request.headers.get("X-Session-ID", "")
        return bool(session_key and obj.session_key == session_key)
