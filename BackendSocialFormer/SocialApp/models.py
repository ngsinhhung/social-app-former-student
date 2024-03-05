from cloudinary.models import CloudinaryField
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class User(AbstractUser):

    class Roles(models.TextChoices):
        FORMER = 'FORMER_STUDENT', ('Cựu học sinh'),
        LECTURER = 'LECTURER', ('Giảng viên'),
        ADMIN = 'ADMIN', ('Quản trị viên')

    username = models.CharField(max_length=50, unique=True)
    created_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    role = models.CharField(choices=Roles.choices, max_length=50)
    avatar_user = CloudinaryField('avatar', blank=True, null=True)
    cover_photo = CloudinaryField('cover', blank=True, null=True)


class FormerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.Roles.FORMER)

class Former(User):
    objects = FormerManager()

    class Meta:
        proxy = True

class LecturerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.Roles.LECTURER)


class Lecturer(User):
    objects = LecturerManager()

    class Meta:
        proxy = True

class Post(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    on_comment = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username}: {self.title}'

class ReactionPost(BaseModel):
    class React(models.TextChoices):
        LIKE = 'LIKE', ('Like')
        HAHA = 'HAHA', ('Haha')
        HEART = 'HEART', ('Heart')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=React.choices)

    class Meta:
        unique_together = ('user', 'post')

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='reply_comment', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.comment[:30]}'
