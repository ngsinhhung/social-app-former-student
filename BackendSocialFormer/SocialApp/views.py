from django.shortcuts import render
from django.templatetags.static import static
from rest_framework import viewsets, status, generics, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
import cloudinary.uploader

from SocialApp.models import User
from SocialApp.serializers import FormerSerializer, LecturerSerializer


# Create your views here.
class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = FormerSerializer
    parser_classes = [parsers.MultiPartParser, ]

    @action(methods=['get', 'put'], detail=False, url_path='current-user')
    def current_user(self, request):
        user = request.user
        if request.method.__eq__('PUT'):
            for key, value in request.data.items():
                setattr(user, key, value)
            user.save()
        return Response(FormerSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)

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

