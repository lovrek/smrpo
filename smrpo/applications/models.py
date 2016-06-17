# Create your models here.

from django.db import models

from information.models import Course
from students.models import Student


class ApplicationProperty(models.Model):
    open_datetime = models.DateTimeField(auto_now_add=True, blank=True)
    close_datetime = models.DateTimeField()


class ResultsMatura(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    matura = models.IntegerField(blank=True, null=True, verbose_name="Število točk na maturi")
    general_success = models.FloatField(blank=True, null=True)
    general_success_3 = models.IntegerField(blank=True, null=True, verbose_name="Končni uspeh v 3. letniku")
    general_success_4 = models.IntegerField(blank=True, null=True, verbose_name="Končni uspeh v 4. letniku")
    passed = models.BooleanField(verbose_name="Opravil maturo")
    student_type = models.IntegerField(blank=True, null=True)
    student_type_profession = models.IntegerField(blank=True, null=True)
    points_matura = models.FloatField(blank=True, null=True)
    points_general_success = models.FloatField(blank=True, null=True)

    course = models.ManyToManyField(Course, through='ResultsCourse')


class ResultsCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Ime predmeta")
    matura = models.ForeignKey(ResultsMatura, on_delete=models.CASCADE)
    result_on_matura = models.IntegerField(blank=True, null=True, verbose_name="Ocena na maturi")
    success_course_3_4 = models.FloatField(blank=True, null=True)
    success_course_3 = models.IntegerField(blank=True, null=True, verbose_name="Ocena v 3. letniku")
    success_course_4 = models.IntegerField(blank=True, null=True, verbose_name="Ocena v 4. letniku")
    passed = models.BooleanField(verbose_name="Opravil predmet")
    type_course = models.IntegerField(blank=True, null=True)
    type_course_profession = models.IntegerField(blank=True, null=True)
    points_result_on_matura = models.FloatField(blank=True, null=True)
    points_success_course_3= models.FloatField(blank=True, null=True)
    points_success_course_4 = models.FloatField(blank=True, null=True)
    def as_json(self):
        json = {"id": self.pk, "course": self.course, "result_on_matura": self.result_on_matura,
                "success_course_3_4": self.success_course_3_4, "success_course_3": self.success_course_3,
                "success_course_4": self.success_course_4, "passed": self.passed,
                "type_course_field": self.get_type(), "is_general": self.is_general()}
        return json

    def is_general(self):
        return self.type_course is not None

    def get_type(self):
        if self.is_general():
            return self.type_course
        else:
            return self.type_course_profession


