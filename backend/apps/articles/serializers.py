from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "source_url",
            "title",
            "raw_text",
            "summary",
            "key_points",
            "tags",
            "is_public",
            "is_owner",
            "author_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_owner", "author_name", "created_at", "updated_at")

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        if request.user and request.user.is_authenticated:
            return obj.user_id == request.user.id
        session_key = request.headers.get("X-Session-ID", "")
        return bool(session_key and obj.session_key == session_key)

    def get_author_name(self, obj):
        if obj.user:
            return obj.user.name or "Anonymous"
        return "Anonymous"


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ("id", "source_url", "title", "summary", "tags", "is_public", "author_name", "created_at")
        read_only_fields = fields

    def get_author_name(self, obj):
        if obj.user:
            return obj.user.name or "Anonymous"
        return "Anonymous"


class ArticleSubmitSerializer(serializers.Serializer):
    url = serializers.URLField(required=False, allow_blank=True)
    text = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        url = data.get("url", "").strip()
        text = data.get("text", "").strip()
        if not url and not text:
            raise serializers.ValidationError("Provide either a URL or text to analyze.")
        return data
