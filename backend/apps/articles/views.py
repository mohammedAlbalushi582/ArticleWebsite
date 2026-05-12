from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import Article
from .serializers import ArticleListSerializer, ArticleSerializer, ArticleSubmitSerializer
from .services import analyze_article


def get_session_key(request):
    return request.headers.get("X-Session-ID", "")


def get_owner_filter(request):
    """Return a queryset filter dict for the current user or session."""
    if request.user and request.user.is_authenticated:
        return {"user": request.user}
    session_key = get_session_key(request)
    if session_key:
        return {"session_key": session_key}
    return {"pk": None}  # match nothing


class ArticleAnalyzeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ArticleSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user.is_authenticated else None
        session_key = get_session_key(request) if not user else None

        article = analyze_article(
            user=user,
            session_key=session_key,
            url=serializer.validated_data.get("url", ""),
            text=serializer.validated_data.get("text", ""),
        )
        return Response(
            ArticleSerializer(article, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ArticleViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("title",)
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Article.objects.filter(**get_owner_filter(self.request)).select_related("user")

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer
        return ArticleSerializer

    def partial_update(self, request, *args, **kwargs):
        article = self.get_object()
        if "is_public" in request.data:
            article.is_public = request.data["is_public"]
            article.save(update_fields=["is_public"])
        return Response(ArticleSerializer(article, context={"request": request}).data)


class PublicArticleListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleListSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("title",)

    def get_queryset(self):
        return Article.objects.filter(is_public=True).select_related("user")


class PublicArticleDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(is_public=True).select_related("user")
