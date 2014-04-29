from django import forms
from django.contrib.auth import get_user_model

from custom.models import Department
from tickets.models import Ticket

PRIORITY_CHOICES_EMPTY = [('', 'Set Ticket Priority')] + Ticket.PRIORITY_CODES
STATUS_CHOICES_EMPTY = [('', 'Set Ticket Status')] + Ticket.STATUS_CODES

DEPARTMENT_CHOICES = [('', 'Select Your Department')]
for department in Department.objects.all().order_by('title'):
    DEPARTMENT_CHOICES.append((department.pk, department.title))


class TicketForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES_EMPTY)
    due_date = forms.DateTimeField(required=False)


class TicketCommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


class TicketEditForm(forms.Form):
    User = get_user_model()

    user_choices = [('', '---')] + [(user.pk, user.get_full_name()) for user in User.objects.filter(is_active=True).order_by('first_name')]

    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=False)
    assigned = forms.ChoiceField(choices=user_choices, required=False)
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    status = forms.ChoiceField(choices=STATUS_CHOICES_EMPTY)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES_EMPTY)
    watchers = forms.MultipleChoiceField(choices=user_choices, required=False)
    minutes_worked = forms.IntegerField(required=False)
    due_date = forms.DateTimeField(required=False)
    closed_date = forms.DateTimeField(required=False)
    resolution = forms.CharField(widget=forms.Textarea, required=False)
