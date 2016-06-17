from functools import wraps

from django.http import HttpResponse
from django.utils.decorators import available_attrs


def student_required(function):
    return profile_required(function, 'student')


def faculty_employee_required(function):
    return profile_required(function, 'faculty_employee')


def referent_required(function):
    return profile_required(function, 'referent')


def profile_required(function, profile):
    @wraps(function, assigned=available_attrs(function))
    def wrapper(request, *args, **kwargs):
        if _auth_user_has_profile(request.user, profile):
            return function(request, *args, **kwargs)
        else:
            return HttpResponse(status=403)
    return wrapper


def _auth_user_has_profile(user, profile):
    return user.is_authenticated() and hasattr(user, profile)
