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