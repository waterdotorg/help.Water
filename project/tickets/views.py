from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden

from custom.models import Department
from tickets.models import Ticket, TicketComment
from tickets.forms import TicketForm, TicketCommentForm, TicketCommentDeleteForm, TicketEditForm


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

    if 'ticket-comments-wrapper' in request.get_full_path():
        selected_tab = 'comments'
    else:
        selected_tab = 'view'

    dict_context = {
        'form': form,
        'selected_tab': selected_tab,
        'ticket': ticket,
        'ticket_comments': ticket_comments,
        'watchers': ticket.watchers.all(),
    }
    return render(request, 'tickets/detail.html', dict_context)


@login_required
def ticket_edit(request, pk=None):
    User = get_user_model()

    try:
        ticket = Ticket.objects.prefetch_related().get(pk=pk)
    except Ticket.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = TicketEditForm(request.POST)
        if form.is_valid():
            try:
                department = Department.objects.get(
                    pk=form.cleaned_data.get('department')
                )
            except:
                department = None

            try:
                assigned = User.objects.get(
                    pk=form.cleaned_data.get('assigned')
                )
            except:
                assigned = None

            watchers_list = []
            for pk in form.cleaned_data.get('watchers'):
                try:
                    watchers_list.append(int(pk))
                except:
                    pass

            ticket.department = department
            ticket.assigned = assigned
            ticket.title = form.cleaned_data.get('title')
            ticket.description = form.cleaned_data.get('description')
            ticket.status = form.cleaned_data.get('status')
            ticket.priority = form.cleaned_data.get('priority')
            ticket.watchers = watchers_list
            ticket.minutes_worked = form.cleaned_data.get('minutes_worked')
            ticket.due_date = form.cleaned_data.get('due_date')
            ticket.closed_date = form.cleaned_data.get('closed_date')
            ticket.resolution = form.cleaned_data.get('resolution')
            ticket.save()

            messages.success(request, 'Ticket updated.')
            return redirect(ticket.get_absolute_url())
    else:
        if ticket.department:
            department_pk = ticket.department.pk
        else:
            department_pk = None

        if ticket.assigned:
            assigned_pk = ticket.assigned.pk
        else:
            assigned_pk = None

        initial = {
            'department': department_pk,
            'assigned': assigned_pk,
            'title': ticket.title,
            'description': ticket.description,
            'status': ticket.status,
            'priority': ticket.priority,
            'watchers': ticket.watchers.values_list('pk', flat=True),
            'minutes_worked': ticket.minutes_worked,
            'due_date': ticket.due_date,
            'closed_date': ticket.closed_date,
            'resolution': ticket.resolution,
        }
        form = TicketEditForm(initial=initial)

    dict_context = {
        'form': form,
        'ticket': ticket,
        'selected_tab': 'edit',
    }

    return render(request, 'tickets/edit.html', dict_context)


@login_required
def ticket_comment_edit(request, pk=None):
    ticket_comment = get_object_or_404(TicketComment, pk=pk)
    ticket_comments = (TicketComment.objects.select_related()
                       .filter(ticket=ticket_comment.ticket)
                       .order_by('-created_date'))

    if ticket_comment.author.pk != request.user.pk and not request.user.is_superuser:
        return HttpResponseForbidden('<p>You do not have access to this page.</p>')

    if request.method == 'POST':
        form = TicketCommentForm(request.POST)
        if form.is_valid():
            ticket_comment.content = form.cleaned_data.get('content')
            ticket_comment.save()
            messages.success(request, 'Comment updated successfully.')
            return redirect(ticket_comment.ticket.get_absolute_url())
    else:
        initial = {
            'content': ticket_comment.content,
        }
        form = TicketCommentForm(initial=initial)

    dict_context = {
        'form': form,
        'ticket_comment': ticket_comment,
        'ticket_comments': ticket_comments,
    }

    return render(request, 'tickets/comments/edit.html', dict_context)


@login_required
def ticket_comment_delete(request, pk=None):
    ticket_comment = get_object_or_404(TicketComment, pk=pk)

    if ticket_comment.author.pk != request.user.pk and not request.user.is_superuser:
        return HttpResponseForbidden('<p>You do not have access to this page.</p>')

    if request.method == 'POST':
        form = TicketCommentDeleteForm(request.POST)
        if form.is_valid():
            redirect_url = ticket_comment.ticket.get_absolute_url()
            ticket_comment.delete()
            messages.success(request, 'Comment deleted successfully.')
            return redirect(redirect_url)
    else:
        initial = {'pk': ticket_comment.pk}
        form = TicketCommentDeleteForm(initial=initial)

    dict_context = {
        'form': form,
        'ticket_comment': ticket_comment,
    }

    return render(request, 'tickets/comments/delete.html', dict_context)
