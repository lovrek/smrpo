from django.conf.urls import url

from . import views

app_name = 'informations'

urlpatterns = [
    url(r'^(?P<entity_type>\w{0,50})/$', views.index, name='sifrant'),
    url(r'^entity/(?P<entity_type>\w{0,50})$', views.entity),
    url(r'^entity/(?P<entity_type>\w{0,50})/(?P<entity_id>\d+)$', views.delete),
    url(r'^entity/(?P<entity_type>\w{0,50})/import$', views.import_entity),
    url(r'^get_regions_by_country/(?P<country_id>\w{0,50})$', views.get_regions_by_country),
    url(r'^get_posts_by_region/(?P<region_id>\w{0,50})$', views.get_posts_by_region),
    url(r'^uploadFile$', views.upload_file, name='uploadFile')
]