from django.contrib import admin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from registration.backends.hmac.views import RegistrationView

from faculties.models import FacultyEmployee
from officials.models import Referent
from students.models import Student
from .forms import CustomRegistrationForm, FacultyEmployeeRegistrationForm, CustomPasswordChangeForm


class StudentsRegistrationView(RegistrationView):
    form_class = CustomRegistrationForm
    template_name = "registration/registration_form_students.html"

    def create_inactive_user(self, form):
        registered_user = super(StudentsRegistrationView, self).create_inactive_user(form)
        registered_user = _save_first_last_name_to_user(registered_user, form.cleaned_data)
        student = Student(user=registered_user)
        student.save()
        return registered_user


class AdminRegistrationFormView(SuccessMessageMixin, FormView):
    success_url = reverse_lazy('admin:index')
    success_message = 'Uporabniški profil uspešno dodan.'

    def get_context_data(self, **kwargs):
        context = super(AdminRegistrationFormView, self).get_context_data(**kwargs)
        admin_context = admin.site.each_context(self.request)
        merged_context = context.copy()
        merged_context.update(admin_context)
        return merged_context


class FacultyEmployeeRegistrationView(AdminRegistrationFormView):
    form_class = FacultyEmployeeRegistrationForm
    template_name = "registration/admin_registration_form.html"

    def get_context_data(self, **kwargs):
        context = super(FacultyEmployeeRegistrationView, self).get_context_data(**kwargs)
        context['url'] = reverse_lazy('admin:register_faculty_employee')
        context['user_profile'] = "Delavec na fakulteti"
        return context

    def form_valid(self, form):
        registered_user = _save_auth_user(form.cleaned_data)
        f_employee = FacultyEmployee(user=registered_user, faculty=form.cleaned_data['faculty'])
        f_employee.save()
        return super(FacultyEmployeeRegistrationView, self).form_valid(form)


class ReferentRegistrationView(AdminRegistrationFormView):
    form_class = CustomRegistrationForm
    template_name = "registration/admin_registration_form.html"

    def get_context_data(self, **kwargs):
        context = super(ReferentRegistrationView, self).get_context_data(**kwargs)
        context['url'] = reverse_lazy('admin:register_referent')
        context['user_profile'] = "Referent"
        return context

    def form_valid(self, form):
        registered_user = _save_auth_user(form.cleaned_data)
        referent = Referent(user=registered_user)
        referent.save()
        return super(ReferentRegistrationView, self).form_valid(form)


def _save_auth_user(data):
    user = User.objects.create_user(data['username'], data['email'], data['password1'])
    return _save_first_last_name_to_user(user, data)


def _save_first_last_name_to_user(user, data):
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.save()
    return user


class PasswordChangeFormView(SuccessMessageMixin, FormView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('home')
    success_message = 'Vaše geslo je spremenjeno.'

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super(PasswordChangeFormView, self).form_valid(form)
