from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.ArticleViewSet, basename="article")

urlpatterns = [
    path("analyze/", views.ArticleAnalyzeView.as_view(), name="article-analyze"),
    path("public/", views.PublicArticleListView.as_view(), name="public-article-list"),
    path("public/<int:pk>/", views.PublicArticleDetailView.as_view(), name="public-article-detail"),
    path("", include(router.urls)),
]
