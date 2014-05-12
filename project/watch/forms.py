from django import forms
from tickets.models import Ticket


class WatchTicketForm(forms.Form):
    ticket_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(WatchTicketForm, self).__init__(*args, **kwargs)

    def clean_ticket_id(self):
        data = self.cleaned_data['ticket_id']
        try:
            Ticket.objects.get(pk=data)
        except Ticket.DoesNotExist:
            raise forms.ValidationError('Invalid ticket.')
        return data
