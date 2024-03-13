import random

from django.db.models import Q
from django.shortcuts import render
from django.templatetags.static import static
from rest_framework import viewsets, status, generics, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import cloudinary.uploader

from SocialApp import perms
from SocialApp.models import User, Post, Image, Comment, ReactionPost
from SocialApp.serializers import FormerSerializer, LecturerSerializer, PostSerializer, CommentSerializer, \
    ReactionSerializer


# Create your views here.
class UserViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = FormerSerializer
    parser_classes = [parsers.MultiPartParser, ]

    @action(methods=['GET', 'PUT'], detail=False, url_path='current-user')
    def current_user(self, request):
        try:
            user = request.user
            user_instance = User.objects.get(username=user)
            if request.method.__eq__('GET'):
                return Response(data=LecturerSerializer(user_instance, context={'request': request}).data,
                                status=status.HTTP_200_OK)
            elif request.method.__eq__('PUT'):
                for key, value in request.data.items():
                    setattr(user_instance, key, value)
                user_instance.save()
                return Response(data=LecturerSerializer(user_instance, context={'request': request}).data,
                                status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountViewSet(viewsets.ViewSet):
    queryset = User.objects.all()

    @action(methods=['post'], detail=False, url_path='former/register')
    def former_register(self, request):
        try:
            data = request.data
            res = cloudinary.uploader.upload(data.get('avatar'), folder='avatar_user/')
            # res_cover_photo = cloudinary.uploader.upload('/static/media/default-cover-4.jpeg', folder='cover_photo/')
            new_former = User.objects.create_user(
                username=data.get('username'),
                password=data.get('password'),
                avatar_user=res['secure_url'],
                # cover_photo=res_cover_photo['secure_url'],
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=User.Roles.FORMER
            )
            return Response(data=FormerSerializer(new_former, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'Error': 'Error creating user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False, url_path='lecturer/register')
    def lecturer_register(self, request):
        try:
            data = request.data
            new_lecturer = User.objects.create_user(
                username=data.get('username'),
                password='ou@123',
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=User.Roles.LECTURER,
                verified=True
            )
            return Response(data=LecturerSerializer(new_lecturer, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'Error': 'Error creating user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False, url_path='change-password')
    def change_password(self, request):
        try:
            user = request.user
            if user.is_authenticated:
                old_password = request.data.get('old_password')
                new_password = request.data.get('new_password')
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    return Response({"Password changed successfully"}, status=status.HTTP_200_OK)
                else:
                    print(user)
                    return Response({"Old password incorrect"}, status=status.HTTP_200_OK)
            else:
                return Response({"Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView,
                  generics.DestroyAPIView):
    queryset = Post.objects.all().order_by('-id')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'on_comment']:
            self.permission_classes = [perms.IsOwner]
        return super(PostViewSet, self).get_permissions()

    def list(self, request):
        try:
            user = request.user
            posts = Post.objects.filter(user=user).order_by('-id')
            return Response(data=PostSerializer(posts, many=True, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            user = request.user
            data = request.data
            post = Post.objects.create(
                user=user,
                title=data['title'],
                content=data['content']
            )
            for image in request.FILES.getlist('image'):
                res = cloudinary.uploader.upload(image, folder='post_image/')
                Image.objects.create(post=post, image=res['secure_url'])
            return Response(data=PostSerializer(post, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        try:
            post = self.get_object()
            for key, value in request.data.items():
                setattr(post, key, value)
            post.save()
            return Response(data=PostSerializer(post, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post', 'get', 'delete'], detail=True, url_path='reaction')
    def react_to_post(self, request, pk):
        try:
            user = request.user
            post = self.get_object()
            if request.methods.__eq__('POST'):
                reacted, react = ReactionPost.objects.update_or_create(
                    post=post,
                    user=user,
                    reaction_type=request.data.get('reaction_type')
                )
                if reacted:
                    reacted.reaction_type = request.data.get('reaction_type')
                    reacted.save()

                return Response(data=ReactionSerializer(reacted).data,
                                status=status.HTTP_201_CREATED)
            elif request.methods.__eq__('GET'):
                react = ReactionPost.objects.filter(post=post)
                return Response(data=ReactionSerializer(react, many=True).data,
                                status=status.HTTP_200_OK)
            elif request.methods.__eq__('DELETE'):
                react = ReactionPost.objects.filter(post=post, user=user)
                react.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BpoAD_REQUEST)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["post", "get"], detail=True, url_path='comment')
    def comment_post(self, request, pk):
        try:
            user = request.user
            post = self.get_object()
            print(user)
            if request.method.__eq__("GET"):
                comment = Comment.objects.filter(Q(post=post) & Q(parent_comment__isnull=True))
                return Response(data=CommentSerializer(comment, many=True, context={'request': request}).data,
                                status=status.HTTP_200_OK)
            elif request.method.__eq__("POST"):
                comment = Comment.objects.create(
                    user=user,
                    post=self.get_object(),
                    comment=request.data.get('comment')
                )
                return Response(data=CommentSerializer(comment, context={'request': request}).data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['put'], detail=True, url_path='on_comment')
    def on_comment(self, request, pk):
        try:
            post = self.get_object()
            if post.on_comment == True:
                post.on_comment = False
                post.save()
            else:
                post.on_comment = True
                post.save()
            return Response(data=PostSerializer(post, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.filter(parent_comment__isnull=True)
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [perms.IsOwner]
        return super(CommentViewSet, self).get_permissions()

    def partial_update(self, request, pk):
        try:
            user = request.user
            comment = Comment.objects.get(pk=pk)
            if user == comment.user:
                comment.comment = request.data.get('comment')
                comment.save()
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
            return Response(data=CommentSerializer(comment, context={'request': request}).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk):
        try:
            comment = self.get_object()
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post', 'get'], detail=True, url_path='reply')
    def reply(self, request, pk):
        try:
            user = request.user
            parent = Comment.objects.get(pk=pk)
            post = parent.post
            if request.method.__eq__('POST'):
                reply = Comment.objects.create(
                    user=user,
                    post=post,
                    comment=request.data.get('comment'),
                    parent_comment=parent
                )
                return Response(data=CommentSerializer(reply).data, status=status.HTTP_201_CREATED)
            elif request.method.__eq__('GET'):
                reply = Comment.objects.filter(parent_comment=parent)
                return Response(data=CommentSerializer(reply, many=True).data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
