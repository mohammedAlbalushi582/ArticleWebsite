from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.articles.models import Article
from apps.articles.views import get_owner_filter, get_session_key
from core.exceptions import ArticleNotFound

from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatSendSerializer
from .services import send_chat_message


class ChatListView(APIView):
    """List chat history and send messages for an article."""

    permission_classes = (AllowAny,)

    def _get_article(self, request, article_id):
        try:
            return Article.objects.get(id=article_id, **get_owner_filter(request))
        except Article.DoesNotExist:
            pass
        try:
            return Article.objects.get(id=article_id, is_public=True)
        except Article.DoesNotExist:
            raise ArticleNotFound()

    def _get_ownership(self, request):
        if request.user and request.user.is_authenticated:
            return {"user": request.user}
        session_key = get_session_key(request)
        if session_key:
            return {"session_key": session_key}
        return {}

    def get(self, request, article_id):
        article = self._get_article(request, article_id)
        ownership = self._get_ownership(request)
        messages = ChatMessage.objects.filter(article=article, **ownership)
        return Response(ChatMessageSerializer(messages, many=True).data)

    def post(self, request, article_id):
        article = self._get_article(request, article_id)

        serializer = ChatSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user and request.user.is_authenticated else None
        session_key = get_session_key(request)

        assistant_msg = send_chat_message(
            article=article,
            user_message=serializer.validated_data["message"],
            user=user,
            session_key=session_key,
        )
        return Response(
            ChatMessageSerializer(assistant_msg).data,
            status=status.HTTP_201_CREATED,
        )
