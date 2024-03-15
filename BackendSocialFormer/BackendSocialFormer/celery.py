import os

from celery import Celery
from django.core.mail import send_mail

from BackendSocialFormer import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackendSocialFormer.settings')

app = Celery('BackendSocialFormer')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(ignore_result=True)
def send_otp(otp, receiver, username):
    print(otp)
    send_mail(
        subject=f'Mã OPT xác thực cho tài khoản của {username}',
        message=f'Mã xác thực: {otp} \nLưu ý rằng mỗi OTP chỉ có thời hạn là 5 phút',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[receiver],
        fail_silently=True,
    )
    return None