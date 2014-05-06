from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from tickets.models import Ticket


def homepage(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    return redirect('auth_signin')


@login_required
def dashboard(request):
    assigned_tickets = Ticket.objects.filter(
        Q(status=Ticket.ASSIGNED_STATUS) | Q(status=Ticket.IN_PROGRESS_STATUS),
        assigned=request.user).order_by('created_date')
    recent_tickets = Ticket.objects.all().order_by('-created_date')[:10]
    dict_context = {
        'assigned_tickets': assigned_tickets,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'dashboard.html', dict_context)


@login_required
def search(request):
    q = request.GET.get('q')

    if not q:
        messages.error(request, 'Please enter a search term.')
        return render(request, 'search.html')

    title_results = Ticket.objects.filter(title__icontains=q)
    content_results = Ticket.objects.filter(
        Q(description__icontains=q) | Q(resolution__icontains=q)
    )

    dict_context = {
        'title_results': title_results,
        'content_results': content_results,
    }

    return render(request, 'search.html', dict_context)


@login_required
def settings_user(request):
    return
