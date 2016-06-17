from django.conf.urls import url

from . import views

app_name = 'study_programs'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add$', views.add, name='add'),
    url(r'^edit/(?P<studyprogram_id>[0-9]+)$', views.add, name='edit'),
    url(r'^study_programs$', views.study_programs, name='study_programs'),
    url(r'^study_program/(?P<study_program_id>[0-9]+)$', views.study_program, name='study_program'),
    url(r'^study_programPDF$', views.study_programs_PDF, name='study_programs_PDF'),
    url(r'^(?P<studyprogram_id>[0-9]+)/requirements$', views.requirements, name='requirements'),
    url(r'^(?P<studyprogram_id>[0-9]+)/requirements/add$', views.add_requirements, name='add_requirements'),
    url(r'^(?P<studyprogram_id>[0-9]+)/requirements/edit', views.edit_requirements, name='edit_requirements'),
    url(r'^(?P<studyprogram_id>[0-9]+)/requirementsPDF$', views.requirementsPDF, name='requirementsPDF'),
]
