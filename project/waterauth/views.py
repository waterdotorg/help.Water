from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.views.decorators.cache import never_cache


def waterauth_signout(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS,
                         'Successfully signed out. Thanks for spending some '
                         'time with me today!')
    return redirect('auth_signin')


@never_cache
def waterauth_signin(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            if request.GET.get('next'):
                r = redirect(request.GET.get('next'))
            else:
                r = redirect(settings.LOGIN_REDIRECT_URL)
            return r
    else:
        form = AuthenticationForm(request)

    request.session.set_test_cookie()

    context = {
        'form': form,
    }
    return render_to_response('waterauth/signin.html', context,
                              context_instance=RequestContext(request))
