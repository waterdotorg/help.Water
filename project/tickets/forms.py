from django import forms
from django.contrib.auth import get_user_model

from custom.models import Department
from tickets.models import Ticket

PRIORITY_CHOICES_EMPTY = [('', 'Set Ticket Priority')] + Ticket.PRIORITY_CODES
STATUS_CHOICES_EMPTY = [('', 'Set Ticket Status')] + Ticket.STATUS_CODES


class TicketForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('title'),
        empty_label="Select Your Department",
    )
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES_EMPTY)
    due_date = forms.DateTimeField(required=False)


class TicketCommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


class TicketCommentDeleteForm(forms.Form):
    pk = forms.CharField(required=False, widget=forms.HiddenInput)


class TicketEditForm(forms.Form):
    User = get_user_model()

    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('title'),
        empty_label="Select Your Department",
    )
    assigned = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name'),
        required=False,
    )
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    status = forms.ChoiceField(choices=STATUS_CHOICES_EMPTY)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES_EMPTY)
    watchers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name'),
        required=False
    )
    minutes_worked = forms.IntegerField(required=False)
    due_date = forms.DateTimeField(required=False)
    closed_date = forms.DateTimeField(required=False)
    resolution = forms.CharField(widget=forms.Textarea, required=False)
