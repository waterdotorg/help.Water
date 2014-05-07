from django import forms
from custom.models import Department


class SettingsForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('title'),
        empty_label="Select Your Department"
    )
    ticket_auto_watch = forms.BooleanField(label='Auto watch your tickets',
                                           required=False)
