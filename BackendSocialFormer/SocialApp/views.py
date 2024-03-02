import random

from django.shortcuts import render
from django.templatetags.static import static
from rest_framework import viewsets, status, generics, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
import cloudinary.uploader

from SocialApp.models import User
from SocialApp.serializers import FormerSerializer, LecturerSerializer


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


    @action(methods=['post'], detail=False, url_path='sent-otp')
    def sent_otp(self, request):
        try:
            email = request.data.get('email')
            if email and User.objects.filter(email=email).exists():
                otp = random.randint(1000,9999)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'Error': 'Error creating user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
