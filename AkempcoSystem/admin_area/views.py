from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

# creating a custom permissions decorator
# uses Feature and UserDetail.features for permissions
def has_permission(self, perm, obj=None):
    return True
    # if perm in self.userdetail.get_permissions():
    #     return True
    # else:
    #     return False

def permission_required(perm):
    return user_passes_test(lambda u: u.has_permission(perm), login_url='dashboard')


@login_required()
def dashboard_view(request):
    return render(request, 'dashboard.html')


def login_check(request):
    if request.user.is_authenticated:
        my_user = User.objects.get(pk=request.user.pk)
        if all([hasattr(my_user, 'userdetail'), my_user.userdetail.activated_at is not None]):
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login_check.html')
    else:
        return redirect('login')