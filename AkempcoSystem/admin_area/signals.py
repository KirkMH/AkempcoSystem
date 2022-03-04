from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import UserLog
 
 
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f'{user.username} logged in')
    log = UserLog()
    log.username = user.username
    log.user = user
    log.action_taken = 'logged in'
    log.save()
 
 
@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    print(f'{credentials.get("username")} logged in failed')
    log = UserLog()
    log.username = credentials.get("username")
    log.action_taken = 'failed to login'
    log.save()
 
 
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    print(f'{user.username} logged out')
    log = UserLog()
    log.username = user.username
    log.user = user
    log.action_taken = 'logged out'
    log.save()