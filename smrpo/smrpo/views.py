from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

from login.templatetags.login_tags import is_student, is_faculty_employee, is_referent


def index(request):
    # todo fix redirects
    if is_faculty_employee(request.user):
        return HttpResponseRedirect(reverse_lazy('applications:index'))
    elif is_referent(request.user):
        return HttpResponseRedirect(reverse_lazy('applications:index'))
    elif is_student(request.user) or request.user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('applications:index'))
    else:
        return HttpResponseRedirect(reverse_lazy('login'))
