from django import template

register = template.Library()


def get_hours_from_full_time_format(full_format):
    return str(full_format).split(':')[0]


def is_student(user):
    return user.is_authenticated() and hasattr(user, 'student')


def is_faculty_employee(user):
    return user.is_authenticated() and hasattr(user, 'faculty_employee')


def is_referent(user):
    return user.is_authenticated() and hasattr(user, 'referent')

register.filter('get_hours_from_full_time_format', get_hours_from_full_time_format)
register.filter('is_student', is_student)
register.filter('is_faculty_employee', is_faculty_employee)
register.filter('is_referent', is_referent)
