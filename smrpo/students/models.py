from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from information.models import Country, Nationality, Region, Post, FinishedEducation, HighSchool, Profession
from study_programs.models import StudyProgram


class Address(models.Model):
    street = models.CharField(max_length=45, verbose_name="Ulica")
    house_number = models.IntegerField(verbose_name="Hišna številka")
    additive = models.CharField(max_length = 1, blank=True, null=True, verbose_name="Hišni dodatek")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country', verbose_name="Država")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='region', verbose_name="Občina")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post', verbose_name="Pošta")


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    emso = models.CharField(max_length=45, blank=True, verbose_name="EMŠO")
    second_last_name = models.CharField(max_length=45, blank=True, null=True, verbose_name="Dekliški priimek")
    male = models.BooleanField(default=True, verbose_name="Spol")
    date_of_birth = models.DateField(auto_now=False, blank=True, null=True, verbose_name="Datum rojstva")
    city_of_birth = models.CharField(max_length=45, null=True, blank=True, verbose_name="Mesto rojstva")
    country_of_birth = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_of_birth', null=True, blank=True, verbose_name="Država rojstva")
    phone_number = models.CharField(max_length=45, null=True, blank=True, verbose_name="Telefonska številka")
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Državljanstvo")

    finished_education = models.ForeignKey(FinishedEducation, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Končana izobrazba")
    high_school = models.ForeignKey(HighSchool, on_delete=models.CASCADE, null=True, blank=True)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE, null=True, blank=True)

    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Stalno prebivališče")
    address_for_notice = models.ForeignKey(Address, related_name="address_for_notice", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Naslov za obveščanje")

    application_code = models.CharField(max_length=45, null=True, blank=True)
    application = models.ManyToManyField(StudyProgram, through='Applications', blank=True)

    def get_study_program_selection(self, priority):
        try:
            application = Applications.objects.filter(student_id=self.pk, priority=priority)[:1].get()
            application_string = application.study_program.name + " ("
            if application.irregular:
                application_string += "IZREDNI)"
            else:
                application_string += "REDNI)"
            return application_string + ", " + application.study_program.faculty.name + ", " \
                                 + application.study_program.faculty.university.name
        except ObjectDoesNotExist:
          return ""

    def as_json(self):
        json = {"id": self.pk, "application_code":self.application_code, "user__first_name": self.user.first_name, "user__last_name": self.user.last_name,
                "emso": self.emso, "second_last_name": self.second_last_name, "finished_education__description": self.finished_education.description,
                "first_selection": self.get_study_program_selection(1),
                "second_selection": self.get_study_program_selection(2),
                "third_selection": self.get_study_program_selection(3),
                }
        return json


class Applications(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    study_program = models.ForeignKey(StudyProgram, on_delete=models.CASCADE, verbose_name="Študijski program")
    priority = models.IntegerField()
    irregular = models.BooleanField(default=False, verbose_name="Način študija")
    timestamp = models.DateTimeField(auto_now=True)
    is_sent = models.BooleanField(default=False)
    points = models.FloatField(blank=True, null=True)
    points_matura = models.FloatField(blank=True, null=True)
    points_general_success = models.FloatField(blank=True, null=True)
    points_priority_course = models.FloatField(blank=True, null=True)
