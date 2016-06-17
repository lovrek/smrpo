import json

from django.core import serializers
from django.db import models
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.fields.reverse_related import ManyToOneRel
from django.db.utils import IntegrityError
from django.utils.translation import ugettext


class InformationBaseClassManager(models.Manager):
    def get_by_natural_key(self, pk, name):
        return {"id": pk, "name": name}

    class Meta:
        abstract = True


class InformationBaseClass(models.Model):
    deleted = models.BooleanField(default=False)

    objects = InformationBaseClassManager()

    def clean(self):
        errors = list()
        fields = self.__class__.get_fields()
        index = 0
        for f in fields:
            value = getattr(self, fields[index].__dict__["name"], "")
            if value == "" or value is None:
                errors.append({"field": fields[index].__dict__["name"], "message": "Polje '"+ugettext(fields[index].__dict__["name"])+"' je obvezno!"})
        if len(errors) > 0:
            raise IntegrityError(errors)

    class Meta:
        abstract = True

    def natural_key(self):
        return self.pk, str(self)

    def as_json(self):
        serial_obj = serializers.serialize('json', [self], use_natural_foreign_keys=True)
        obj_as_dict = json.loads(serial_obj)[0]['fields']
        # obj_as_dict.pop("deleted", None)
        obj_as_dict['id'] = self.pk
        return obj_as_dict

    @classmethod
    def has_foreign_key_fields(cls):
        fields = cls.get_fields()
        for field in fields:
            if type(field) is ForeignKey or type(field) is ManyToManyField:
                return True
        return False

    @classmethod
    def json_to_object(cls, dct):
        obj = cls()
        for k, v in dct.items():
            if not (k == "id" and v == "") and not cls.is_m2m(k):
                setattr(obj, k, isinstance(v, dict) and obj.__class__(v) or v)
        obj.save()
        for k, v in dct.items():
            if cls.is_m2m(k):
                setattr(obj, k, [item[0] for item in v])
        return obj

    @classmethod
    def get_fields(cls):
        fields = []
        for f in cls._meta.get_fields():
            if type(f) == ManyToOneRel:
                continue
            fields.append(f)
        fields.pop(fields.index(cls._meta.get_field("id")))
        fields.pop(fields.index(cls._meta.get_field("deleted")))
        fields.insert(0, cls._meta.get_field("id"))
        return fields

    @classmethod
    def is_m2m(cls, field_name):
        field = cls._meta.get_field(field_name)
        return type(field) == ManyToManyField


class InformationBaseClassWithSifra(InformationBaseClass):
    sifra = models.CharField(unique=True, blank=False, max_length=40)

    class Meta:
        abstract = True


class Country(InformationBaseClassWithSifra):
    name = models.CharField(max_length=45, blank=False, unique=True)
    eu = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class Region(InformationBaseClassWithSifra):
    name = models.CharField(max_length=45, blank=False, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Post(InformationBaseClass):
    name = models.CharField(max_length=45, blank=False, unique=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=False)
    zip_code = models.CharField(max_length=45, blank=False, unique=True)

    def __str__(self):
        return self.zip_code+" - "+self.name

    class Meta:
        ordering = ('name',)


class Nationality(InformationBaseClassWithSifra):
    description = models.CharField(max_length=100, blank=False, unique=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('description',)


class HighSchool(InformationBaseClassWithSifra):
    name = models.CharField(max_length=45, blank=False, unique=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.name


class Profession(InformationBaseClassWithSifra):
    name = models.CharField(max_length=100, blank=False, unique=True)

    def __str__(self):
        return self.name


class Course(InformationBaseClassWithSifra):
    name = models.CharField(max_length=100, blank=False)
    is_general = models.BooleanField(default=False)

    @classmethod
    def get_fields(cls):
        fields = super(Course, cls).get_fields()
        fields.pop(fields.index(cls._meta.get_field("professionmatura")))
        fields.pop(fields.index(cls._meta.get_field("resultsmatura")))
        return fields

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Document(models.Model):
    file = models.FileField(upload_to='document/')


class FinishedEducation(InformationBaseClassWithSifra):
    description = models.CharField(max_length=100, blank=False, unique=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('description',)
