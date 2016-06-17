from django.conf.urls import url, include
from django.views.defaults import page_not_found
from django.contrib.auth import views as auth_views

from . import views, forms

urlpatterns = [
    # disable default register url first
    url(r'^register/$', page_not_found, kwargs={'exception': Exception("Bad Request")}),

    url(r'^register/student/$', view=views.StudentsRegistrationView.as_view(),
        name='register_student'),

    url(r'^login/$', auth_views.login, name='login'),

    url(r'^password/change/$', view=views.PasswordChangeFormView.as_view(), name='password_change'),

    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'set_password_form': forms.CustomSetPasswordForm},
        name='password_reset_confirm'),

    url(r'^password/reset/complete$', auth_views.password_reset_complete,
        name='password_reset_complete'),

    url(r'^', include('registration.backends.hmac.urls')),
]
