from django import forms

from custom.models import Department
from tickets.models import Ticket


class TicketForm(forms.Form):
    PRIORITY_CHOICES_EMPTY = [('', 'Set Ticket Priority')] + Ticket.PRIORITY_CODES

    department_choices = [('', 'Select Your Department')]
    for department in Department.objects.all().order_by('title'):
        department_choices.append((department.pk, department.title))

    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    department = forms.ChoiceField(choices=department_choices)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES_EMPTY)
    due_date = forms.DateTimeField(required=False)
