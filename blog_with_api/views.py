from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.views import APIView

from .models import Post, Comment
from .serializer import PostSerializers, TagSerializer, ContactSerializer, RegisterSerializer, UserSerializer, \
    CommentSerializer
from rest_framework.response import Response
from rest_framework import permissions, pagination, generics
from taggit.models import Tag


class PostPagination(pagination.PageNumberPagination):
    page_size = 3
    page_query_param = 'page_size'
    ordering = '-created_at'


class TagDetailView(generics.ListAPIView):
    serializer_class = PostSerializers
    pagination_class = PostPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug'].lower()
        tag = Tag.objects.get(slug=tag_slug)
        return Post.objects.filter(tags=tag)


class PostViewSet(viewsets.ModelViewSet):
    search_fields = ['content', 'h1', 'title']
    filter_backends = (filters.SearchFilter,)
    serializer_class = PostSerializers
    queryset = Post.objects.all()
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    pagination_class = PostPagination


class TagView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class AsideView(generics.ListAPIView):
    queryset = Post.objects.all().order_by("-id")[:5]
    serializer_class = PostSerializers
    permission_classes = [permissions.AllowAny]


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ContactSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = ContactSerializer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get('name')
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            send_mail(f'От {name} | {subject}', message, email, ['muhammadosmanov02@gmail.com'])
            return Response({"success": "Sent"})


class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно зарегистрирован",
        })


class ProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return Response({
            "user": UserSerializer(request.user, context=self.get_serializer_context()).data
        })


class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        post_slug = self.kwargs['post_slug'].lower()
        post = Post.objects.get(slug=post_slug)
        return Comment.objects.filter(post=post)
