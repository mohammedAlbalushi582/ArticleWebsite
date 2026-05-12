from django.urls import path

from . import views

urlpatterns = [
    path("<int:article_id>/", views.ChatListView.as_view(), name="chat-list"),
]
