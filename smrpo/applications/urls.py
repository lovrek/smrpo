from django.conf.urls import url

from . import views

app_name = 'applications'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add$', views.add, name='add'),
    url(r'^add/(?P<student_id>[0-9]+)$', views.add, name='edit'),
    url(r'^delete$', views.delete, name='delete'),
    url(r'^delete/(?P<student_id>[0-9]+)$', views.delete, name='delete_student_application'),
    url(r'^send$', views.send, name='send'),
    url(r'^students$', views.students, name='students'),
    url(r'^(?P<student_id>[0-9]+)/PDF$', views.download_PDF, name='application_PDF'),
    url(r'^display_PDF$', views.display_PDF, name='display_PDF'),
    url(r'^list_of_candidates_PDF$', views.list_of_candidates_PDF, name='list_of_candidates_PDF'),
    url(r'^(?P<user_id>[0-9]+)/compute_points$', views.compute_points, name='compute_points'),
    url(r'^(?P<student_id>[0-9]+)/details$', views.details, name='details'),
    url(r'^(?P<student_id>[0-9]+)/add_matura_info', views.add_matura_info, name='add_matura_info'),
    url(r'^(?P<student_id>[0-9]+)/detailsPDF$', views.detailsPDF, name='detailsPDF'),
]