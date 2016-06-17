from django.contrib import admin

from .views import FacultyEmployeeRegistrationView, ReferentRegistrationView

admin.site.register_view(
    'register/faculty-employee',
    name='Registriraj delavca na fakulteti',
    urlname='register_faculty_employee',
    view=FacultyEmployeeRegistrationView.as_view())

admin.site.register_view(
    'register/referent',
    name='Registriraj referenta',
    urlname='register_referent',
    view=ReferentRegistrationView.as_view())
