from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from custom.models import Department
from tickets.models import Ticket
from tickets.forms import TicketForm


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
