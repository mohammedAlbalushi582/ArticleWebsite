from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.articles.models import Article
from apps.articles.views import get_owner_filter, get_session_key
from core.exceptions import ArticleNotFound

from .models import Highlight
from .serializers import HighlightSerializer


def _get_requester_ownership(request):
    """Return dict identifying the current requester."""
    if request.user and request.user.is_authenticated:
        return {"user": request.user}
    session_key = get_session_key(request)
    if session_key:
        return {"session_key": session_key}
    return {}


def _is_article_owner(request, article):
    """Check if the requester owns the article."""
    if request.user and request.user.is_authenticated:
        return article.user_id == request.user.id
    session_key = get_session_key(request)
    return bool(session_key and article.session_key == session_key)


def _get_accessible_article(request, article_id):
    """Return article if the requester owns it or it is public."""
    try:
        return Article.objects.select_related("user").get(
            id=article_id, **get_owner_filter(request)
        )
    except Article.DoesNotExist:
        pass
    # Fallback: check if the article is public
    try:
        return Article.objects.select_related("user").get(id=article_id, is_public=True)
    except Article.DoesNotExist:
        raise ArticleNotFound()


class HighlightListView(APIView):
    """List and create highlights for an article."""

    permission_classes = (AllowAny,)

    def get(self, request, article_id):
        article = _get_accessible_article(request, article_id)
        is_owner = _is_article_owner(request, article)

        if is_owner:
            # Owner sees only their own highlights
            ownership = _get_requester_ownership(request)
            highlights = Highlight.objects.filter(article=article, **ownership)
        else:
            # Viewer of public article sees owner's highlights + their own
            owner_q = Q()
            if article.user_id:
                owner_q = Q(user_id=article.user_id)
            elif article.session_key:
                owner_q = Q(session_key=article.session_key)

            requester = _get_requester_ownership(request)
            requester_q = Q()
            if "user" in requester:
                requester_q = Q(user=requester["user"])
            elif "session_key" in requester:
                requester_q = Q(session_key=requester["session_key"])

            highlights = Highlight.objects.filter(article=article).filter(
                owner_q | requester_q
            )

        return Response(
            HighlightSerializer(highlights, many=True, context={"request": request}).data
        )

    def post(self, request, article_id):
        article = _get_accessible_article(request, article_id)
        ownership = _get_requester_ownership(request)
        serializer = HighlightSerializer(
            data={**request.data, "article": article.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(**ownership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HighlightDetailView(APIView):
    """Delete a specific highlight."""

    permission_classes = (AllowAny,)

    def delete(self, request, article_id, highlight_id):
        article = _get_accessible_article(request, article_id)
        ownership = _get_requester_ownership(request)

        deleted, _ = Highlight.objects.filter(
            id=highlight_id, article=article, **ownership
        ).delete()
        if not deleted:
            return Response(
                {"error": {"code": "ERR_HIGHLIGHT_NOT_FOUND", "message": "Highlight not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
