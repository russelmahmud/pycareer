import json

from django.db import transaction
from django.shortcuts import redirect, HttpResponse
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.views import password_change, password_reset, password_reset_confirm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from registration.backends.default.views import RegistrationView, ActivationView

from pycareer.core.choices import COUNTRIES
from pycareer.services import get_service
from .forms import RegistrationForm, DeveloperProfileForm, RecruiterProfileForm
from .models import Profile, Skill

developer_search = get_service('developer_search')


class CustomRegistrationView(RegistrationView):

    form_class = RegistrationForm

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(request, form)
        else:
            return self.form_invalid(form)

    def form_valid(self, request, form):
        messages.success(request, 'Thank you! Activation email sent. Please check your inbox.',
                         extra_tags='registration')
        return super(CustomRegistrationView, self).form_valid(request, form)

    def _create_profile(self, user, user_type):
        profile = Profile()
        profile.user = user
        profile.type = user_type
        profile.save()

    def register(self, request, **cleaned_data):
        cleaned_data['username'] = cleaned_data['email']
        new_user = super(CustomRegistrationView, self).register(request, **cleaned_data)
        new_user.first_name = cleaned_data['first_name']
        new_user.last_name = cleaned_data['last_name']
        new_user.save()
        self._create_profile(new_user, cleaned_data['user_type'])
        return new_user

    register = transaction.commit_on_success(register)

    def get_success_url(self, request, user):
        return reverse('registration_register')


class CustomActivationView(ActivationView):
    def get_success_url(self, request, user):
        messages.info(request, 'Your account is now activated. You can login now.', extra_tags='login')
        return reverse('auth_login')


def change_password(request):
    response = password_change(request, post_change_redirect=reverse('auth_password_change'))
    if isinstance(response, HttpResponseRedirect):
        messages.success(request, 'Success! Your password has been successfully updated.', extra_tags='password')
    return response


def reset_password(request):
    response = password_reset(request, post_reset_redirect=reverse('auth_password_reset'))
    if isinstance(response, HttpResponseRedirect):
        messages.info(request, 'Email with password reset instructions has been sent.', extra_tags='password')
    return response


def reset_password_confirm(request, uidb64=None, token=None):
    response = password_reset_confirm(request, uidb64=uidb64, token=token,
                                      post_reset_redirect=reverse('auth_login'))
    if isinstance(response, HttpResponseRedirect):
        messages.info(request, 'Password reset successfully. You can login now.', extra_tags='login')
    return response


class ProfileUpdateView(FormView):
    developer_form_class = DeveloperProfileForm
    recruiter_form_class = RecruiterProfileForm
    http_method_names = ['get', 'post']
    template_name = 'account/my_profile.html'

    def get(self, request, *args, **kwargs):
        profile = request.user.get_profile()
        return self.render_to_response(self.get_context_data(
            profile=profile,
            countries=COUNTRIES
        ))

    def post(self, request, *args, **kwargs):
        # Pass request to get_form_class and get_form for per-request
        # form control.
        form_class = self.get_form_class(request)
        form = self.get_form(form_class)
        if form.is_valid():
            # Pass request to form_valid.
            return self.form_valid(request, form)
        else:
            return self.form_invalid(request, form)

    def form_valid(self, request, form):
        profile = request.user.get_profile()
        profile.user.first_name = form.cleaned_data['first_name']
        profile.user.last_name = form.cleaned_data['last_name']
        profile.user.save()

        for key, value in form.cleaned_data.items():
            setattr(profile, key, value)
        profile.save()

        if profile.is_developer():
            developer_search.index(profile)

        messages.success(request, 'Success! Your profile has been successfully updated.', extra_tags='profile')
        return self.render_to_response(self.get_context_data(profile=profile, countries=COUNTRIES))

    def form_invalid(self, request, form):
        return self.render_to_response(self.get_context_data(form=form,
                                                             profile=request.user.get_profile(),
                                                             countries=COUNTRIES))

    def get_form_class(self, request=None):
        profile = request.user.get_profile()
        if profile.is_developer():
            return self.developer_form_class
        elif profile.is_recruiter():
            return self.recruiter_form_class


@login_required
def auto_complete_skills(request):
    status = 200
    if request.is_ajax():
        q = request.GET.get('q', '')
        skills = Skill.objects.filter(name__startswith=q.capitalize())[:10]
        results = []
        for s in skills:
            skill_json = {
                'id': s.id,
                'name': s.name
            }
            results.append(skill_json)
        data = json.dumps(results)
    else:
        data = 'fail'
        status = 400
    mimetype = 'application/json'
    return HttpResponse(data, mimetype, status=status)


def my_account(request):
    return redirect('profile_page')
