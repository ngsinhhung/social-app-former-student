from django.conf import settings
from django.core.mail import send_mail

def sendotp(otp, receiver, first_name):
    send_mail(
        subject='Mã OPT xác thực cho tài khoản của bạn',
        message=f'{first_name}\n Mã xác thực:{otp}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[receiver],
        fail_silently=False,
    )