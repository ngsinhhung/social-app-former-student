from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework_recursive.fields import RecursiveField

from SocialApp.models import Former, User, Post, Image, Comment


class FormerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Former
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar_user', 'cover_photo',
                  'role', 'verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }


class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Former
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'avatar_user', 'cover_photo',
                  'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar_user', 'cover_photo', 'role']


class ImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        return representation
    class Meta:
        model = Image
        fields = ['image', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    image = SerializerMethodField()
    def get_image(self, obj):
        images = Image.objects.filter(post_id=obj.id)
        serializer = ImageSerializer(images, many=True).data
        return serializer
    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'image', 'on_comment']

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveField(many=True, read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'comment', 'parent_comment', 'created_at', 'replies']


