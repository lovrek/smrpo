from django.core.urlresolvers import reverse
from django.db import models

from faculties.models import Faculty
from information.models import Profession, InformationBaseClass, Course


class TypeRequirements(models.Model):
    name = models.CharField(max_length=45)
    code = models.CharField(max_length=45)
    profession = models.BooleanField(default=False)  # vrednosti 0 - poljuben poklic, 1 - dolocen poklic
    course = models.IntegerField()     # vrednosti 0 - maturitetni predmeti niso potrebni, 1 - poljuben predmet, 2 - obvezen predmet

    def __str__(self):
        return self.name

    def is_P0(self):
        return self.code == "00"

    def is_P1(self):
        return self.code == "P1"

    def is_P3(self):
        return self.code == "P3"


class GeneralMatura(models.Model):
    w_matura = models.FloatField()
    w_general_success = models.FloatField()
    w_priority_course_3_4 = models.FloatField(blank=True, null=True)
    w_priority_course_matura = models.FloatField(blank=True, null=True)


class ProfessionMatura(models.Model):
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, blank=True, null=True)
    matura_courses = models.ManyToManyField(Course)

    w_matura = models.FloatField()
    w_general_success = models.FloatField()
    w_matura_course = models.FloatField(blank=True, null=True)
    w_priority_course_3_4 = models.FloatField(blank=True, null=True)
    w_priority_course_matura = models.FloatField(blank=True, null=True)


class Slots(models.Model):
    enrolment_slots_EU = models.IntegerField(default=0, verbose_name='Vpisna mesta za državljane EU')
    enrolment_slots_other = models.IntegerField(default=0, verbose_name='Vpisna mesta za ostale')


class StudyProgram(InformationBaseClass):
    code = models.CharField(max_length=45, verbose_name='Šifra')
    name = models.CharField(max_length=100, verbose_name='Ime')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE,verbose_name='Fakulteta')
    general_matura = models.OneToOneField(GeneralMatura, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Splošna matura')
    profession_matura = models.OneToOneField(ProfessionMatura, on_delete=models.CASCADE, blank=True, null=True,verbose_name='Poklicna matura')
    type_requirements = models.ForeignKey(TypeRequirements, on_delete=models.CASCADE, null=True,verbose_name='Vpisni pogoj')
    priority_course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True,verbose_name='Prioritetni predmet')
    regular_slots = models.OneToOneField(Slots, on_delete=models.CASCADE, blank=True, null=True,verbose_name='Redni')
    irregular_slots = models.OneToOneField(Slots, related_name="irregular_slots", on_delete=models.CASCADE, blank=True, null=True,verbose_name='Izredni')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name + " (" + self.faculty.name + ")"

    def get_absolute_url(self):
        return reverse('study_programs:index')

    def clean(self):
        models.Model.clean(self)

    def get_slots(self, regular, eu):
        if regular and self.regular_slots is not None:
            if eu and self.regular_slots.enrolment_slots_EU is not None:
                return self.regular_slots.enrolment_slots_EU
            elif not eu and self.regular_slots.enrolment_slots_other is not None:
                return self.regular_slots.enrolment_slots_other
        elif not regular and self.irregular_slots is not None:
            if eu and self.irregular_slots.enrolment_slots_EU is not None:
                return self.irregular_slots.enrolment_slots_EU
            elif not eu and self.irregular_slots.enrolment_slots_other is not None:
                return self.irregular_slots.enrolment_slots_other
        return 0

    def as_json(self):
        json = {"id": self.pk, "code": self.code, "name": self.name, "faculty__name": self.faculty.name,
                "faculty__code": self.faculty.code, "faculty__university__name": self.faculty.university.name,
                "faculty__university__sifra": self.faculty.university.sifra,
                "regular_slots__enrolment_slots_EU": self.get_slots(True, True),
                "regular_slots__enrolment_slots_other": self.get_slots(True, False),
                "irregular_slots__enrolment_slots_EU": self.get_slots(False, True),
                "irregular_slots__enrolment_slots_other": self.get_slots(False, False),
                "deleted": self.deleted}
        return json

    def has_requirements(self):
        return self.type_requirements is not None

    def has_priority_course(self):
        return self.priority_course is not None
