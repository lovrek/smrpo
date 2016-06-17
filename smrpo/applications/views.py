# Create your views here.
import datetime
import json
import random
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.base import Model
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from io import BytesIO
from random import randint

from django.utils.functional import curry
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from applications.forms import PersonalInformationForm, AddressForm, StudyProgramForm, UserForm, \
    ResultsMaturaForm, ResultsCourseForm
from applications.models import ApplicationProperty, ResultsMatura, ResultsCourse
from information.models import Profession, Course
from login.templatetags.login_tags import is_student, is_faculty_employee, is_referent
from students.models import Student, Applications
from study_programs.models import StudyProgram, ProfessionMatura, GeneralMatura

table_general_matura = {10: 40, 11: 45, 12: 47.5, 13: 50, 14: 55, 15: 60, 16: 65, 17: 67.5, 18: 70, 19: 75, 20: 80,
                        21: 85, 22: 87.5, 23: 90, 24: 91, 25: 92, 26: 93, 27: 94, 28: 95, 29: 95.8, 30: 96.7, 31: 97.5,
                        32: 98.3, 33: 99.2, 34: 100}
table_profession_matura = {8: 40, 9: 45, 10: 50, 11: 55, 12: 60, 13: 65, 14: 70, 15: 75, 16: 80, 17: 85, 18: 90, 19: 93,
                           20: 95, 21: 96.7, 22: 98.3, 23: 100}
table_2_to_5 = {2: 40, 3: 60, 4: 80, 5: 100}
table_2_to_8 = {2: 40, 3: 50, 4: 60, 5: 70, 6: 80, 7: 90, 8: 100}
courses_high_level = ["M101", "M103", "M131", "M191", "M201", "M211", "M212", "M221", "M222", "M231", "M241", "M241",
                      "M251", "M252", "M261", "M262", "M271", "M272", "M281", "M282", "M291", "M292", "M301", "M302",
                      "M401", "M402"]


@login_required
def index(request):
    closed = is_application_closed()
    # if not hasattr(request.user, "student"):
    if is_faculty_employee(request.user) or is_referent(request.user):
        return render(request, 'applications/index_zaposleni.html', {})
    elif is_student(request.user):
        applications = Applications.objects.filter(student_id=request.user.student.pk).order_by("priority")
        if len(applications) > 0:
            return render(request, 'applications/index.html', {"applications": applications, "closed": closed})
    if closed:
        return render(request, 'applications/end_of_applications.html')
    return redirect('/application/add')


@login_required
def add(request, student_id=None):
    if is_student(request.user) and is_application_closed() or is_faculty_employee(request.user):
        return redirect('/application/')
    student = user = address = address_for_notice = first_selection = second_selection = third_selection = region = post = region_for_notice = post_for_notice = None
    if is_student(request.user):
        student = request.user.student
    elif student_id is not None:
        student = Student.objects.get(pk=student_id)
    if student is not None:
        user = student.user
        address = student.address
        address_for_notice = student.address_for_notice
        if student.address is not None:
            region = student.address.region
            post = student.address.post
        if student.address_for_notice is not None:
            region_for_notice = student.address_for_notice.region
            post_for_notice = student.address_for_notice.post
        applications = Applications.objects.filter(student_id=student.pk).order_by("priority")
        if len(applications) > 0:
            first_selection = applications[0]
            if len(applications) > 1:
                second_selection = applications[1]
                if len(applications) > 2:
                    third_selection = applications[2]
    elif not is_referent(request.user) and not is_faculty_employee(request.user):
        user = request.user
    if request.method == "GET":
        user_form = UserForm(prefix="user_form", instance=user)
        personal_info_form = PersonalInformationForm(prefix="personal_info_form", instance=student)
        address_form = AddressForm(prefix="address_form", instance=address, post=post, region=region)
        address_for_notice_form = AddressForm(prefix="address_for_notice_form", instance=address_for_notice,
                                              post=post_for_notice, region=region_for_notice)
        select_study_program_form1 = StudyProgramForm(prefix="select_study_program_form1", priority=1,
                                                      instance=first_selection)
        select_study_program_form2 = StudyProgramForm(prefix="select_study_program_form2", priority=2,
                                                      instance=second_selection)
        select_study_program_form3 = StudyProgramForm(prefix="select_study_program_form3", priority=3,
                                                      instance=third_selection)
        return render(request, 'applications/add.html',
                      {"student": student, "user_form": user_form, "personal_info_form": personal_info_form,
                       "address_form": address_form,
                       "address_for_notice_form": address_for_notice_form,
                       "select_study_program_form1": select_study_program_form1,
                       "select_study_program_form2": select_study_program_form2,
                       "select_study_program_form3": select_study_program_form3})
    elif request.method == "POST":
        user_form = UserForm(request.POST, prefix="user_form", instance=user)
        personal_info_form = PersonalInformationForm(request.POST, prefix="personal_info_form", instance=student)
        address_form = AddressForm(request.POST, prefix="address_form", instance=address)
        address_for_notice_form = AddressForm(request.POST, prefix="address_for_notice_form",
                                              instance=address_for_notice)
        select_study_program_form1 = StudyProgramForm(request.POST, prefix="select_study_program_form1", priority=1,
                                                      instance=first_selection)
        select_study_program_form2 = StudyProgramForm(request.POST, prefix="select_study_program_form2", priority=2,
                                                      instance=second_selection)
        select_study_program_form3 = StudyProgramForm(request.POST, prefix="select_study_program_form3", priority=3,
                                                      instance=third_selection)

        if personal_info_form.is_valid() and user_form.is_valid():
            student = personal_info_form.save(commit=False)
            if student.emso is None or student.emso == "":
                student.emso = generate_EMSO(student)
            user = user_form.save(commit=False)
            if user.username is None or user.username == "":
                user.username = user.first_name + user.last_name + str(randint(100, 999))
            if address_form.is_valid():
                address = address_form.save(commit=False)
                if (address_for_notice_form.is_valid()):
                    address_for_notice = address_for_notice_form.save(commit=False)
                    address.save()
                    address_for_notice.save()
                    user.save()
                    student.user = user
                    student.address = address
                    student.address_for_notice = address_for_notice
                    student.application_code = str(datetime.datetime.now().year) + '-' + str(
                        random.randrange(1, 999999)).zfill(6)
                    student.save()
                    if is_student(request.user):
                        request.user.student = student
                if select_study_program_form1.is_valid():
                    select1 = select_study_program_form1.save(commit=False)
                    select1.student = student
                    if is_referent(request.user):
                        select1.is_sent = True
                    select1.save()

                    is_second_selected = False
                    if (select_study_program_form2.is_valid()):
                        select2 = select_study_program_form2.save(commit=False)
                        select2.student = student
                        if is_referent(request.user):
                            select2.is_sent = True
                        select2.save()
                        is_second_selected = True
                    elif second_selection:
                        second_selection.delete()
                    if (select_study_program_form3.is_valid()):
                        select3 = select_study_program_form3.save(commit=False)
                        select3.student = student
                        if not is_second_selected:
                            select3.priority = 2
                        if is_referent(request.user):
                            select3.is_sent = True
                        select3.save()
                    elif third_selection:
                        third_selection.delete()
        return redirect('/application/')


def generate_EMSO(student):
    date = student.date_of_birth.strftime('%d.%m.%Y')
    day = date.split('.')[0]
    month = date.split('.')[1]
    year = date.split('.')[2][1:]

    if student.male:
        male = '500'
    else:
        male = '505'
    random_code = str(random.randrange(1, 99)).zfill(2)
    emso = day + month + year + male + random_code
    emso_factor_map = [7, 6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    emso_sum = 0
    for digit in range(12):
        emso_sum += int(str(emso)[digit]) * emso_factor_map[digit]
    control_digit = 11 - (emso_sum % 11)
    return emso + str(control_digit)


def students(request):
    if request.method == "GET":
        student_ids = Applications.objects.filter(is_sent=True).values('student')
        filter_dict = {"pk__in": student_ids}
        first_selection_query = None
        second_selection_query = None
        third_selection_query = None
        for k, v in dict(request.GET).items():
            if (k == "_"):
                break
            elif k == "first_selection":
                first_selection_query = v[0].lower()
            elif k == "second_selection":
                second_selection_query = v[0].lower()
            elif k == "third_selection":
                third_selection_query = v[0].lower()
            else:
                filter_dict.update({k + "__icontains": v[0]})
        objects = Student.objects.filter(**filter_dict)

        faculty = None
        if is_faculty_employee(request.user):
            faculty = request.user.faculty_employee.faculty.name
        results = []
        for ob in objects:
            as_json = ob.as_json()
            number_of_displayed_selections = 3
            if faculty is not None:
                split = as_json["first_selection"].split(", ")
                if len(split) > 2 and split[1] != faculty:
                    number_of_displayed_selections -= 1
                    as_json["first_selection"] = ""
                split = as_json["second_selection"].split(", ")
                if len(split) > 2 and split[1] != faculty:
                    number_of_displayed_selections -= 1
                    as_json["second_selection"] = ""
                split = as_json["third_selection"].split(", ")
                if len(split) > 2 and split[1] != faculty:
                    number_of_displayed_selections -= 1
                    as_json["third_selection"] = ""
            if number_of_displayed_selections != 0:
                if first_selection_query is not None and first_selection_query in as_json["first_selection"].lower():
                    results.append(as_json)
                if second_selection_query is not None and second_selection_query in as_json["second_selection"].lower():
                    results.append(as_json)
                if third_selection_query is not None and third_selection_query in as_json["third_selection"].lower():
                    results.append(as_json)
                if first_selection_query is None and second_selection_query is None and third_selection_query is None:
                    results.append(as_json)
        return HttpResponse(json.dumps(results), content_type="application/json")


def delete(request, student_id=None):
    if is_student(request.user):
        student_id = request.user.student.pk
    Applications.objects.filter(student_id=student_id).delete()
    return redirect('/application/')


def send(request):
    if is_student(request.user):
        Applications.objects.filter(student_id=request.user.student.pk).update(is_sent=True)
    return redirect('/application/')


def is_application_closed():
    application_time = ApplicationProperty.objects.get(pk=1)
    return application_time.close_datetime < timezone.now()


def download_PDF(request, student_id=None):
    if is_student(request.user):
        student_id = request.user.student.pk
    elif student_id is None:
        return
    student = Student.objects.get(id=student_id)
    applications = Applications.objects.filter(student_id=student_id)

    pdf = generate_pdf(student, applications)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prijava.pdf"'
    response.write(pdf)
    return response


def list_of_candidates_PDF(request):
    students = Student.objects.exclude(application_code__isnull=True)
    users = []
    # for student in allStudents:
    #     if Applications.objects.filter(student=student.id):
    #         users.append(User.objects.get(pk=student.user))

    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="seznam_kandidatov.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)
    max_width = 595
    max_heigth = 842
    width = 50
    heigth = 750

    p.setFont('VeraBd', 20)
    p.drawCentredString(max_width / 2.0, heigth, "Seznam vpisanih kandidatov")
    p.setFont('Vera', 14)
    heigth -= 40
    p.drawString(width + 15, heigth, "Ime kandidata")
    p.drawString(width + 130, heigth, "Priimek kandidata")
    p.drawString(width + 280, heigth, "Št. prijave")
    p.drawString(width + 380, heigth, "Izobrazba")
    heigth -= 20
    p.line(30, heigth, max_width - 30, heigth)
    heigth -= 40
    p.setFont('Vera', 10)

    counter = 1
    for student in students:
        if heigth < 120:
            p.line(50, 100, max_width - 50, 100)
            p.showPage()
            p.setFont('Vera', 14)
            heigth = 750
            p.drawString(width + 15, heigth, "Ime kandidata")
            p.drawString(width + 130, heigth, "Priimek kandidata")
            p.drawString(width + 280, heigth, "Številka prijave")
            p.drawString(width + 380, heigth, "Izobrazba")
            heigth -= 20
            p.line(30, heigth, max_width - 30, heigth)
            heigth -= 40
            p.setFont('Vera', 10)

        p.drawString(width - 10, heigth, str(counter) + '.')
        p.drawString(width + 15, heigth, student.user.first_name)
        p.drawString(width + 130, heigth, student.user.last_name)
        p.drawString(width + 280, heigth, student.application_code)
        p.drawString(width + 380, heigth, student.finished_education.description)
        heigth -= 20
        counter += 1

    p.line(50, 100, max_width - 50, 100)
    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def display_PDF(request):
    if is_student(request.user):
        student = Student.objects.get(user_id=request.user.id)
        applications = Applications.objects.filter(student=request.user.student)

        pdf = generate_pdf(student, applications)

        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="prijava.pdf"'
        response.write(pdf)
        return response


def generate_pdf(student, applications):
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
    buffer = BytesIO()
    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)
    max_width = 595
    width = 50
    heigth = 750
    p.setFont('VeraBd', 20)
    p.drawCentredString(max_width / 2.0, heigth, "Prijava na fakulteto")
    p.setFont('Vera', 12)
    heigth -= 20
    # Splosi podatki
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    p.drawString(width, heigth, "Vrsta prijave:")
    p.drawString(width + 110, heigth, "Vpis v 1. letnik")
    p.drawString(max_width - 300, heigth, "Številka prijave:")
    p.drawString(max_width - 200, heigth, student.application_code)
    heigth -= 20
    p.drawString(width, heigth, "Stopnja:")
    p.drawString(width + 110, heigth, "Prva stopnja")
    p.drawString(max_width - 300, heigth, "Datum: ")
    for application in applications:
        p.drawString(max_width - 200, heigth, application.timestamp.strftime('%d.%m.%Y'))
        break;
    heigth -= 40
    # Osebni podatki
    p.setFont('VeraBd', 14)
    p.drawString(width, heigth, "OSEBNI PODATKI")
    p.setFont('Vera', 12)
    heigth -= 10
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    p.drawString(width, heigth, "Ime in priimek:")
    p.drawString(width + 110, heigth, student.user.first_name + ' ' + student.user.last_name)
    heigth -= 20
    p.drawString(width, heigth, "Dekliški priimek:")
    if student.second_last_name != None:
        p.drawString(width + 110, heigth, student.second_last_name)
    else:
        p.drawString(width + 110, heigth, "")
    heigth -= 20
    p.drawString(width, heigth, "EMŠO:")
    p.drawString(width + 110, heigth, student.emso)
    p.drawString(max_width - 300, heigth, "Spol:")
    if student.male:
        p.drawString(max_width - 200, heigth, "Moški")
    else:
        p.drawString(max_width - 200, heigth, "Ženski")
    heigth -= 20
    p.drawString(width, heigth, "Datum rojstva:")
    p.drawString(width + 110, heigth, student.date_of_birth.strftime('%d.%m.%Y'))
    p.drawString(max_width - 300, heigth, "Država in kraj:")
    p.drawString(max_width - 200, heigth,
                 student.country_of_birth.name + ', ' + student.city_of_birth)
    heigth -= 20
    p.drawString(width, heigth, "Kontaktni telefon:")
    p.drawString(width + 110, heigth, student.phone_number)
    p.drawString(max_width - 300, heigth, "E-pošta:")
    p.drawString(max_width - 200, heigth, student.user.email)
    heigth -= 40
    # Naslov stalnega bivališča
    p.setFont('VeraBd', 14)
    p.drawString(width, heigth, "NASLOV STALNEGA BIVALIŠČA")
    p.setFont('Vera', 12)
    heigth -= 10
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    p.drawString(width, heigth, "Naslov:")
    if student.address.additive != None:
        p.drawString(width + 110, heigth, student.address.street + ' ' + str(
            student.address.house_number) + student.address.additive + ', ' + student.address.region.name + ', ' + student.address.post.zip_code + '-' + student.address.post.name)
    else:
        p.drawString(width + 110, heigth, student.address.street + ' ' + str(
            student.address.house_number) + ', ' + student.address.region.name + ', ' + student.address.post.zip_code + '-' + student.address.post.name)
    heigth -= 20
    p.drawString(width, heigth, "Država:")
    p.drawString(width + 110, heigth, student.address.country.name)
    heigth -= 40
    # Naslov za obvestila
    p.setFont('VeraBd', 14)
    p.drawString(width, heigth, "NASLOV ZA OBVESTILA")
    p.setFont('Vera', 12)
    heigth -= 10
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    p.drawString(width, heigth, "Ime in priimek:")
    p.drawString(width + 110, heigth, student.user.first_name + ' ' + student.user.last_name)
    heigth -= 20
    p.drawString(width, heigth, "Država:")
    p.drawString(width + 110, heigth, student.address_for_notice.country.name)
    heigth -= 20
    p.drawString(width, heigth, "Naslov:")
    if student.address_for_notice.additive != None:
        p.drawString(width + 110, heigth, student.address_for_notice.region.name + ' ' + str(
            student.address_for_notice.house_number) + student.address_for_notice.additive + ', ' + student.address_for_notice.region.name + ', ' + student.address_for_notice.post.zip_code + '-' + student.address_for_notice.post.name)
    else:
        p.drawString(width + 110, heigth, student.address_for_notice.region.name + ' ' + str(
            student.address_for_notice.house_number) + ', ' + student.address_for_notice.region.name + ', ' + student.address_for_notice.post.zip_code + '-' + student.address_for_notice.post.name)
    heigth -= 40
    # Podatki o državljanstvu
    p.setFont('VeraBd', 14)
    p.drawString(width, heigth, "PODATKI O DRŽAVLJANSTVU")
    p.setFont('Vera', 12)
    heigth -= 10
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    p.drawString(width, heigth, "Državljanstvo:")
    p.drawString(width + 110, heigth, student.nationality.description)

    heigth -= 40
    for application in applications:
        if heigth < 150:
            p.showPage()
            heigth = 750
        # Izbrani študijski programi
        p.setFont('VeraBd', 14)
        p.drawString(width, heigth, str(application.priority) + '. ' + "IZBRANI ŠTUDIJSKI PROGRAMI")
        p.setFont('Vera', 12)
        heigth -= 10
        p.line(30, heigth, max_width - 30, heigth)
        p.line(30, heigth - 1, max_width - 30, heigth - 1)
        heigth -= 20
        p.drawString(width, heigth, "Univerza:")
        p.drawString(width + 140, heigth, str(application.study_program.faculty.university.name))
        heigth -= 20
        p.drawString(width, heigth, "Visokošoljski zavod:")
        p.drawString(width + 140, heigth, application.study_program.faculty.name)
        heigth -= 20
        p.drawString(width, heigth, "Študijski program:")
        p.drawString(width + 140, heigth, application.study_program.name)
        heigth -= 20
        p.drawString(width, heigth, "Trenutna izobrazba:")
        p.drawString(width + 140, heigth, student.finished_education.description)
        heigth -= 20
        p.drawString(width, heigth, "Način študija:")
        if application.irregular:
            p.drawString(width + 140, heigth, "Izredni")
        else:
            p.drawString(width + 140, heigth, "Redni")
        heigth -= 40

    # Zadna vrstica za podpis
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth, 30, heigth - 20)
    p.line(max_width - 30, heigth, max_width - 30, heigth - 20)
    p.line(30, heigth - 20, max_width - 30, heigth - 20)
    p.drawString(width, heigth - 14, "Datum:")
    p.line(width + 60, heigth, width + 60, heigth - 20)
    p.drawString(width + 80, heigth - 14, datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
    p.line(width + 230, heigth, width + 230, heigth - 20)
    p.drawString(width + 250, heigth - 14, "Podpis:")
    p.line(width + 315, heigth, width + 315, heigth - 20)
    # Close the PDF object cleanly.
    p.showPage()
    p.save()
    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def compute_points(request,user_id):
    # user_id = 1
    student = Student.objects.get(user=user_id)
    matura = ResultsMatura.objects.get(student=student)
    applications = Applications.objects.filter(student_id=student.id).order_by("priority")
    for application in applications:
        if application.study_program.type_requirements.is_P0():
            p = compute_points_for_P0(application, matura)
        elif application.study_program.type_requirements.is_P1():
            p = compute_points_for_P1(application, matura)
        elif application.study_program.type_requirements.is_P3():
            p = compute_points_for_P3(application, matura)
        application.points = p
        application.save()
    return redirect('/application/')

def compute_points_for_P0(application, matura):
    study_program = StudyProgram.objects.get(applications=application)
    points = 0
    if matura.student_type is not None:
        if matura.passed:
            Matura = study_program.general_matura.w_matura * table_general_matura[matura.matura]
            General_success = study_program.general_matura.w_general_success * matura.general_success * 2 * 10
            matura.points_matura = table_general_matura[matura.matura]
            points = Matura + General_success
            matura.points_general_success = matura.general_success * 2 * 10
            matura.save()
            # points = Matura + General_success
            application.points_matura = Matura
            application.points_general_success = General_success
            application.save()
    else:
        if matura.passed:
            Matura = study_program.profession_matura.w_matura * table_profession_matura[matura.matura]
            General_success = study_program.profession_matura.w_general_success * matura.general_success * 2 * 10
            matura.points_matura = table_profession_matura[matura.matura]
            points = Matura + General_success
            matura.points_general_success = matura.general_success * 2 * 10
            matura.save()
            # points = Matura + General_success
            application.points_matura = Matura
            application.points_general_success = General_success
            application.save()

    return points


def compute_points_for_P1(application, matura):
    study_program = StudyProgram.objects.get(applications=application)
    if study_program.priority_course in matura.course.all():
        course = ResultsCourse.objects.get(matura=matura, course=study_program.priority_course)
    else:
        course = None

    points = 0
    if matura.student_type is not None and matura.passed:
        if study_program.priority_course is not None and course is not None and course.passed:
            Matura = study_program.general_matura.w_matura * table_general_matura[matura.matura]
            General_success = study_program.general_matura.w_general_success * matura.general_success * 2 * 10
            Priority_course_3_4 = study_program.general_matura.w_priority_course_3_4 * course.success_course_3_4 * 2 * 10
            if study_program.priority_course.sifra in courses_high_level:
                Priority_course_matura = study_program.general_matura.w_priority_course_matura * table_2_to_8[course.result_on_matura]
                course.points_result_on_matura = table_2_to_8[course.result_on_matura]
                application.points_priority_course = Priority_course_matura
            else:
                Priority_course_matura = study_program.general_matura.w_priority_course_matura * table_2_to_5[course.result_on_matura]
                course.points_result_on_matura = table_2_to_5[course.result_on_matura]
                application.points_priority_course = Priority_course_matura
            points = Matura + General_success + Priority_course_3_4 + Priority_course_matura
            matura.points_matura = table_general_matura[matura.matura]
            matura.points_general_success = matura.general_success * 2 * 10
            matura.save()
            course.points_success_course_3 = course.success_course_3*10
            course.points_success_course_4 = course.success_course_4*10
            course.save()
            application.points_matura = Matura
            application.points_general_success = General_success
            application.save()
        elif study_program.priority_course is None:
            Matura = study_program.general_matura.w_matura * table_general_matura[matura.matura]
            General_success = study_program.general_matura.w_general_success * matura.general_success * 2 * 10
            points = Matura + General_success
            matura.points_matura = table_general_matura[matura.matura]
            matura.points_general_success = matura.general_success * 2 * 10
            matura.save()
            application.points_matura = Matura
            application.points_general_success = General_success
            application.save()
    else:
        if matura.passed:
            if study_program.priority_course is not None and course is not None and course.passed:
                Matura = study_program.profession_matura.w_matura * table_profession_matura[matura.matura]
                General_success = study_program.profession_matura.w_general_success * matura.general_success * 2 * 10
                Priority_course_3_4 = study_program.profession_matura.w_priority_course_3_4 * course.success_course_3_4 * 2 * 10
                if study_program.priority_course.sifra in courses_high_level:
                    Priority_course_matura = study_program.profession_matura.w_priority_course_matura * table_2_to_8[course.result_on_matura]
                    course.points_result_on_matura = table_2_to_8[course.result_on_matura]
                    application.points_priority_course = Priority_course_matura
                else:
                    Priority_course_matura = study_program.profession_matura.w_priority_course_matura * table_2_to_5[course.result_on_matura]
                    course.points_result_on_matura = table_2_to_5[course.result_on_matura]
                    application.points_priority_course = Priority_course_matura
                points = Matura + General_success + Priority_course_3_4 + Priority_course_matura
                course.points_success_course_3 = course.success_course_3*10
                course.points_success_course_4 = course.success_course_4*10
                course.save()
                matura.points_matura = table_profession_matura[matura.matura]
                matura.points_general_success = matura.general_success * 2 * 10
                matura.save()
                application.points_matura = Matura
                application.points_general_success = General_success
                application.save()
            elif study_program.priority_course is None:
                if ResultsCourse.objects.filter(matura=matura,type_course_profession=5).exists():
                    matura_course = ResultsCourse.objects.get(matura=matura,type_course_profession=5)
                    if study_program.profession_matura.matura_courses.filter(sifra = matura_course.course.sifra) and matura_course.passed:
                        Matura = study_program.profession_matura.w_matura * table_profession_matura[matura.matura]
                        General_success = study_program.profession_matura.w_general_success * matura.general_success * 2 * 10
                        Matura_course = 0
                        if matura_course.course.sifra in courses_high_level:
                            Matura_course = study_program.profession_matura.w_matura_course * table_2_to_8[matura_course.result_on_matura]
                            matura_course.points_result_on_matura = table_2_to_8[matura_course.result_on_matura]
                            application.points_priority_course = Matura_course
                        else:
                            Matura_course = study_program.profession_matura.w_matura_course * table_2_to_5[matura_course.result_on_matura]
                            matura_course.points_result_on_matura = table_2_to_5[matura_course.result_on_matura]
                            application.points_priority_course = Matura_course
                        points = Matura + General_success + Matura_course
                        matura.points_matura = table_profession_matura[matura.matura]
                        matura.points_general_success = matura.general_success * 2 * 10
                        matura.save()
                        application.points_matura = Matura
                        application.points_general_success = General_success
                        application.save()
    return points


def compute_points_for_P3(application, matura):
    study_program = StudyProgram.objects.get(applications=application)
    points = 0
    if matura.student_type is not None and matura.passed:
        Matura = study_program.general_matura.w_matura * table_general_matura[matura.matura]
        General_success = study_program.general_matura.w_general_success * matura.general_success*2*10
        points = Matura + General_success
        matura.points_matura = table_general_matura[matura.matura]
        matura.points_general_success = matura.general_success * 2 * 10
        matura.save()
        application.points_matura = Matura
        application.points_general_success = General_success
        application.save()
    else:
        if matura.passed and study_program.profession_matura.profession.sifra == matura.student.profession.sifra:
            if study_program.profession_matura.matura_courses.all().count() == 1 and ResultsCourse.objects.filter(matura=matura,type_course_profession=5).exists():
                required_course = study_program.profession_matura.matura_courses.all()[0]
                matura_course = 0
                course_name = required_course.name[0:required_course.name.find('(')]
                for x in Course.objects.all():
                    if x.name[0:x.name.find('(')] == course_name:
                        for course in ResultsCourse.objects.filter(matura=matura):
                            if course.course.sifra == x.sifra:
                                matura_course = course

                if matura_course.type_course_profession != 5 and matura_course.passed:
                    for course in ResultsCourse.objects.filter(matura=matura):
                        if course.type_course_profession == 5:
                            matura_course = course
                            break
                        else:
                            return 0

                Matura = study_program.profession_matura.w_matura * table_profession_matura[matura.matura]
                General_success = study_program.profession_matura.w_general_success * matura.general_success*2*10
                if matura_course.course.sifra in courses_high_level:
                    Matura_course = study_program.profession_matura.w_matura_course * table_2_to_8[matura_course.result_on_matura]
                    matura_course.points_result_on_matura = table_2_to_8[matura_course.result_on_matura]
                    application.points_priority_course = Matura_course
                else:
                    Matura_course = study_program.profession_matura.w_matura_course * table_2_to_5[matura_course.result_on_matura]
                    matura_course.points_result_on_matura = table_2_to_5[matura_course.result_on_matura]
                    application.points_priority_course = Matura_course
                matura_course.save()
                points = Matura + General_success + Matura_course
                matura.points_matura = table_profession_matura[matura.matura]
                matura.points_general_success = matura.general_success * 2 * 10
                matura.save()
                application.points_matura = Matura
                application.points_general_success = General_success
                application.save()
    return points


def details(request, student_id):
    student = Student.objects.get(pk=student_id)
    try:
        matura = ResultsMatura.objects.get(student=student)
        courses_on_matura = ResultsCourse.objects.filter(matura=matura)
        applications = Applications.objects.filter(student=student)
    except ObjectDoesNotExist:
        return redirect("/application/"+str(student.pk)+"/add_matura_info")

    compute_points(request,student.user.id)


    context = {
        'student': student,
        'matura':matura,
        'courses_on_matura':courses_on_matura,
        'applications':applications,
    }
    return render(request, 'applications/show_details.html', context)

def detailsPDF(request, student_id):
    student = Student.objects.get(pk=student_id)
    matura = ResultsMatura.objects.get(student=student)
    courses_on_matura = ResultsCourse.objects.filter(matura=matura)
    applications = Applications.objects.filter(student=student)

    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+ student.user.first_name + student.user.last_name +'.pdf"'

    buffer = BytesIO()
    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)
    max_width = 595
    width = 50
    heigth = 750
    shift = 130
    p.setFont('VeraBd', 20)
    p.drawCentredString(max_width / 2.0, heigth, "Podatki o kandidatu")
    p.setFont('Vera', 12)
    heigth -= 20
    # Splosi podatki
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    p.drawString(width, heigth, "Ime in priimek:")
    if student.second_last_name is not None:
        p.drawString(width+shift, heigth, student.user.first_name + ' ' + student.user.last_name + ' ' + student.second_last_name)
    else:
        p.drawString(width+shift, heigth, student.user.first_name + ' ' + student.user.last_name)
    heigth -= 20
    p.drawString(width, heigth, "Srednja šola:")
    if student.high_school is not None:
        p.drawString(width+shift, heigth, student.high_school.name)
    else:
        p.drawString(width+shift, heigth, "Ni podatka o srednji šoli.")
    heigth -= 20
    p.drawString(width, heigth, "Poklic:")
    if student.profession is not None:
        p.drawString(width+shift, heigth, student.profession.name)
    else:
        p.drawString(width+shift, heigth, "Ni podatka o poklicu.")
    heigth -= 40

    #Podatki o uspehu
    p.setFont('VeraBd', 14)
    p.drawString(width, heigth, "PODATKI O USPEHU")
    p.setFont('Vera', 12)
    heigth-= 10
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    p.drawString(width, heigth, "Tip mature:")
    if matura.student_type is not None:
        p.drawString(width+shift, heigth, "Splošna matura")
    else:
        p.drawString(width+shift, heigth, "Poklicna matura")
    heigth -= 20
    p.drawString(width, heigth, "Točke na maturi:")
    p.drawString(width+shift, heigth, str(matura.matura))
    heigth -= 20
    p.drawString(width, heigth, "Splošni uspeh v 3. letniku:")
    p.drawString(width+shift + 40, heigth, str(matura.general_success_3))
    heigth -= 20
    p.drawString(width, heigth, "Splošni uspeh v 4. letniku:")
    p.drawString(width+shift + 40, heigth, str(matura.general_success_4))
    heigth -= 40

    p.setFont('VeraBd', 14)
    p.drawString(width, heigth, "Predmet")
    p.drawString(width+shift+150, heigth, "Ocena")
    p.drawString(width+shift+210, heigth, "Ocena v 3.")
    p.drawString(width+shift+300, heigth, "Ocena v 4.")
    p.setFont('Vera', 12)
    heigth -= 10
    p.line(width,heigth, max_width-width,heigth)
    heigth -= 20
    for course in courses_on_matura:
        p.drawString(width, heigth, course.course.name)
        p.drawString(width+shift+170, heigth, str(course.result_on_matura))
        p.drawString(width+shift+230, heigth, str(course.success_course_3))
        p.drawString(width+shift+320, heigth, str(course.success_course_4))
        heigth -= 20

    heigth -= 20
    p.setFont('VeraBd', 14)
    p.drawString(width, heigth, "PODATKI O PRIJAVI")
    p.setFont('Vera', 12)
    heigth -= 10
    p.line(30, heigth, max_width - 30, heigth)
    p.line(30, heigth - 1, max_width - 30, heigth - 1)
    heigth -= 20
    for application in applications:
        if application.priority == 1:
            p.drawString(width, heigth, "Prva želja:")
        elif application.priority == 2:
            p.drawString(width, heigth, "Druga želja:")
        elif application.priority == 3:
            p.drawString(width, heigth, "Tretja želja:")
        p.drawString(width+shift, heigth, application.study_program.name)
        heigth -= 20
        p.drawString(width, heigth, "Vrsta študija:")
        if application.irregular:
            p.drawString(width+shift, heigth, "Izredni")
        else:
            p.drawString(width+shift, heigth, "Redni")
        heigth -= 20
        p.drawString(width,heigth, "Število točk: ")
        if application.points:
            p.drawString(width+shift, heigth, str(application.points) + ' točk')
        else:
            p.setFillColorRGB(255,0,0)
            p.drawString(width+shift, heigth, "Ne ustreza pogojem.")
            p.setFillColorRGB(0,0,0)
        heigth -= 30

    p.line(30, 50, max_width - 30, 50)

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def add_matura_info(request, student_id):
    student = Student.objects.get(pk=student_id)
    matura = None
    courses = None
    is_general_matura = True
    type_matura = None
    try:
        matura = ResultsMatura.objects.get(student=student)
        is_general_matura = matura.student_type is not None
        if is_general_matura:
            type_matura = matura.student_type
        else:
            type_matura = matura.student_type_profession
        courses = ResultsCourse.objects.filter(matura=matura)
    except ObjectDoesNotExist:
        pass
    length = 1
    has_courses = False
    if matura is not None and courses is not None and len(courses) > 0:
        length = len(courses)
        has_courses = True
    ResultsCourseFormSet = formset_factory(ResultsCourseForm, extra=length)
    if request.method == "GET":
        results_matura_form = ResultsMaturaForm(prefix="results-matura-form", instance=matura, is_general=is_general_matura, type=type_matura)
        #TODO: GENERAL, TYPE
        course_form_set = ResultsCourseFormSet()
        if matura is not None and courses is not None:
            courses_fields = [ob.as_json() for ob in courses]
            for subform, data in zip(course_form_set.forms, courses_fields):
                subform.initial = data
        return render(request, 'applications/add_matura_info.html',
                      {"student": student, "results_matura_form": results_matura_form, "course_form_set":course_form_set, "has_courses": has_courses})
    else:
        results_matura_form = ResultsMaturaForm(request.POST, prefix="results-matura-form", instance=matura)
        course_form_set = ResultsCourseFormSet(request.POST)
        if results_matura_form.is_valid():
            matura = results_matura_form.save(commit=False)
            matura.general_success = (matura.general_success_3 + matura.general_success_4)/2.0
            matura.student = student
            matura.save()

            ResultsCourse.objects.filter(matura=matura).delete()
            for course_form in course_form_set:
                if course_form.is_valid():
                    course = course_form.save(commit=False)
                    course.matura = matura
                    course.success_course_3_4 = (course.success_course_3 + course.success_course_4)/2.0
                    course.save()
                else:
                    print("INVALID")
            return redirect('/application/'+str(student.pk)+"/details")
        else:
            print("INVALID MATURA")
            return render(request, 'applications/add_matura_info.html',
                          {"student": student, "results_matura_form": results_matura_form, "course_form_set":course_form_set})