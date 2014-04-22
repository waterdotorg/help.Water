from django import forms

from custom.models import Department
from tickets.models import Ticket


class TicketForm(forms.Form):
    department_choices = list()
    for department in Department.objects.all().order_by('title'):
        department_choices.append((department.pk, department.title))

    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    department = forms.ChoiceField(choices=department_choices)
    priority = forms.ChoiceField(choices=Ticket.PRIORITY_CODES)
    due_date = forms.DateTimeField(required=False)
