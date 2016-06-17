import csv
import sys
import os
import shutil
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse, Http404
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.conf import settings

#IMPORT ALL MODELS THAT INHERIT InformationBaseClass
from django.utils.translation import ugettext

from applications.models import *
from faculties.models import *
from information.models import *
from login.models import *
from officials.models import *
from students.models import *
from study_programs.models import *

from .forms import UploadFileForm
from .models import Document


def index(request, entity_type):
    class_object = str_to_class(entity_type)
    fields = class_object.get_fields()
    has_foreign_key_fields = class_object.has_foreign_key_fields()
    return render(request, 'information/index.html',
                  {"entity_type": entity_type, "fields": fields, "has_foreign_key_fields": has_foreign_key_fields})


def entity(request, entity_type):
    class_object = str_to_class(entity_type)
    if request.method == "GET":
        query = request.GET.get("q", None)
        objects = []
        if query:
            filter_dict = {'name__icontains': query, "deleted": False}
            objects = class_object.objects.filter(**filter_dict)
        else:
            objects = class_object.objects.all()
        results = [ob.as_json() for ob in objects]
        return HttpResponse(json.dumps(results), content_type="application/json")
    elif request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        try:
            with transaction.atomic():
                object = class_object.json_to_object(data)
                object.clean()
                object.save()
        except IntegrityError as e:
            return HttpResponse(json.dumps({"success": False, "errors": get_validation_errors(e)}), content_type="application/json")
        return HttpResponse(json.dumps({"success": True, "entity": object.as_json()}), content_type="application/json")
    else:
        raise Http404()


def delete(request, entity_type, entity_id):
    if request.method == "DELETE":
        class_object = str_to_class(entity_type)
        object = class_object.objects.get(pk=entity_id)
        object.deleted = True
        object.save()
        return HttpResponse(status=204)
    else:
        raise Http404()


def str_to_class(str):
    try:
        return getattr(sys.modules[__name__], str)
    except AttributeError:
        raise Http404(str + " does not exist!")


def get_validation_errors(e):
    if e.args[0] == 1062:
        print(e.args[1])
        splitted_string = e.args[1].split("for key")[1].split("_")
        if(len(splitted_string) > 2):
            field_name = '_'.join(str(x) for x in splitted_string[2:-2])
        else:
            field_name = e.args[1].split("for key")[1].strip()[1:-1]
        return json.dumps([{"field": field_name, "message": "Zapis že obstaja!"}])
    elif e.args[0] == 1048:
        field_name = e.args[1].split("'")[1].split("_")[0]
        return json.dumps([{"field": field_name, "message": "To polje je obvezno!"}])
    return json.dumps(e.args[0])


def get_regions_by_country(request, country_id):
    if request.method == "GET":
        regions = Region.objects.filter(country_id=country_id)
        results = [ob.as_json() for ob in regions]
        return HttpResponse(json.dumps(results), content_type="application/json")


def get_posts_by_region(request, region_id):
    if request.method == "GET":
        posts = Post.objects.filter(region_id=region_id)
        results = [ob.as_json() for ob in posts]
        return HttpResponse(json.dumps(results), content_type="application/json")


def study_program(request, study_program_id):
    if request.method == "GET":
        study_program = StudyProgram.objects.get(id=study_program_id)
        return HttpResponse(json.dumps(study_program.as_json()), content_type="application/json")


# TODO: REMOVE
def import_entity(request, entity_type):
    import_from_csv(entity_type, "/vagrant/smrpo/information/" + entity_type + ".csv")
    return HttpResponse(200)


def import_from_csv(entity_type, path):
    data_reader = csv.reader(open(path), delimiter=',', quotechar='"')
    class_object = str_to_class(entity_type)
    class_object.objects.all().delete()
    for row in data_reader:
        if entity_type == "Country":
            country = Country(name=row[0], eu=row[1] == "D")
            country.save()
        elif entity_type == "Region":
            region = Region(name=row[1], country_id=207)
            region.save()

def import_from_text(file1,file2):
    filename1 = file1.split('/')[2]
    filename2 = file2.split('/')[2]
    #parsing data
    with open(settings.MEDIA_ROOT + '/' + file1,  encoding = 'cp1250') as fp:
        data1 = [line.replace('\n','').replace(' ','').replace('\t','').split('Q') for line in fp]

    with open(settings.MEDIA_ROOT + '/' + file2, encoding = 'cp1250') as fp:
        data2 = [line.replace('\n','').replace(' ','').replace('\t','').split('Q') for line in fp]
    #import data result on matura
    for data in data1:
        if not data[3]:
            continue
        student = Student.objects.filter(emso=data[0])
        if not student:
            user = create_user(data[1],data[2])
            student = Student(emso=data[0], male=1, user=user)
            student.save()
        student = Student.objects.get(emso=data[0])
        student.high_school=HighSchool.objects.get(sifra=data[8])
        student.profession=Profession.objects.get(sifra=data[9])
        student.save()
        passed=0
        if data[4] == "D":
            passed = 1
        if filename1 == "maturant.txt" or filename1 == "maturant1.txt":
            matura = ResultsMatura.objects.filter(student=student)
            if not matura:
                matura = ResultsMatura(student=student, matura=data[3], general_success_3=int(data[5]), general_success_4=int(data[6]), general_success=(int(data[5])+int(data[6]))/2.0, passed=passed, student_type=data[7])
            else:
                matura = ResultsMatura.objects.get(student=student)
                matura.matura=data[3]
                matura.general_success_3 = int(data[5])
                matura.general_success_4 = int(data[6])
                matura.general_success = (int(data[5])+int(data[6]))/2.0
                matura.passed = passed
                matura.student_type = data[7]
            matura.save()

        elif filename1 == "poklmat.txt" or filename1 == "poklmat1.txt":
            matura = ResultsMatura.objects.filter(student=student)
            if not matura:
                matura = ResultsMatura(student=student, matura=data[3], general_success_3=int(data[5]), general_success_4=int(data[6]) ,general_success=(int(data[5])+int(data[6]))/2.0, passed=passed, student_type_profession=data[7])
            else:
                matura = ResultsMatura.objects.get(student=student)
                matura.matura=data[3]
                matura.general_success_3 = int(data[5])
                matura.general_success_4 = int(data[6])
                matura.general_success = (int(data[5])+int(data[6]))/2.0
                matura.passed = passed
                matura.student_type_profession = data[7]
            matura.save()

    #import data  courses on matura
    for data in data2:
        if not data[3]:
            continue
        matura = ResultsMatura.objects.get(student=Student.objects.get(emso=data[0]))
        if not Course.objects.filter(sifra=data[1]):
            continue
        course = Course.objects.get(sifra=data[1])
        exists = ResultsCourse.objects.filter(matura=matura,course=course)
        passed = 0
        if data[5] == "D":
            passed = 1
        if not exists:
            if filename2 == "maturpre.txt" or filename2 == "maturpre1.txt":
                resultCourse = ResultsCourse(course=course, matura=matura, result_on_matura=data[2], success_course_3=int(data[3]), success_course_4=int(data[4]) ,success_course_3_4=(int(data[3])+int(data[4]))/2.0, passed=passed,type_course=data[6])
                resultCourse.save()
            elif filename2 == "poklpre.txt" or filename2 == "poklpre1.txt":
                resultCourse = ResultsCourse(course=course, matura=matura, result_on_matura=data[2], success_course_3=int(data[3]), success_course_4=int(data[4]), success_course_3_4=(int(data[3])+int(data[4]))/2.0, passed=passed,type_course_profession=data[6])
                resultCourse.save()
        else:
            resultCourse = ResultsCourse.objects.get(matura=matura,course=course)
            if filename2 == "maturpre.txt" or filename2 == "maturpre1.txt":
                resultCourse.result_on_matura=data[2]
                resultCourse.success_course_3=data[3]
                resultCourse.success_course_4=data[4]
                resultCourse.success_course_3_4=(int(data[3])+int(data[4]))/2.0
                resultCourse.passed=passed
                resultCourse.type_course=data[6]
                resultCourse.save()
            elif filename2 == "poklpre.txt" or filename2 == "poklpre1.txt":
                resultCourse.result_on_matura=data[2]
                resultCourse.success_course_3=data[3]
                resultCourse.success_course_4=data[4]
                resultCourse.success_course_3_4=(int(data[3])+int(data[4]))/2.0
                resultCourse.passed=passed
                resultCourse.type_course_profession=data[6]
                resultCourse.save()




def upload_file(request):
    # Handle file upload
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(file = request.FILES['file'])
            newdoc.save()
            if os.path.exists(settings.MEDIA_ROOT + '/document/maturant.txt') and os.path.exists(settings.MEDIA_ROOT + '/document/maturpre.txt'):
                import_from_text('/document/maturant.txt', '/document/maturpre.txt')
            elif os.path.exists(settings.MEDIA_ROOT + '/document/maturant1.txt') and os.path.exists(settings.MEDIA_ROOT + '/document/maturpre1.txt'):
                import_from_text('/document/maturant1.txt', '/document/maturpre1.txt')
            elif os.path.exists(settings.MEDIA_ROOT + '/document/poklmat.txt') and os.path.exists(settings.MEDIA_ROOT + '/document/poklpre.txt'):
                import_from_text('/document/poklmat.txt', '/document/poklpre.txt')
            elif os.path.exists(settings.MEDIA_ROOT + '/document/poklmat1.txt') and os.path.exists(settings.MEDIA_ROOT + '/document/poklpre1.txt'):
                import_from_text('/document/poklmat1.txt', '/document/poklpre1.txt')
            else:
                return redirect('/information/uploadFile')

            shutil.rmtree(settings.MEDIA_ROOT + '/document')
            Document.objects.all().delete()
            # newdoc.delete()
            # Redirect to the document list after POST
            return redirect('/information/uploadFile')
    else:
        form = UploadFileForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'information/upload.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )


def create_user(first_name, last_name):
    user = User.objects.create_user(first_name + last_name,"lovropodgorsek@gmail.com", "qweasd123")
    user.first_name = first_name
    user.last_name = last_name
    user.is_active = True
    user.save()
    return user