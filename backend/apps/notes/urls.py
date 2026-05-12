from django.urls import path

from . import views

urlpatterns = [
    path("<int:article_id>/", views.HighlightListView.as_view(), name="highlight-list"),
    path("<int:article_id>/<int:highlight_id>/", views.HighlightDetailView.as_view(), name="highlight-detail"),
]
