from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from pycareer.core.choices import COUNTRIES, USER_TYPE_CHOICES
from pycareer.core.forms import BaseForm


class RegistrationForm(BaseForm):
    MIN_PASS_LENGTH = 6

    first_name = forms.CharField(help_text=_('Enter first Name'), max_length=30)
    last_name = forms.CharField(help_text=_('Enter last Name'), max_length=30)
    email = forms.EmailField(help_text=_('Enter email address'))
    password1 = forms.CharField(widget=forms.PasswordInput,
                                help_text=_('Make sure your password is longer than 6 characters'))
    password2 = forms.CharField(widget=forms.PasswordInput, help_text=_('Confirm your password'))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, error_messages={
        'required': _(u'Are you Python Developer or Recruiter?'),
    })

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_('This email address is already in use.'))
        return self.cleaned_data['email']

    def clean_password1(self):
        """ Minimum length """
        password1 = self.cleaned_data.get('password1', '')
        if len(password1) < self.MIN_PASS_LENGTH:
            raise forms.ValidationError('Password must be at least %i characters' % self.MIN_PASS_LENGTH)

        return self.cleaned_data['password1']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data


class ProfileForm(forms.Form):
    first_name = forms.CharField(label=_('First Name'), max_length=30)
    last_name = forms.CharField(label=_('Last Name'), max_length=30)


class DeveloperProfileForm(ProfileForm):
    title = forms.CharField(label=_('Title'), max_length=50, required=True)
    skills = forms.CharField(label=_('Skills'), widget=forms.Textarea, required=False)
    city = forms.CharField(label=_('City'), max_length=50, required=True)
    state = forms.CharField(label=_('State'), max_length=50, required=False)
    country = forms.ChoiceField(label=_('Country'), required=True, choices=COUNTRIES)
    phone_number = forms.CharField(max_length=30, required=False)
    summary = forms.CharField(widget=forms.Textarea, required=True)
    avatar_url = forms.URLField(label=_('Avatar URL'), max_length=250, required=False)
    linkedin_url = forms.URLField(label=_('LinkedIn URL'), max_length=250, required=False)
    github_url = forms.URLField(label=_('Github URL'), max_length=250, required=False)
    stackoverflow_url = forms.URLField(label=_('StackOverflow URL'), max_length=250, required=False)


class RecruiterProfileForm(ProfileForm):
    company_name = forms.CharField(label=_('Company Name'), max_length=50, required=False)
    company_description = forms.CharField(widget=forms.Textarea, required=False)
