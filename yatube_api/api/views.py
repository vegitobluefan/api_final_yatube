from rest_framework import viewsets, permissions, filters
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from posts.models import Group, Post, Follow
from .serializers import (
    GroupSerializer, PostSerializer, CommentSerializer, FollowSerializer
)
from .permissions import AuthorOrReadOnly


class BaseMixin:
    """Кастомный миксин для повторяющегося кода."""

    error = PermissionDenied('Изменение и удаление чужого контента запрещено!')
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, AuthorOrReadOnly
    )

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise self.error
        super().perform_update(serializer)

    def perform_destroy(self, serializer):
        if serializer.author != self.request.user:
            raise self.error
        return super().perform_destroy(serializer)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Group, предназначенный только для чтения."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(BaseMixin, viewsets.ModelViewSet):
    """ViewSet для модели Post."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(BaseMixin, viewsets.ModelViewSet):
    """ViewSet для модели Comment."""

    serializer_class = CommentSerializer

    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs.get('post_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())

    def get_queryset(self):
        return self.get_post().comments.all()


class FollowViewSet(viewsets.ModelViewSet):
    """Viewset для модели Follow."""

    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
