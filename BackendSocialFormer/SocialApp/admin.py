from django.contrib import admin
from SocialApp.models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(ReactionPost)
admin.site.register(Comment)
