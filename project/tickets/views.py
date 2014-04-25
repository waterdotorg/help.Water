from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.http import Http404

from custom.models import Department
from tickets.models import Ticket, TicketComment
from tickets.forms import TicketForm, TicketCommentForm


@login_required
def tickets(request):
    tickets = cache.get('tickets_cache')
    if not tickets:
        tickets = Ticket.objects.all()
        cache.set('tickets_cache', tickets, 500)
    tickets = Ticket.objects.all()

    kwargs = {}

    filter_status = request.GET.get('fstatus')
    if filter_status:
        kwargs.update({'status__in': filter_status.split(',')})

    filter_priority = request.GET.get('fpriority')
    if filter_priority:
        kwargs.update({'priority__in': filter_priority.split(',')})

    if kwargs:
        tickets = tickets.filter(**kwargs)

    tickets = tickets.order_by('-created_date')

    paginator = Paginator(tickets, 25)
    page = request.GET.get('page')
    try:
        tickets_pager = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tickets_pager = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tickets_pager = paginator.page(paginator.num_pages)

    dict_context = {'tickets_pager': tickets_pager}

    return render(request, 'tickets/tickets.html', dict_context)


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                department = Department.objects.get(
                    pk=form.cleaned_data.get('department')
                )
            except Department.DoesNotExist:
                department = None

            ticket = Ticket(
                author=request.user,
                department=department,
                title=form.cleaned_data.get('title'),
                description=form.cleaned_data.get('description'),
                priority=form.cleaned_data.get('priority'),
                due_date=form.cleaned_data.get('due_date')
            )
            ticket.save()
            messages.success(request, 'Successfully created ticket.')
            return redirect('dashboard')
    else:
        form = TicketForm()

    dict_context = {'form': form}

    return render(request, 'tickets/create.html', dict_context)


@login_required
def ticket_detail(request, pk=None):
    try:
        ticket = Ticket.objects.prefetch_related().get(pk=pk)
    except Ticket.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = TicketCommentForm(request.POST)
        if form.is_valid():
            ticket_comment = TicketComment(
                ticket=ticket,
                author=request.user,
                content=form.cleaned_data.get('content'),
            )
            ticket_comment.save()
            messages.success(request, 'Successfully added comment.')
            return redirect(ticket.get_absolute_url())
    else:
        form = TicketCommentForm()

    ticket_comments = (TicketComment.objects.select_related()
                       .filter(ticket=ticket).order_by('-created_date'))

    dict_context = {
        'form': form,
        'ticket': ticket,
        'ticket_comments': ticket_comments,
    }
    return render(request, 'tickets/detail.html', dict_context)
