from django.urls import path
from .views import BlogPostListView, BlogPostDetailView

urlpatterns = [
    path('posts/', BlogPostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', BlogPostDetailView.as_view(), name='post-detail'),
]
