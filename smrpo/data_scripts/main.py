import csv
import datetime
import os
import random
import sys
from random import randrange, randint

import django

root_path = os.path.abspath(os.path.split(__file__)[0]).rsplit('/', 1)[0]
sys.path.insert(0, os.path.join(root_path, 'smrpo'))
sys.path.insert(0, root_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smrpo.settings")
django.setup()

from applications.views import generate_EMSO
from officials.models import *
from students.models import *
from faculties.models import *
from information.models import *
from study_programs.models import TypeRequirements, StudyProgram
from applications.models import ApplicationProperty


def requirements():
    TypeRequirements(name='Navadni', code='00', profession=0, course=0).save()
    TypeRequirements(name='Poljuben poklic, določen predmet', code='P1', profession=0,
                     course=1).save()
    TypeRequirements(name='Določen poklic, pogojno določeni predmet', code='P3', profession=1,
                     course=2).save()


def import_countries():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/Country.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    Country.objects.all().delete()
    for row in data_reader:
        object = Country(sifra=row[0], name=row[1], eu=row[2] == "D")
        object.save()


def import_nationalities():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/Nationality.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    Nationality.objects.all().delete()
    for row in data_reader:
        object = Nationality(sifra=row[0], description=row[1])
        object.save()


def import_regions():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/Region.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    slovenija = Country.objects.get(sifra="705")
    Region.objects.all().delete()
    for row in data_reader:
        object = Region(sifra=row[0], name=row[1], country_id=slovenija.pk)
        object.save()


def import_universities():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/University.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    University.objects.all().delete()
    for row in data_reader:
        object = University(sifra=row[0], name=row[1])
        object.save()


def import_professions():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/Profession.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    Profession.objects.all().delete()
    for row in data_reader:
        object = Profession(sifra=row[0], name=row[1])
        object.save()


def import_faculties():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/Faculty.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    Faculty.objects.all().delete()
    for row in data_reader:
        university = University.objects.get(sifra=row[4])
        object = Faculty(sifra=row[0], name=row[1], code=row[2], university_id=university.pk)
        object.save()


def import_posts():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/Post.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    Post.objects.all().delete()
    for row in data_reader:
        region = Region.objects.order_by('?').first()
        object = Post(zip_code=row[0], name=row[1], region_id=region.pk)
        object.save()


def import_high_schools():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/HighSchool.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    HighSchool.objects.all().delete()
    for row in data_reader:
        post = Post.objects.order_by('?').first()
        object = HighSchool(sifra=row[0], name=row[1], post_id=post.pk)
        object.save()


def import_courses():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/Course.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    Course.objects.all().delete()
    for row in data_reader:
        object = Course(sifra=row[0], name=row[1], is_general=random.choice([True, False]))
        object.save()


def import_study_programs():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/StudyProgram.csv"), delimiter=',',
                             quotechar='"')
    next(data_reader)
    StudyProgram.objects.all().delete()
    for row in data_reader:
        faculty = Faculty.objects.get(sifra=row[2])
        object = StudyProgram(code=row[3], name=row[4], faculty_id=faculty.pk)
        object.save()


def import_finished_educations():
    data_reader = csv.reader(open("/vagrant/smrpo/data_scripts/FinishedEducation.csv"),
                             delimiter=',', quotechar='"')
    next(data_reader)
    FinishedEducation.objects.all().delete()
    for row in data_reader:
        object = FinishedEducation(sifra=row[0], description=row[1])
        object.save()


def reset_database():
    print("Deleting database...")
    os.system('mysql -u root -psmrpo_uber_secure -e "DROP DATABASE IF EXISTS smrpo_db"')
    print("Database successfully deleted!")
    print("Creating database...")
    os.system('mysql -u root -psmrpo_uber_secure -e "create database smrpo_db character set utf8 collate utf8_general_ci"')
    os.system('mysql -u root -psmrpo_uber_secure -e "grant all privileges on smrpo_db.* to \'$smrpo_db_user\'@\'localhost\' identified by \'smrpo_uber_secure\'')
    print("Database successfully created...")
    print("Running migrations...")
    os.system("sudo python3.4 /vagrant/smrpo/manage.py makemigrations")
    os.system("sudo python3.4 /vagrant/smrpo/manage.py migrate")


def set_application_date():
    ApplicationProperty(open_datetime=datetime.date(2016, 1, 1),
                        close_datetime=datetime.date(2016, 9, 1)).save()


def create_super_user():
    user = User.objects.create_superuser("admin", None, "qweasd123")
    user.save()


def create_student(first_name, last_name):
    user = create_user(first_name, last_name)
    student = Student(user=user)
    student.save()
    return student


# TODO
def apply(student, is_sent=True):
    student.date_of_birth = datetime.date(randint(1990, 1996), randint(1, 12), randint(1, 30))
    nationality = random.choice([1] * 25 + [2, 3, 4, 5, 6])
    student.nationality = Nationality.objects.get(sifra=nationality)
    student.city_of_birth = "Random mesto "+str(randint(1,30))
    student.high_school = HighSchool.objects.order_by('?').first()
    student.profession = Profession.objects.order_by('?').first()
    country = None
    region = None
    post = None
    if True:
        country = Country.objects.get(sifra="705")
        student.country_of_birth = country
        region = Region.objects.filter(country_id=country.pk).order_by("?").first()
        post = Post.objects.filter(region_id=region.pk).order_by("?").first()
    else:
        country = Country.objects.order_by('?').first()
        student.country_of_birth = country
        region = Region.objects.get(sifra="0")
        post = Post.objects.get(zip_code="0")
    address = Address(street="Random ulica " + str(randint(1, 100)), house_number=randint(1, 30), country_id=country.pk, post_id=post.pk, region_id=region.pk)
    address.save()
    address_for_notice = Address(street="Random ulica " + str(randint(1, 100)), house_number=randint(1, 30), country_id=country.pk, post_id=post.pk, region_id=region.pk)
    address_for_notice.save()
    student.address = address
    student.address_for_notice = address_for_notice
    student.emso = generate_EMSO(student)
    student.phone_number = ''.join(str(random.choice([0,1,2,3,4,5,6,7,8,9])) for _ in range(9))
    student.finished_education = FinishedEducation.objects.get(sifra=random.choice([1]*3+[2]))
    student.application_code = str(datetime.datetime.now().year) + '-' + str(random.randrange(1, 999999)).zfill(6)
    student.save()
    for i in range(1, 4):
        study_program = StudyProgram.objects.order_by('?').first()
        application = Applications(student_id=student.pk, study_program_id=study_program.pk, priority=i, irregular=random.choice([True]*5+[False]), is_sent=is_sent)
        application.save()
        student.save()


def create_referent(first_name, last_name):
    user = create_user(first_name, last_name)
    referent = Referent(user=user)
    referent.save()


def create_faculty_employee(first_name, last_name, faculty):
    user = create_user(first_name, last_name)
    faculty_employee = FacultyEmployee(user=user, faculty_id=faculty.pk)
    faculty_employee.save()


def create_user(first_name, last_name):
    user = User.objects.create_user(first_name + last_name,
                                    first_name+last_name + "@gmail.com", "qweasd123")
    user.first_name = first_name
    user.last_name = last_name
    user.is_active = True
    user.save()
    return user


def delete_all_students():
    Student.objects.all().delete()


def delete_all_faculty_employees():
    FacultyEmployee.objects.all().delete()


def delete_all_referents():
    Referent.objects.all().delete()

if __name__ == '__main__':
    reset_database()
    print("Importing data...")
    create_super_user()
    set_application_date()
    requirements()
    import_countries()
    import_nationalities()
    import_regions()
    import_universities()
    import_professions()
    import_faculties()
    import_posts()
    import_high_schools()
    import_courses()
    import_study_programs()
    import_finished_educations()
    print("Data imported successfully!")
    create_referent("Referent", "Referent")

    create_faculty_employee("delavec", "FRI", Faculty.objects.get(sifra="63"))
    create_faculty_employee("delavec", "FMF", Faculty.objects.get(sifra="47"))
    create_faculty_employee("delavec", "BF", Faculty.objects.get(sifra="36"))

    first_names = ["Lana", "Sara", "Eva", "Nika", "Lara", "Ana", "Neža", "Zala", "Julija", "Ema",
                   "Nina", "Maša", "Hana", "Zoja", "Kaja", "Luka", "Jan", "Nejc", "Nik", "Žiga", "Žan",
                   "Jakob", "Jaka", "Matic", "Aljaž", "Anže", "Gal", "Mark", "Miha", "Filip"]

    last_names = ["Koren", "Jerman", "Majcen", "Jereb", "Pušnik", "Kranjc", "Rupnik", "Breznik",
                  "Lesjak", "Perko", "Furlan", "Dolenc", "Pečnik", "Vidic", "Pavlin", "Močnik", "Logar",
                  "Jenko", "Ribič", "Tomšič", "Kovačević", "Žnidaršič", "Janeži", "Maček", "Marolt",
                  "Jelen", "Černe", "Pintar", "Blatnik", "Gregorič", "Fras", "Zadravec", "Kokalj",
                  "Hren", "Lešnik", "Mihelič", "Bezjak", "Petrović"]

    student = create_user("Lovro", "Podgorsek")
    student = create_user("Tim", "Smole")
    for i in range(1, 2):
        first_name = randrange(0, len(first_names))
        last_name = randrange(0, len(last_names))
        student = create_student(first_names[first_name], last_names[last_name])
        student.male = first_name > 14
        apply(student)


