from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from pycareer.core.choices import COUNTRIES
from pycareer.core.forms import BaseForm


class JobForm(BaseForm):
    company_name = forms.CharField(max_length=50, help_text=_('Company name, max length 50 chars'))
    title = forms.CharField(max_length=255, help_text=_('Job title, max length 250 chars'))
    city = forms.CharField(max_length=50, help_text=_('e.g. Brooklyn'))
    state = forms.CharField(required=False, max_length=50, help_text=_('e.g. NY'))
    country = forms.ChoiceField(label=_('Country'), required=False, choices=COUNTRIES)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    will_sponsor = forms.ChoiceField(choices=((True, 'Yes'), (False, 'No')), error_messages={
        'required': _(u'Please choose yes or no.'),
    })
    visas = forms.CharField(max_length=255, required=False, help_text=_('H-1B, H-1B1'))
    company_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4}))
    contact_url = forms.URLField(required=False,
                                 help_text=_('Company site, job listing page or link to application page'))
    contact_name = forms.CharField(max_length=255, required=False)
    contact_email = forms.EmailField(required=True)

    def clean_description(self):
        description = self.cleaned_data['description']
        return escape(description.strip())

    def clean_company_description(self):
        description = self.cleaned_data['company_description']
        return escape(description.strip())
