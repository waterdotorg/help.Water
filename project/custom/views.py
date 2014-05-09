from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

from tickets.models import Ticket
from custom.forms import SettingsForm


def homepage(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    return redirect('auth_signin')


@login_required
def dashboard(request):
    assigned_tickets = Ticket.objects.filter(
        Q(status=Ticket.ASSIGNED_STATUS) | Q(status=Ticket.IN_PROGRESS_STATUS),
        assigned=request.user).order_by('created_date')
    watching_tickets = Ticket.objects.filter(
        Q(status=Ticket.UNASSIGNED_STATUS) | Q(status=Ticket.ASSIGNED_STATUS) |
        Q(status=Ticket.IN_PROGRESS_STATUS),
        watchers=request.user.pk,
    ).order_by('-updated_date')
    recent_tickets = Ticket.objects.all().order_by('-created_date')[:10]
    dict_context = {
        'assigned_tickets': assigned_tickets,
        'recent_tickets': recent_tickets,
        'watching_tickets': watching_tickets,
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
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            request.user.department = form.cleaned_data.get('department')
            request.user.ticket_auto_watch = form.cleaned_data.get('ticket_auto_watch', '')
            request.user.save()
            messages.success(request, 'Successfully updated settings.')
            return redirect('dashboard')
    else:
        initial = {
            'department': request.user.department,
            'ticket_auto_watch': request.user.ticket_auto_watch,
        }
        form = SettingsForm(initial=initial)

    dict_context = {'form': form}

    return render(request, 'settings.html', dict_context)
