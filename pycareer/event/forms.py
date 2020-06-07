from django import forms
from django.utils.translation import ugettext_lazy as _

from pycareer.core.choices import COUNTRIES
from pycareer.core.forms import BaseForm


class EventForm(BaseForm):
    name = forms.CharField(max_length=50, help_text=_('Name of the event'))
    start_date = forms.DateField(help_text=_('YYYY-MM-DD'))
    end_date = forms.DateField(help_text=_('YYYY-MM-DD'))
    city = forms.CharField(max_length=30, help_text=_('e.g. Brooklyn'))
    state = forms.CharField(required=False, max_length=30, help_text=_('e.g. NY'))
    country = forms.ChoiceField(label=_('Country'), required=False, choices=COUNTRIES)
    website = forms.URLField(required=False, help_text=_('a URL with more details for the event'))
    topics = forms.CharField(required=False, help_text=_('Django, Pyramid, Flask, Web Programming'))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False,
                                  help_text=_('a short description on venue address, event activities.'))

    def clean(self):
        if 'start_date' in self.cleaned_data and 'end_date' in self.cleaned_data:
            if self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
                raise forms.ValidationError(_("End date must be greater than Start date."))
        return self.cleaned_data
