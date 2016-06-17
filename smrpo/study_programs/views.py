import json
from io import BytesIO

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from study_programs.forms import StudyProgramForm, SlotsForm
from .models import StudyProgram, GeneralMatura, ProfessionMatura
from .forms import RequirementsTypeForm, Requirement00Form, RequirementP1P3Form

SAVE_SUCCESS_MSSG = 'Shranjevanje uspešno.'


def index(request):
    return render(request, 'study_programs/index.html', {})


def add(request, studyprogram_id=None):
    if studyprogram_id is not None:
        study_program = get_object_or_404(StudyProgram, pk=studyprogram_id)
        regular_slots = study_program.regular_slots
        irregular_slots = study_program.irregular_slots
    else:
        study_program = None
        regular_slots = None
        irregular_slots = None
    if request.method == "GET":
        form = StudyProgramForm(prefix="form", instance=study_program)
        regular_slots_form = SlotsForm(prefix='regular_slots_form', instance=regular_slots)
        irregular_slots_form = SlotsForm(prefix='irregular_slots_form', instance=irregular_slots)
        return render(request, 'study_programs/add.html', {"form": form, "regular_slots_form": regular_slots_form, "irregular_slots_form": irregular_slots_form})
    elif request.method == "POST":
        form = StudyProgramForm(request.POST, prefix="form", instance=study_program)
        regular_slots_form = SlotsForm(request.POST, prefix='regular_slots_form', instance=regular_slots)
        irregular_slots_form = SlotsForm(request.POST, prefix='irregular_slots_form', instance=irregular_slots)
        if regular_slots_form.is_valid() and irregular_slots_form.is_valid() and form.is_valid():
            regular_slots = regular_slots_form.save(commit=False)
            irregular_slots = irregular_slots_form.save(commit=False)
            study_program = form.save(commit=False)
            regular_slots.save()
            study_program.regular_slots = regular_slots
            irregular_slots.save()
            study_program.irregular_slots = irregular_slots
            study_program.save()
    return render(request, 'study_programs/index.html', {})


def study_programs(request):
    if request.method == "GET":
        filter_dict = {}
        for k, v in dict(request.GET).items():
            #TODO: int fields, boolean fields
            filter_dict.update({k+"__icontains": v[0]})
        objects = []
        if len(filter_dict) > 0:
            objects = StudyProgram.objects.filter(**filter_dict).order_by("name")
        else:
            objects = StudyProgram.objects.all().order_by("name")

        results = [ob.as_json() for ob in objects]
        return HttpResponse(json.dumps(results), content_type="application/json")


def study_program(request, study_program_id):
    if request.method == "GET":
        study_program = StudyProgram.objects.get(id=study_program_id)
        return HttpResponse(json.dumps(study_program.as_json()), content_type="application/json")


def requirements(request, studyprogram_id):
    s_program = get_object_or_404(StudyProgram, id=studyprogram_id)
    if not s_program.has_requirements():
        return HttpResponseRedirect(reverse('study_programs:add_requirements', args=(studyprogram_id,)))

    newCourses = ""
    counter = 0
    courses=s_program.profession_matura.matura_courses.all()
    if courses is not None:
        for c in courses:
            if c.name[0:c.name.find('(')-1] in newCourses:
                counter += 1
                continue
            elif counter == len(courses) - 1:
                newCourses += c.name[0:c.name.find('(')-1] + '. '
            else:
                newCourses += c.name[0:c.name.find('(')-1] + ', '
            counter += 1

    priority_course = ""
    p = s_program.priority_course
    if p is not None:
        priority_course = p.name[0:p.name.find('(')-1].lower()

    profession = ""
    if s_program.profession_matura.profession is not None:
        s_program.profession_matura.profession.name.lower(),

    context = {
        'study_program': s_program,
        'courses': newCourses.lower(),
        'profession': profession,
        'priority_course': priority_course,
    }

    return render(request, 'study_programs/requirements.html', context)


def add_requirements(request, studyprogram_id):
    context = {}
    s_program = get_object_or_404(StudyProgram, id=studyprogram_id)

    if request.method == 'POST':
        type_form = RequirementsTypeForm(request.POST, prefix='type')

        r_00_form = Requirement00Form(request.POST, prefix='r_00')
        r_p1_p3_form = RequirementP1P3Form(request.POST, prefix='r_P1_P3')

        if type_form.is_valid():
            type_ = type_form.cleaned_data['type'].code

            if type_ == '00':
                form = Requirement00Form(request.POST, prefix='r_00')
                if form.is_valid():
                    _save_requirement_00(s_program, type_form, form)
                    messages.success(request, SAVE_SUCCESS_MSSG)
                    return HttpResponseRedirect(
                        reverse('study_programs:requirements',
                                args=(studyprogram_id,)))
            elif type_ == 'P1' or type_ == 'P3':
                form = RequirementP1P3Form(request.POST, prefix='r_P1_P3')
                if form.is_valid():
                    if type_ == 'P1':
                        _save_requirement_p1p3(s_program, type_form, form)
                    elif type_ == 'P3':
                        s_program = _save_requirement_p1p3(s_program,
                                                           type_form, form)
                        s_program.profession_matura.profession = \
                            form.cleaned_data['profession']
                        s_program.profession_matura.save()
                        s_program.save()
                    return HttpResponseRedirect(
                        reverse('study_programs:requirements',
                                args=(studyprogram_id,)))
                else:
                    context['show_priority_course'] = form.cleaned_data[
                        'has_priority_course']
            context['type_'] = type_
    else:
        type_form = RequirementsTypeForm(prefix='type')
        r_00_form = Requirement00Form(prefix='r_00')
        r_p1_p3_form = RequirementP1P3Form(prefix='r_P1_P3')

    context['study_program'] = s_program
    context['type_form'] = type_form
    context['r_00_form'] = r_00_form
    context['r_p1_p3_form'] = r_p1_p3_form

    return render(request, 'study_programs/add_edit_requirements.html',
                  context)


def edit_requirements(request, studyprogram_id):
    context = {}
    s_program = get_object_or_404(StudyProgram, id=studyprogram_id)
    type_ = s_program.type_requirements.code
    context['type_'] = type_

    if request.method == 'POST':
        type_form = RequirementsTypeForm(request.POST, prefix='type')

        r_00_form = Requirement00Form(request.POST, prefix='r_00')
        r_p1_p3_form = RequirementP1P3Form(request.POST, prefix='r_P1_P3')

        if type_form.is_valid():
            type_ = type_form.cleaned_data['type'].code

            if type_ == '00':
                form = Requirement00Form(request.POST, prefix='r_00')
                if form.is_valid():
                    _save_requirement_00(s_program, type_form, form)
                    messages.success(request, SAVE_SUCCESS_MSSG)
                    return HttpResponseRedirect(reverse('study_programs:requirements', args=(studyprogram_id,)))
            elif type_ == 'P1' or type_ == 'P3':
                form = RequirementP1P3Form(request.POST, prefix='r_P1_P3')
                if form.is_valid():
                    if type_ == 'P1':
                        _save_requirement_p1p3(s_program, type_form, form)
                    elif type_ == 'P3':
                        _save_requirement_p1p3(s_program, type_form, form, profession=form.cleaned_data['profession'])
                    return HttpResponseRedirect(
                        reverse('study_programs:requirements',
                                args=(studyprogram_id,)))
                else:
                    context['show_priority_course'] = form.cleaned_data['has_priority_course']
            context['type_'] = type_
    else:
        type_form = RequirementsTypeForm(prefix='type', initial={'type': s_program.type_requirements})
        if type_ == '00':
            r_00_form = Requirement00Form(prefix='r_00', initial={'w_matura': s_program.general_matura.w_matura, 'w_general': s_program.general_matura.w_general_success})
            r_p1_p3_form = RequirementP1P3Form(prefix='r_P1_P3')
        elif type_ == 'P1' or type_ == 'P3':
            r_00_form = Requirement00Form(prefix='r_00')
            context['show_priority_course'] = s_program.has_priority_course()
            initial = {
                'w_gen_matura': s_program.general_matura.w_matura,
                'w_gen_general': s_program.general_matura.w_general_success,
                'w_pro_matura': s_program.profession_matura.w_matura,
                'w_pro_general': s_program.profession_matura.w_general_success,
                'has_priority_course': s_program.has_priority_course()
            }
            if s_program.has_priority_course():
                initial['priority_course'] = s_program.priority_course
                initial['w_gen_priority_course_matura'] = s_program.general_matura.w_priority_course_matura
                initial['w_gen_priority_course_general'] = s_program.general_matura.w_priority_course_3_4
                initial['w_pro_priority_course_matura'] = s_program.profession_matura.w_priority_course_matura
                initial['w_pro_priority_course_general'] = s_program.profession_matura.w_priority_course_3_4
            else:
                initial['matura_courses'] = [x for x in s_program.profession_matura.matura_courses.all()]
                initial['w_matura_course'] = s_program.profession_matura.w_matura_course
            if type_ == 'P3':
                initial['profession'] = s_program.profession_matura.profession

            r_p1_p3_form = RequirementP1P3Form(prefix='r_P1_P3', initial=initial)

    context['study_program'] = s_program
    context['type_form'] = type_form
    context['r_00_form'] = r_00_form
    context['r_p1_p3_form'] = r_p1_p3_form

    return render(request, 'study_programs/add_edit_requirements.html', context)


def _save_requirement_00(s_program, type_form, form):
    w_matura = form.cleaned_data['w_matura']
    w_general = form.cleaned_data['w_general']
    type_ = type_form.cleaned_data['type']

    gen_matura = GeneralMatura(w_matura=w_matura, w_general_success=w_general)
    pro_matura = ProfessionMatura(w_matura=w_matura, w_general_success=w_general)
    gen_matura.save()
    pro_matura.save()

    s_program.general_matura = gen_matura
    s_program.profession_matura = pro_matura
    s_program.type_requirements = type_
    s_program.save()


def _save_requirement_p1p3(s_program, type_form, form, profession=None):
    w_gen_matura = form.cleaned_data['w_gen_matura']
    w_gen_general = form.cleaned_data['w_gen_general']
    w_pro_matura = form.cleaned_data['w_pro_matura']
    w_pro_general = form.cleaned_data['w_pro_general']
    type_ = type_form.cleaned_data['type']
    has_priority_course = form.cleaned_data['has_priority_course']

    if has_priority_course:
        w_gen_priority_course_matura = form.cleaned_data['w_gen_priority_course_matura']
        w_gen_priority_course_general = form.cleaned_data['w_gen_priority_course_general']
        w_pro_priority_course_matura = form.cleaned_data[
            'w_pro_priority_course_matura']
        w_pro_priority_course_general = form.cleaned_data[
            'w_pro_priority_course_general']
        gen_matura = GeneralMatura(w_matura=w_gen_matura,
                                   w_general_success=w_gen_general, w_priority_course_3_4=w_gen_priority_course_general, w_priority_course_matura=w_gen_priority_course_matura)
        pro_matura = ProfessionMatura(w_matura=w_pro_matura,
                                      w_general_success=w_pro_general, w_priority_course_3_4=w_pro_priority_course_general, w_priority_course_matura=w_pro_priority_course_matura)
        s_program.priority_course = form.cleaned_data['priority_course']
    else:
        matura_courses = form.cleaned_data['matura_courses']
        w_matura_course = form.cleaned_data['w_matura_course']
        gen_matura = GeneralMatura(w_matura=w_gen_matura,
                                   w_general_success=w_gen_general)
        pro_matura = ProfessionMatura(w_matura=w_pro_matura,
                                      w_general_success=w_pro_general, w_matura_course=w_matura_course)
        pro_matura.save()
        for mc in matura_courses:
            pro_matura.matura_courses.add(mc)

    gen_matura.save()
    if profession is not None:
        pro_matura.profession = profession
    pro_matura.save()
    s_program.general_matura = gen_matura
    s_program.profession_matura = pro_matura
    s_program.type_requirements = type_
    s_program.save()
    return s_program



def study_programs_PDF(request):
    study_programs = StudyProgram.objects.all()

    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="seznam_studijskih_programov.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)
    max_width = 595
    max_heigth = 842
    width = 50
    heigth = 750

    p.setFont('VeraBd', 20)
    p.drawCentredString(max_width/2.0, heigth, "Seznam študijskih programov")
    p.setFont('Vera', 14)
    heigth -= 40
    p.drawString(width + 30, heigth, "Ime študijskega programa")
    p.drawString(width + 330, heigth, "Šifra")
    p.drawString(width + 430, heigth, "Fakulteta")
    heigth -= 20
    p.line(30,heigth, max_width-30, heigth)
    heigth -= 40
    p.setFont('Vera', 10)

    counter = 1
    for program in study_programs:
        if heigth < 120:
            p.line(50, 100, max_width-50, 100)
            p.showPage()
            p.setFont('Vera', 14)
            heigth = 750
            p.drawString(width + 30, heigth, "Ime študijskega programa")
            p.drawString(width + 330, heigth, "Šifra")
            p.drawString(width + 430, heigth, "Fakulteta")
            heigth -= 20
            p.line(30,heigth, max_width-30, heigth)
            heigth -= 40
            p.setFont('Vera', 10)

        p.drawString(width-10, heigth, str(counter)+'.')
        p.drawString(width + 30, heigth, program.name)
        p.drawString(width + 330, heigth, program.code)
        p.drawString(width + 430, heigth, program.faculty.code)
        heigth -=20
        counter +=1

    p.line(50, 100, max_width-50, 100)
    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response



def requirementsPDF(request,studyprogram_id):
    study_program = StudyProgram.objects.get(pk=studyprogram_id)
    stringCourses = ""
    counter = 0
    courses=study_program.profession_matura.matura_courses.all()
    for c in courses:
        if c.name[0:c.name.find('(')-1] in stringCourses:
            counter += 1
            continue
        elif counter == len(courses) - 1:
            stringCourses += c.name[0:c.name.find('(')-1] + '. '
        else:
            stringCourses += c.name[0:c.name.find('(')-1] + ', '
        counter += 1

    stringCourses = stringCourses.lower()

    p = study_program.priority_course
    if p is not None:
        priority_course = p.name[0:p.name.find('(')-1].lower()

    profession = ""
    if study_program.profession_matura.profession is not None:
        study_program.profession_matura.profession.name.lower(),


    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+ study_program.name +'.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer)

    width = 40
    height = 750
    shift = 15
    max_width = 595

    p.setFont('VeraBd', 20)
    p.drawCentredString(max_width/2.0,height,study_program.name)
    height-= 40
    p.setFont('VeraBd', 14)
    p.drawString(width,height, "Podatki o programu:")
    height -= 10
    p.line(30,height, max_width-30, height)
    height -= 20
    p.setFont('Vera', 12)
    p.drawString(width,height,"UNIVERZA: " + study_program.faculty.university.name)
    height -= 20
    p.drawString(width,height, "VISOKOŠOLSKI ZAVOD: " + study_program.faculty.name)
    height -= 20
    p.drawString(width, height, "ŠTUDIJSKI PROGRAM: " + study_program.name)
    height -= 20
    p.drawString(width, height, "ŠIFRA PROGRAMA: " + study_program.code)
    height -= 20
    p.drawString(width, height, "TIP VPISNEGA POGOJA: " + study_program.type_requirements.code + ' - ' + study_program.type_requirements.name)
    height -= 40


    p.setFont('VeraBd', 14)
    p.drawString(width,height, "Vpisni pogoji:")
    height -= 10
    p.line(30,height, max_width-30, height)
    height -= 20
    p.setFont('Vera', 12)
    if study_program.type_requirements.code == 'P1':
        p.drawString(width+shift, height, "a) Kdor je opravil splosno maturo." )
        height -= 20
        p.drawString(width+shift, height, "b) Kdor je opravil poklicno maturo v kateremkoli srednješolskem programu")
        height -= 15
        p.drawString(width+shift+15, height, "in izpit iz enega od maturitetnih predmetov: " + stringCourses)
        height -= 15
        p.drawString(width+shift+15, height, "Izbrani predmet ne se sme biti predmet, ki ga je kandidat že opravil pri poklicni")
        height -= 15
        p.drawString(width+shift+15, height, "maturi.")

    elif study_program.type_requirements.code == '00':
        p.drawString(width, height, "Vpiše se lahko, kdor je opravil zaključni izpit v kateremkoli štiriletnem srednješolskem")
        height -= 15
        p.drawString(width, height, "programu, poklicno maturo ali splošno maturo.")
    elif study_program.type_requirements.code == 'P2':
        p.drawString(width+shift, height, "a) Kdor je opravil splošno maturo.")
        height -= 20
        p.drawString(width+shift, height, "b) Kdor je opravil poklico maturo v kateremkoli srednješolskem programu")
        height -= 15
        if stringCourses != "":
            p.drawString(width+shift+15, height, "in izpit iz maturitetnega predemta: " + stringCourses)
        else:
            p.drawString(width+shift+15, height, "in izpit iz poljubenga maturitetnega predemta.")
        height -= 15
        p.drawString(width+shift+15, height, "Če je kandidat ta predmet opravil že pri poklicni maturi pa izpit")
        height -= 15
        p.drawString(width+shift+15, height, "iz kateregakoli maturitetnega predmeta. Izbrani predmet ne sme biti predmet,")
        height -= 15
        p.drawString(width+shift+15, height, "ki ga je kandidat že opravil pri poklicni maturi.")

    elif study_program.type_requirements.code == 'P3':
        p.drawString(width+shift, height, "a) Kdor je opravil splošno maturo.")
        height -= 20
        p.drawString(width+shift, height, "b) Kdor je opravil poklico maturo v kateremkoli srednješolskem programu")
        height -= 15
        p.drawString(width+shift+15, height, study_program.profession_matura.profession.name.lower() + " in izpit iz maturitetnega predmeta " + stringCourses)
        height -= 15
        p.drawString(width+shift+15, height, "Ce je kandidat navedeni predmet že opravil pri poklicni maturi, pa izpit iz")
        height -= 15
        p.drawString(width+shift+15, height, "kateregakoli maturitetnega predmeta. Izbrani predmet ne sme biti")
        height -= 15
        p.drawString(width+shift+15, height, "predmet, ki ga je kandidat že opravil pri poklicni maturi.")

    height -= 40
    p.setFont('VeraBd', 16)
    p.drawString(width, height, "Splošna matura:")
    height -= 10
    p.line(30,height, max_width-30, height)
    p.setFont('Vera', 12)
    height -= 20
    p.drawString(width+shift, height, "- Uspeh na maturi: " + str(study_program.general_matura.w_matura * 100) + "%")
    height -= 20
    p.drawString(width+shift, height, "- Splošni uspeh v 3. in 4. letniku: " + str(study_program.general_matura.w_general_success * 100) + "%")
    if study_program.general_matura.w_priority_course_3_4 is not None and study_program.general_matura.w_priority_course_3_4 > 0:
        height -= 20
        p.drawString(width+shift, height, "- Splošni uspeh v 3. in 4. letniku pri predmetu " + priority_course + ": " + str(study_program.general_matura.w_priority_course_3_4 * 100) + "%")
        # height -= 20
        # p.drawString(width+shift, height, "- Splošni uspeh v 4. letniku pri predmetu " + study_program.priority_course.name + ": " + str(study_program.general_matura.success_course_4_grade) + "%")
    if study_program.general_matura.w_priority_course_matura is not  None and study_program.general_matura.w_priority_course_matura > 0:
        height -= 20
        p.drawString(width+shift, height, "- Splošni uspeh na maturi iz predmeta " + priority_course + ": " + str(study_program.general_matura.w_priority_course_matura * 100) + "%")

    height -= 40
    p.setFont('VeraBd', 14)
    p.drawString(width, height, "Poklicna matura:")
    height -= 10
    p.line(30,height, max_width-30, height)
    p.setFont('Vera', 12)
    height -= 20
    p.drawString(width+shift, height, "- Uspeh na maturi: " + str(study_program.profession_matura.w_matura*100) + "%")
    height -= 20
    p.drawString(width+shift, height, "- Splošni uspeh v 3. in 4. letniku: " + str(study_program.profession_matura.w_general_success * 100) + "%")
    if study_program.profession_matura.w_matura_course is not None and study_program.profession_matura.w_matura_course > 0:
        height -= 20
        p.drawString(width+shift,height, "- Maturitetni predmet: " + str(study_program.profession_matura.w_general_success * 100) + "%")
    if study_program.profession_matura.w_priority_course_3_4 is not None and study_program.profession_matura.w_priority_course_3_4 > 0:
        height -= 20
        p.drawString(width+shift, height, "- Splošni uspeh v 3. letniku pri predmetu " + priority_course + ": " + str(study_program.profession_matura.w_priority_course_3_4 * 100) + "%")
        # height -= 20
        # p.drawString(width+shift, height, "- Splošni uspeh v 4. letniku pri predmetu " + study_program.priority_course.name + ": " + str(study_program.profession_matura.success_course_4_grade) + "%")
    if study_program.profession_matura.w_priority_course_matura is not None and study_program.profession_matura.w_priority_course_matura > 0:
        height -= 20
        p.drawString(width+shift, height, "- Splošni uspeh na maturi iz predmeta " + priority_course + ": " + str(study_program.profession_matura.w_priority_course_matura * 100) + "%")

    height -= 40

    if height < 200:
        p.line(30, 50, max_width - 30, 50)
        p.showPage()
        height = 750


    p.setFont('VeraBd', 14)
    p.drawString(width, height, "Vpisna mesta:")
    height -= 10
    p.line(30,height, max_width-30, height)
    p.setFont('Vera', 12)
    height -= 20
    p.drawString(width, height, "Državljani Slovenije in Evropske unije:")
    height -= 20
    if study_program.regular_slots is None and study_program.irregular_slots is None:
        p.drawString(width+shift, height, "Ni razpisanih vpisnih mest.")
    elif study_program.regular_slots.enrolment_slots_EU == 0 and study_program.irregular_slots.enrolment_slots_EU == 0:
        p.drawString(width+shift, height, "Ni razpisanih vpisnih mest.")
    else:
        if study_program.regular_slots.enrolment_slots_EU > 0:
            p.drawString(width+shift, height, "- Redni študij: " + str(study_program.regular_slots.enrolment_slots_EU) + " mest.")
        else:
            p.drawString(width+shift, height, "- Redni študij: ni razpisanih vpisnih mest.")
        height -= 20
        if study_program.irregular_slots.enrolment_slots_EU > 0:
            p.drawString(width+shift, height, "- Izredni študij: " + str(study_program.irregular_slots.enrolment_slots_EU) + " mest.")
        else:
            p.drawString(width+shift, height, "- Izredni študij: ni razpisanih vpisnih mest.")
    height -= 20

    p.drawString(width, height, "Slovenci brez slovenskega državljanstva in ostali:")
    height -= 20
    if study_program.regular_slots is None and study_program.irregular_slots is None:
        p.drawString(width+shift, height, "Ni razpisanih vpisnih mest.")
    elif study_program.regular_slots.enrolment_slots_other == 0 and study_program.regular_slots.enrolment_slots_other == 0:
        p.drawString(width+shift, height, "Ni razpisanih vpisnih mest.")
    else:
        if study_program.regular_slots.enrolment_slots_other > 0:
            p.drawString(width+shift, height, "- Redni študij: " + str(study_program.regular_slots.enrolment_slots_other) + " mest.")
        else:
            p.drawString(width+shift, height, "- Redni študij: ni razpisanih vpisnih mest.")
        height -= 20
        if study_program.irregular_slots.enrolment_slots_other > 0:
            p.drawString(width+shift, height, "- Izredni študij: " + str(study_program.irregular_slots.enrolment_slots_other) + " mest.")
        else:
            p.drawString(width+shift, height, "- Izredni študij: ni razpisanih pisnih mest.")
    p.line(30, 50, max_width - 30, 50)

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

