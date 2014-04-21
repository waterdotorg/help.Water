from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def homepage(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    return redirect('auth_signin')


@login_required
def dashboard(request):
    return
