from django import forms
from django.utils.translation import ugettext_lazy as _


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.help_text:
                field.widget.attrs['placeholder'] = field.help_text


class ContactForm(BaseForm):
    name = forms.CharField(max_length=100, help_text=_('Enter full name'))
    email = forms.EmailField(help_text=_('Email address'))
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}),
                              help_text=_('Your Message'))


class NewsletterForm(forms.Form):
    first_name = forms.CharField(label=_('First Name'), max_length=30)
    last_name = forms.CharField(label=_('Last Name'), max_length=30)
    email = forms.EmailField(label=_('Email'))
