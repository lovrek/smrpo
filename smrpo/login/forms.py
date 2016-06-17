from django.core.validators import RegexValidator, MinLengthValidator
from django.forms import CharField, ModelChoiceField
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from registration.forms import RegistrationFormUniqueEmail

from faculties.models import Faculty


class CustomRegistrationForm(RegistrationFormUniqueEmail):

    field_order = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    first_name = CharField(label="Ime")
    last_name = CharField(label="Priimek")

    def __init__(self, *args, **kwargs):
        super(CustomRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['email'].help_text = None
        self.fields['password1'].validators.append(_at_least_8_chars)
        self.fields['password1'].validators.append(_contains_digit)
        self.fields['password2'].validators.append(_at_least_8_chars)
        self.fields['password2'].validators.append(_contains_digit)
        self.fields['password2'].help_text = None


class FacultyEmployeeRegistrationForm(CustomRegistrationForm):
    faculty = ModelChoiceField(queryset=Faculty.objects.all(), empty_label='Fakulteta')


class CustomPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].validators.append(_at_least_8_chars)
        self.fields['new_password1'].validators.append(_contains_digit)
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].validators.append(_at_least_8_chars)
        self.fields['new_password2'].validators.append(_contains_digit)
        self.fields['new_password2'].help_text = None


class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].validators.append(_at_least_8_chars)
        self.fields['new_password1'].validators.append(_contains_digit)
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].validators.append(_at_least_8_chars)
        self.fields['new_password2'].validators.append(_contains_digit)
        self.fields['new_password2'].help_text = None


_contains_digit = RegexValidator(
    regex='\d',
    message='Geslo mora vsebovati vsaj en numeričen znak',
    code='invalid_password'
)

_at_least_8_chars = MinLengthValidator(
    8,
    message='Geslo mora biti dolgo vsaj 8 znakov'
)
