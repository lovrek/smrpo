from django import template
from django.db.models.fields import AutoField, BooleanField, CharField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.translation import ugettext

register = template.Library()


@register.filter
def column_name(field):
    column = str(field).split('.')[-1]
    for char in "<>\"'":
        column = column.replace(char, '')
    return column


@register.filter
def field_name(field):
    return str(field).split('.', 1)[1]


@register.filter
def get_type(field):
    return str(type(field))


@register.filter
def is_auto_field(field):
    return type(field) is AutoField


@register.filter
def is_boolean_field(field):
    return type(field) is BooleanField


@register.filter
def is_char_field(field):
    return type(field) is CharField

@register.filter
def is_foreign_key_field(field):
    return type(field) is ForeignKey

@register.filter
def is_many_to_many_field(field):
    return type(field) is ManyToManyField


@register.filter
def foreign_key_entity_type(field):
    if is_foreign_key_field(field):
        return column_name(field.rel.to)
    elif is_many_to_many_field(field):
        return column_name(field.__dict__["related_model"])


@register.filter
def trans(word):
    return ugettext(word)
