from django.contrib.auth.models import User
from django.db import models

from information.models import InformationBaseClassWithSifra


class University(InformationBaseClassWithSifra):
    name = models.CharField(max_length=45)

    def __str__(self):
        return self.name


class Faculty(InformationBaseClassWithSifra):
    name = models.CharField(max_length=45, blank=False)
    code = models.CharField(max_length=45, blank=False, unique=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.name + ' (' + self.code + ')'


class FacultyEmployee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_employee')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
