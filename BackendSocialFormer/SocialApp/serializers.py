from rest_framework import serializers

from SocialApp.models import Former


class FormerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Former
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar_user', 'cover_photo', 'role', 'verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }


class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Former
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar_user', 'cover_photo', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }